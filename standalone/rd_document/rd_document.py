"""
Relatório de Receitas — Escriba Document (TD / PJ / Certidões).

Versão standalone do relatório de receitas do AFINCO
(app/relatorios/_make_rd_txt_file.py), lendo do banco `document`.
Gera um TXT no mesmo layout, só com receitas (sem despesas).

Toda a configuração (banco, contas, prefixos, pasta de saída) vem do
config.ini; só o SQL fica embutido no programa.
"""
import configparser
import logging
import platform
import re
import sys
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path

import pymysql

log = logging.getLogger('rd_document')

CONFIG_NOME = 'config.ini'

# chaves obrigatórias na seção [contas]
CONTAS = ('caixa', 'servico', 'devolucao', 'deposito_previo', 'emolumento')

NOMES_HP = {1: 'receitas caixa', 6: 'devoluções caixa', 4: 'emolumentos selados'}

# segundos
TEMPO_CONEXAO = 10    # para o servidor aceitar a conexão
LIMITE_CONSULTA = 90  # duração máxima de cada consulta (interrompida no servidor)
FOLGA_CLIENTE = 15    # o cliente desiste um pouco depois, caso o servidor não interrompa

# códigos de erro do MySQL
ER_QUERY_TIMEOUT = 3024  # max_execution_time estourado
CR_SERVER_LOST = 2013    # conexão perdida durante a consulta (inclui timeout do cliente)


class ErroRelatorio(Exception):
    """Erro com mensagem pronta para mostrar ao usuário."""


class ConfigAusente(ErroRelatorio):
    """O config.ini ainda não existe: é preciso perguntar os dados do banco."""


class ConsultaDemorada(ErroRelatorio):
    """A consulta passou do limite e foi interrompida; `diagnostico` aponta o report gerado."""

    def __init__(self, mensagem, diagnostico):
        super().__init__(mensagem)
        self.diagnostico = diagnostico


def pasta_do_programa():
    """Pasta do executável (PyInstaller) ou deste script."""
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def recurso(nome):
    """Arquivo embutido no executável (ou ao lado do script)."""
    return Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parent)) / nome


@dataclass(frozen=True)
class Config:
    host: str
    porta: int
    usuario: str
    senha: str
    pasta_saida: Path
    pasta_config: Path  # onde ficam config.ini, relatorio.log e diagnósticos
    contas: dict
    prefixos: dict
    siglas: dict = field(default_factory=dict)


@dataclass(frozen=True)
class Resultado:
    arquivo: Path
    linhas: int
    resumo: dict  # hp -> (quantidade, total)
    segundos: float


def sem_progresso(etapa):
    pass


def conectar(host, porta, usuario, senha, limite=None):
    """
    Abre uma sessão protegida para não pesar no banco:
    - max_execution_time: o próprio servidor interrompe qualquer SELECT
      que passe do limite e libera os recursos;
    - somente leitura e READ COMMITTED: nada é gravado e não se mantém
      uma visão antiga dos dados aberta.
    """
    limite = LIMITE_CONSULTA if limite is None else limite
    try:
        return pymysql.connect(
            host=host,
            port=int(porta),
            user=usuario,
            password=senha,
            charset='utf8mb4',
            connect_timeout=TEMPO_CONEXAO,
            read_timeout=limite + FOLGA_CLIENTE,
            write_timeout=limite + FOLGA_CLIENTE,
            autocommit=True,
            init_command=(
                f'SET SESSION max_execution_time = {int(limite * 1000)}, '
                'SESSION transaction_read_only = 1, '
                "SESSION transaction_isolation = 'READ-COMMITTED'"
            ),
        )
    except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
        raise ErroRelatorio(
            'Não foi possível conectar ao banco de dados.\n'
            'Verifique servidor, porta, usuário e senha e se o '
            f'computador está na rede do cartório.\n\nDetalhe: {e}'
        )


