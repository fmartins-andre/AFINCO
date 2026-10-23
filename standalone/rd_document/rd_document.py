"""
Relatório de Receitas — Escriba Document (TD / PJ / Certidões).

Versão standalone do relatório de receitas do AFINCO
(app/relatorios/_make_rd_txt_file.py), lendo do banco `document`.
Gera um TXT no mesmo layout, só com receitas (sem despesas).

Uso:
    python rd_document.py 2026-10-01 2026-10-31 [--saida DIR]

Conexão por variáveis de ambiente: DB_HOST, DB_PORT, DB_USER, DB_PASSWORD.
"""
import argparse
import os
import sys
from collections import defaultdict
from datetime import date
from decimal import Decimal
from pathlib import Path

import pymysql

SQL_FILE = Path(__file__).with_name('rd_document.sql')

# contas contábeis (as mesmas do relatório do AFINCO)
CONTA_CAIXA = '1000001'
CONTA_SERVICO = '9010001'
CONTA_DEVOLUCAO = '9300008'
CONTA_DEPOSITO_PREVIO = '1010001'
CONTA_EMOLUMENTO = '1010002'


# prefixo do documento por tipo de processo: só identifica a origem,
# sem valor contábil. 1º dígito = natureza (9 ato, 8 certidão, 7 exame,
# 6 despesa); 2º dígito = tipo (repetido no Registro de Imóveis:
# 99 RE, 88 CE, 77 EX, 66 despesas; decrescente no Document).
PREFIXO_DOCUMENTO = {
    'TD': '98',
    'PJ': '97',
    'MT': '95',
    'LV': '94',  # reservado, sem processos ainda
    'AP': '93',  # reservado, sem processos ainda
    'IR': '92',  # reservado, sem processos ainda
    'CT': '87',
    'EX': '76',
}

# sigla no histórico, quando difere do tipo no banco
# (EX já é o exame do Registro de Imóveis no AFINCO)
SIGLA_DOCUMENTO = {
    'EX': 'ED',
}


def linha(data, conta_debito, conta_credito, tipo, protocolo, hp, valor, historico):
    """
    Monta uma linha no layout do relatório:
    DD MM DEBITO CREDITO DOCUMENTO HP VALOR HISTORICO
    """
    centavos = int((valor * 100).to_integral_value())
    campos = [
        f'{data.day:02d}',
        f'{data.month:02d}',
        conta_debito,
        conta_credito,
        f'{PREFIXO_DOCUMENTO[tipo]}{protocolo:07d}',
        f'{hp:>2}',
        f'{centavos:012d}',
        f'{historico} PROT. {SIGLA_DOCUMENTO.get(tipo, tipo)}.{protocolo}'[:32].ljust(32),
    ]
    return ' '.join(campos)


def lancamentos(row):
    """
    Converte uma linha da query nas linhas do TXT.
    Mesma regra do AFINCO: receita e devolução no caixa geram
    uma segunda linha movimentando o depósito prévio.
    """
    data, hp, tipo, protocolo, valor = row

    if hp == 1:  # receita de serviço no caixa
        yield linha(data, CONTA_CAIXA, CONTA_SERVICO, tipo, protocolo, 1, valor, 'CX SERVICO')
        yield linha(data, CONTA_DEPOSITO_PREVIO, CONTA_CAIXA, tipo, protocolo, 2, valor, 'DP SERVICO')

    elif hp == 6:  # devolução no caixa
        yield linha(data, CONTA_DEVOLUCAO, CONTA_CAIXA, tipo, protocolo, 6, valor, 'CX DEVOLUCAO')
        yield linha(data, CONTA_CAIXA, CONTA_DEPOSITO_PREVIO, tipo, protocolo, 6, valor, 'DP DEVOLUCAO')

    elif hp == 4:  # emolumento selado
        yield linha(data, CONTA_EMOLUMENTO, CONTA_DEPOSITO_PREVIO, tipo, protocolo, 4, valor, 'DP EMOLUMENTO')

    else:
        raise ValueError(f'Histórico padrão desconhecido: {hp}')


def consultar(data_ini, data_fim):
    conexao = pymysql.connect(
        host=os.environ.get('DB_HOST', '192.168.1.253'),
        port=int(os.environ.get('DB_PORT', 3306)),
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASSWORD'],
        charset='utf8mb4',
        connect_timeout=10,
    )
    try:
        with conexao.cursor() as cursor:
            cursor.execute(
                SQL_FILE.read_text(encoding='utf-8'),
                {'data_ini': data_ini.isoformat(), 'data_fim': data_fim.isoformat()},
            )
            return cursor.fetchall()
    finally:
        conexao.close()


def main():
    parser = argparse.ArgumentParser(description='Relatório de Receitas — Escriba Document')
    parser.add_argument('data_ini', type=date.fromisoformat, help='AAAA-MM-DD')
    parser.add_argument('data_fim', type=date.fromisoformat, help='AAAA-MM-DD')
    parser.add_argument('--saida', type=Path, default=Path('saida'), help='diretório do TXT (padrão: ./saida)')
    args = parser.parse_args()

    if args.data_fim < args.data_ini:
        sys.exit('Erro: data final anterior à data inicial.')

    rows = consultar(args.data_ini, args.data_fim)

    invalidos = [r for r in rows if r[3] is None or r[2] not in PREFIXO_DOCUMENTO]
    if invalidos:
        for r in invalidos:
            print(f'  inválido: data={r[0]} hp={r[1]} tipo={r[2]} protocolo={r[3]} valor={r[4]}', file=sys.stderr)
        sys.exit(
            f'Erro: {len(invalidos)} lançamento(s) sem processo vinculado ou com tipo desconhecido. '
            'Relatório não gerado.'
        )

    if not rows:
        sys.exit('Não foram encontrados dados para a solicitação.')

    args.saida.mkdir(parents=True, exist_ok=True)
    arquivo = args.saida / f'RecDoc_{args.data_ini}.{args.data_fim}.txt'

    resumo = defaultdict(lambda: [0, Decimal('0')])
    qtd_linhas = 0
    with open(arquivo, 'w', encoding='ascii', newline='') as f:
        for row in rows:
            resumo[row[1]][0] += 1
            resumo[row[1]][1] += row[4]
            for texto in lancamentos(row):
                f.write(texto + '\r\n')
                qtd_linhas += 1

    nomes = {1: 'receitas caixa', 6: 'devoluções caixa', 4: 'emolumentos selados'}
    print(f'Arquivo: {arquivo}')
    print(f'Linhas no TXT: {qtd_linhas}')
    for hp in (1, 6, 4):
        if hp in resumo:
            qtd, total = resumo[hp]
            print(f'  HP {hp} ({nomes[hp]}): {qtd} lançamento(s), R$ {total:,.2f}')


if __name__ == '__main__':
    main()
