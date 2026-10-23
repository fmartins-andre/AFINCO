-- Relatório de Receitas — Escriba Document (TD / PJ / Certidões)
--
-- Retorna uma linha por lançamento, com os valores ainda sem formatação.
-- A formatação no layout do TXT é feita no rd_document.py.
--
-- Parâmetros (pymysql): %(data_ini)s, %(data_fim)s  ->  'YYYY-MM-DD'
--
-- Colunas:
--   data       DATE           data do lançamento (caixa) ou da confirmação do selo
--   hp         INT            1 = receita no caixa, 6 = devolução no caixa, 4 = emolumento selado
--   tipo       VARCHAR        TD | PJ | CT | EX | MT (tipo do processo no Escriba Document)
--   protocolo  INT            número do protocolo do processo (NULL = vínculo não encontrado)
--   valor      DECIMAL(16,2)  sempre positivo

SELECT data, hp, tipo, protocolo, valor
FROM (

    -- ---------------------------------------------------------------
    -- 1) Caixa: tudo o que entrou ou saiu no balcão (emolumentos + fundos)
    --    cx -> protocolo_gi (guia) -> titulo | pjuridica | ccertidao
    -- ---------------------------------------------------------------
    SELECT
        cx.cx_data AS data,
        IF(cx.cx_valor < 0, 6, 1) AS hp,
        pg.pg_tiposeq AS tipo,
        CAST(COALESCE(t.Protocolo, p.Protocolo, c.Protocolo) AS UNSIGNED) AS protocolo,
        CAST(ABS(cx.cx_valor) AS DECIMAL(16, 2)) AS valor
    FROM document.cx AS cx
    LEFT JOIN document.protocolo_gi AS pg ON (pg.pg_gi_id = cx.cx_gi_id)
    LEFT JOIN document.titulo AS t ON (
        pg.pg_tiposeq IN ('TD', 'EX')
        AND t.Sequencia = pg.pg_sequencia
    )
    LEFT JOIN document.pjuridica AS p ON (
        pg.pg_tiposeq = 'PJ'
        AND p.Sequencia = pg.pg_sequencia
    )
    LEFT JOIN document.ccertidao AS c ON (
        pg.pg_tiposeq = 'CT'
        AND c.NumeroCertidao = pg.pg_sequencia
    )
    WHERE cx.cx_valor != 0
        AND cx.cx_data BETWEEN %(data_ini)s AND %(data_fim)s

    UNION ALL

    -- ---------------------------------------------------------------
    -- 2) Selagem: emolumento só vira receita depois que o selo foi
    --    confirmado no eSelo. Os selos são agrupados por protocolo e por
    --    dia de confirmação.
    --    Os selos de processos cancelados (inativos) ficam de fora:
    --    tendem a ser devolvidos ou trocados depois.
    --    selogo -> eselo.selo -> selo_retorno -> retorno
    -- ---------------------------------------------------------------
    SELECT
        selos.data,
        4 AS hp,
        selos.tipo,
        selos.protocolo,
        CAST(SUM(selos.valor) AS DECIMAL(16, 2)) AS valor
    FROM (

        SELECT
            confirmados.data,
            confirmados.tipo,
            CAST(COALESCE(t.Protocolo, p.Protocolo, c.Protocolo) AS UNSIGNED) AS protocolo,
            COALESCE(t.cancelado, p.cancelado, c.Cancelado, 0) AS cancelado,
            confirmados.valor
        FROM (

            SELECT DISTINCT
                es.sel_id,
                er.ret_dataConfirmacao AS data,
                sg.sgo_tipoDoc AS tipo,
                sg.sgo_sequencia AS sequencia,
                es.sel_valor_emolumentos AS valor
            FROM eselo.retorno AS er
            INNER JOIN eselo.selo_retorno AS esr ON (er.ret_id = esr.ser_retorno)
            INNER JOIN eselo.selo AS es ON (esr.ser_selo = es.sel_id)
            INNER JOIN document.selogo AS sg ON (sg.sgo_numero = es.sel_numero)
            WHERE er.ret_dataConfirmacao BETWEEN %(data_ini)s AND %(data_fim)s
                AND er.ret_situacao = 'PROCESSADO_COM_SUCESSO'
                AND es.sel_status != 'Cancelado'
                AND es.sel_valor_emolumentos != 0

        ) AS confirmados
        LEFT JOIN document.titulo AS t ON (
            confirmados.tipo = 'TD'
            AND t.Sequencia = confirmados.sequencia
        )
        LEFT JOIN document.pjuridica AS p ON (
            confirmados.tipo = 'PJ'
            AND p.Sequencia = confirmados.sequencia
        )
        LEFT JOIN document.ccertidao AS c ON (
            confirmados.tipo = 'CT'
            AND c.NumeroCertidao = confirmados.sequencia
        )

    ) AS selos
    WHERE selos.cancelado = 0
    GROUP BY selos.data, selos.tipo, selos.protocolo

) AS lancamentos
ORDER BY data, protocolo, hp