def testar_conexao(host, porta, usuario, senha):
    """Conecta e confere se o usuário enxerga os bancos usados pelo relatório."""
    if not host.strip():
        raise ErroRelatorio('Informe o servidor do banco (IP ou nome).')
    if not str(porta).strip().isdigit():
        raise ErroRelatorio('A porta deve ser um número (normalmente 3306).')
    if not usuario.strip():
        raise ErroRelatorio('Informe o usuário do banco.')

    conexao = conectar(host.strip(), str(porta).strip(), usuario.strip(), senha)
    try:
        with conexao.cursor() as cursor:
            for tabela in ('document.cx', 'document.selogo', 'eselo.selo'):
                try:
                    cursor.execute(f'SELECT 1 FROM {tabela} LIMIT 1')
                except pymysql.err.MySQLError as e:
                    raise ErroRelatorio(
                        f'A conexão funcionou, mas o usuário não consegue ler {tabela}.\n\nDetalhe: {e}'
                    )
    finally:
        conexao.close()


def salvar_banco(arquivo, host, porta, usuario, senha):
    """
    Grava os dados do banco no config.ini. Se o arquivo ainda não existe,
    ele é criado a partir do modelo; se existe, só a seção [banco] muda.
    """
    arquivo = Path(arquivo)
    if arquivo.exists():
        texto = arquivo.read_text(encoding='utf-8-sig')
    else:
        texto = recurso('config.exemplo.ini').read_text(encoding='utf-8')

    valores = {'host': host.strip(), 'porta': str(porta).strip(), 'usuario': usuario.strip(), 'senha': senha}
    for chave, valor in valores.items():
        texto = re.sub(rf'^\s*{chave}\s*=.*$', lambda _: f'{chave} = {valor}', texto, count=1, flags=re.M)
    arquivo.write_text(texto, encoding='utf-8')


def ler_banco(arquivo):
    """Dados da seção [banco] do config.ini, sem validar (para pré-preencher a tela)."""
    parser = configparser.ConfigParser(interpolation=None)
    try:
        parser.read(arquivo, encoding='utf-8-sig')
    except (configparser.Error, UnicodeDecodeError):
        return {}
    return dict(parser.items('banco')) if parser.has_section('banco') else {}


def mes_anterior(hoje=None):
    """Primeiro e último dia do mês anterior."""
    fim = (hoje or date.today()).replace(day=1) - timedelta(days=1)
    return fim.replace(day=1), fim


def ler_data(texto):
    """Aceita DD/MM/AAAA ou AAAA-MM-DD."""
    texto = texto.strip()
    for formato in ('%d/%m/%Y', '%Y-%m-%d'):
        try:
            return datetime.strptime(texto, formato).date()
        except ValueError:
            pass
    raise ErroRelatorio(f'Data inválida: "{texto}". Use o formato DD/MM/AAAA.')


def configurar_log(pasta):
    """Registra erros e relatórios gerados em relatorio.log, na pasta indicada."""
    handler = logging.FileHandler(Path(pasta) / 'relatorio.log', encoding='utf-8', delay=True)
    handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
    log.addHandler(handler)
    log.setLevel(logging.INFO)


def carregar_config(arquivo):
    """Lê e valida o config.ini. Levanta ConfigAusente se ele não existir."""
    arquivo = Path(arquivo)
    if not arquivo.exists():
        raise ConfigAusente(f'Arquivo de configuração não encontrado: {arquivo}')

    parser = configparser.ConfigParser(interpolation=None)
    parser.optionxform = str  # mantém maiúsculas (TD, PJ...)
    try:
        parser.read(arquivo, encoding='utf-8-sig')
    except (configparser.Error, UnicodeDecodeError) as e:
        raise ErroRelatorio(f'O arquivo {arquivo.name} está com erro de formatação:\n{e}')

    def valor(secao, chave):
        v = parser.get(secao, chave, fallback='').strip()
        if not v:
            raise ErroRelatorio(f'Preencha "{chave}" na seção [{secao}] do arquivo {arquivo.name}.')
        return v

    def secao(nome):
        if not parser.has_section(nome):
            raise ErroRelatorio(f'A seção [{nome}] não foi encontrada no arquivo {arquivo.name}.')
        return {k.strip(): v.strip() for k, v in parser.items(nome)}

    porta = valor('banco', 'porta')
    if not porta.isdigit():
        raise ErroRelatorio(f'A porta do banco no arquivo {arquivo.name} deve ser um número.')

    contas = {k: valor('contas', k) for k in CONTAS}
    for k, v in contas.items():
        if not re.fullmatch(r'\d{7}', v):
            raise ErroRelatorio(f'A conta "{k}" no arquivo {arquivo.name} deve ter 7 dígitos.')

    prefixos = {k.upper(): v for k, v in secao('prefixos').items()}
    for k, v in prefixos.items():
        if not re.fullmatch(r'\d{2}', v):
            raise ErroRelatorio(f'O prefixo "{k}" no arquivo {arquivo.name} deve ter 2 dígitos.')
    if len(set(prefixos.values())) != len(prefixos):
        raise ErroRelatorio(f'Há prefixos repetidos na seção [prefixos] do arquivo {arquivo.name}.')

    siglas = {k.upper(): v for k, v in secao('siglas').items()} if parser.has_section('siglas') else {}

    pasta = parser.get('saida', 'pasta', fallback='').strip()

    return Config(
        host=valor('banco', 'host'),
        porta=int(porta),
        usuario=valor('banco', 'usuario'),
        senha=parser.get('banco', 'senha', fallback='').strip(),
        pasta_saida=Path(pasta) if pasta else arquivo.resolve().parent,
        pasta_config=arquivo.resolve().parent,
        contas=contas,
        prefixos=prefixos,
        siglas=siglas,
    )


def linha(config, data, conta_debito, conta_credito, tipo, protocolo, hp, valor, historico):
    """
    Monta uma linha no layout do relatório:
    DD MM DEBITO CREDITO DOCUMENTO HP VALOR HISTORICO
    """
    centavos = int((valor * 100).to_integral_value())
    sigla = config.siglas.get(tipo, tipo)
    campos = [
        f'{data.day:02d}',
        f'{data.month:02d}',
        conta_debito,
        conta_credito,
        f'{config.prefixos[tipo]}{protocolo:07d}',
        f'{hp:>2}',
        f'{centavos:012d}',
        f'{historico} PROT. {sigla}.{protocolo}'[:32].ljust(32),
    ]
    return ' '.join(campos)


def lancamentos(config, row):
    """
    Converte uma linha da query nas linhas do TXT.
    Mesma regra do AFINCO: receita e devolução no caixa geram
    uma segunda linha movimentando o depósito prévio.
    """
    data, hp, tipo, protocolo, valor = row
    c = config.contas

    if hp == 1:  # receita de serviço no caixa
        yield linha(config, data, c['caixa'], c['servico'], tipo, protocolo, 1, valor, 'CX SERVICO')
        yield linha(config, data, c['deposito_previo'], c['caixa'], tipo, protocolo, 2, valor, 'DP SERVICO')

    elif hp == 6:  # devolução no caixa
        yield linha(config, data, c['devolucao'], c['caixa'], tipo, protocolo, 6, valor, 'CX DEVOLUCAO')
        yield linha(config, data, c['caixa'], c['deposito_previo'], tipo, protocolo, 6, valor, 'DP DEVOLUCAO')

    elif hp == 4:  # emolumento selado
        yield linha(config, data, c['emolumento'], c['deposito_previo'], tipo, protocolo, 4, valor, 'DP EMOLUMENTO')

    else:
        raise ValueError(f'Histórico padrão desconhecido: {hp}')


def consultar(config, data_ini, data_fim, progresso=sem_progresso):
    sql = recurso('rd_document.sql').read_text(encoding='utf-8')
    parametros = {'data_ini': data_ini.isoformat(), 'data_fim': data_fim.isoformat()}

    progresso('Conectando ao banco de dados...')
    conexao = conectar(config.host, config.porta, config.usuario, config.senha)
    inicio = time.monotonic()
    try:
        progresso(f'Consultando os lançamentos no banco (limite de {LIMITE_CONSULTA} s)...')
        with conexao.cursor() as cursor:
            cursor.execute(sql, parametros)
            return cursor.fetchall()
    except pymysql.err.MySQLError as e:
        decorrido = time.monotonic() - inicio
        codigo = e.args[0] if e.args else None
        if codigo == ER_QUERY_TIMEOUT or (codigo == CR_SERVER_LOST and decorrido >= LIMITE_CONSULTA):
            if codigo != ER_QUERY_TIMEOUT:  # quem desistiu foi o cliente: garante que o servidor pare
                interromper_no_servidor(config, conexao.thread_id())
            progresso('Gerando relatório de diagnóstico...')
            diagnostico = gerar_diagnostico(config, data_ini, data_fim, decorrido, e, sql, parametros)
            raise ConsultaDemorada(
                f'A consulta ao banco passou do limite de {LIMITE_CONSULTA} segundos e foi '
                'interrompida, sem prejuízo para o banco de dados.\n\n'
                'Tente gerar o relatório com um período menor (por exemplo, um mês por vez).\n'
                'Se o problema continuar, procure o suporte e envie o arquivo de diagnóstico:\n'
                f'{diagnostico}',
                diagnostico,
            )
        raise ErroRelatorio(
            'O banco de dados não respondeu à consulta (a conexão caiu).\n'
            f'Tente novamente; se continuar, avise a TI.\n\nDetalhe: {e}'
        )
    finally:
        conexao.close()


def interromper_no_servidor(config, id_conexao):
    """KILL QUERY por outra conexão, para a consulta abandonada não continuar rodando."""
    try:
        conexao = conectar(config.host, config.porta, config.usuario, config.senha, limite=10)
        try:
            with conexao.cursor() as cursor:
                cursor.execute(f'KILL QUERY {int(id_conexao)}')
        finally:
            conexao.close()
        log.warning('Consulta %s interrompida no servidor (KILL QUERY).', id_conexao)
    except Exception:
        log.exception('Não foi possível interromper a consulta %s no servidor.', id_conexao)


def gerar_diagnostico(config, data_ini, data_fim, decorrido, erro, sql, parametros):
    """
    Grava um report para o suporte analisar a consulta lenta: contexto,
    erro, plano de execução (EXPLAIN) e o SQL com os parâmetros.
    Não inclui a senha.
    """
    agora = datetime.now()
    arquivo = config.pasta_config / f'diagnostico_consulta_{agora:%Y-%m-%d_%H%M%S}.txt'

    versao, plano, sql_final = '(não obtida)', '(não obtido)', sql
    try:
        conexao = conectar(config.host, config.porta, config.usuario, config.senha, limite=20)
        try:
            with conexao.cursor() as cursor:
                sql_final = cursor.mogrify(sql, parametros)
                cursor.execute('SELECT VERSION()')
                versao = cursor.fetchone()[0]
                cursor.execute('EXPLAIN ' + sql_final)  # só o plano: não executa a consulta
                colunas = [c[0] for c in cursor.description]
                plano = '\n'.join(
                    ' | '.join(f'{c}={v}' for c, v in zip(colunas, linha) if v is not None)
                    for linha in cursor.fetchall()
                )
        finally:
            conexao.close()
    except Exception as e:
        plano = f'(não obtido: {e})'

    secoes = [
        'DIAGNÓSTICO — CONSULTA ACIMA DO LIMITE DE TEMPO',
        '=' * 60,
        f'Data/hora:          {agora:%d/%m/%Y %H:%M:%S}',
        f'Período pedido:     {data_ini:%d/%m/%Y} a {data_fim:%d/%m/%Y} ({(data_fim - data_ini).days + 1} dias)',
        f'Tempo até parar:    {formatar_tempo(decorrido)} (limite: {LIMITE_CONSULTA} s)',
        f'Erro:               {erro}',
        f'Servidor:           {config.host}:{config.porta} (usuário {config.usuario})',
        f'Versão do MySQL:    {versao}',
        f'Computador:         {platform.platform()} / Python {platform.python_version()}',
        '',
        'PLANO DE EXECUÇÃO (EXPLAIN)',
        '-' * 60,
        plano,
        '',
        'SQL EXECUTADO',
        '-' * 60,
        sql_final.strip(),
        '',
    ]
    arquivo.write_text('\n'.join(secoes), encoding='utf-8')
    log.warning('Consulta acima do limite (%s a %s, %.1f s). Diagnóstico: %s', data_ini, data_fim, decorrido, arquivo)
    return arquivo


def arquivo_saida(config, data_ini, data_fim):
    return config.pasta_saida / f'RecDoc_{data_ini}.{data_fim}.txt'


def gerar(config, data_ini, data_fim, progresso=sem_progresso):
    """
    Consulta o banco e grava o TXT. Retorna o Resultado.
    `progresso(etapa)` é chamado a cada etapa, para a interface mostrar.
    """
    if data_fim < data_ini:
        raise ErroRelatorio('A data final é anterior à data inicial.')

    inicio = time.monotonic()
    rows = consultar(config, data_ini, data_fim, progresso)
    progresso(f'Gravando o arquivo ({len(rows)} lançamentos)...')

    invalidos = [r for r in rows if r[3] is None or r[2] not in config.prefixos]
    if invalidos:
        detalhes = '\n'.join(
            f'  {r[0]:%d/%m/%Y}  HP {r[1]}  tipo {r[2]}  protocolo {r[3]}  R$ {moeda(r[4])}'
            for r in invalidos[:20]
        )
        raise ErroRelatorio(
            f'{len(invalidos)} lançamento(s) sem processo vinculado ou com tipo '
            f'sem prefixo no config.ini. Relatório não gerado.\n\n{detalhes}'
        )

    if not rows:
        raise ErroRelatorio('Não foram encontrados lançamentos no período informado.')

    arquivo = arquivo_saida(config, data_ini, data_fim)

    resumo = defaultdict(lambda: [0, Decimal('0')])
    qtd_linhas = 0
    try:
        config.pasta_saida.mkdir(parents=True, exist_ok=True)
        with open(arquivo, 'w', encoding='ascii', newline='') as f:
            for row in rows:
                resumo[row[1]][0] += 1
                resumo[row[1]][1] += row[4]
                for texto in lancamentos(config, row):
                    f.write(texto + '\r\n')
                    qtd_linhas += 1
    except PermissionError:
        raise ErroRelatorio(f'Não foi possível gravar {arquivo}.\nO arquivo pode estar aberto em outro programa.')
    except OSError as e:
        raise ErroRelatorio(f'Não foi possível gravar {arquivo}.\nVerifique a pasta de saída no config.ini.\n\nDetalhe: {e}')

    segundos = time.monotonic() - inicio
    resultado = Resultado(arquivo, qtd_linhas, {hp: tuple(v) for hp, v in resumo.items()}, segundos)
    log.info('Relatório %s a %s gerado: %s (%s linhas, %.1f s)', data_ini, data_fim, arquivo, qtd_linhas, segundos)
    return resultado


def formatar_tempo(segundos):
    """3.42 -> '3,4 s'; 65 -> '1 min 05 s'"""
    if segundos < 60:
        return f'{segundos:.1f} s'.replace('.', ',')
    minutos, resto = divmod(int(segundos), 60)
    return f'{minutos} min {resto:02d} s'


def moeda(valor):
    """1234.5 -> '1.234,50'"""
    return f'{valor:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')


def formatar_resumo(resultado):
    linhas = [
        f'Arquivo: {resultado.arquivo}',
        f'Linhas no TXT: {resultado.linhas}   (concluído em {formatar_tempo(resultado.segundos)})',
    ]
    for hp in (1, 6, 4):
        if hp in resultado.resumo:
            qtd, total = resultado.resumo[hp]
            linhas.append(f'  HP {hp} ({NOMES_HP[hp]}): {qtd} lançamento(s), R$ {moeda(total)}')
    return '\n'.join(linhas)
