"""
Relatório de Receitas — Escriba Document — modo terminal.

Uso:
    terminal.py                          pergunta o período (padrão: mês anterior)
    terminal.py 01/10/2026 31/10/2026    gera direto
    terminal.py ... --config CAMINHO     usa outro config.ini

Se o config.ini não existir, pergunta os dados do banco, testa a
conexão e cria o arquivo.
"""
import argparse
import getpass
import sys
from pathlib import Path

import rd_document as rd


def perguntar(rotulo, padrao=''):
    sufixo = f' [{padrao}]' if padrao else ''
    return input(f'{rotulo}{sufixo}: ').strip() or padrao


def configurar(arquivo):
    """Pergunta os dados do banco até a conexão funcionar e grava o config.ini."""
    print('Arquivo de configuração não encontrado. Vamos criá-lo.\n')
    while True:
        host = perguntar('Servidor do banco (IP ou nome)')
        porta = perguntar('Porta', '3306')
        usuario = perguntar('Usuário')
        senha = getpass.getpass('Senha: ')

        print('\nTestando a conexão...')
        try:
            rd.testar_conexao(host, porta, usuario, senha)
        except rd.ErroRelatorio as e:
            print(f'\n{e}\n')
            if perguntar('Tentar novamente? (S/N)', 'S').upper().startswith('N'):
                raise SystemExit(1)
            continue

        rd.salvar_banco(arquivo, host, porta, usuario, senha)
        print(f'Conexão OK. Configuração salva em {arquivo}\n')
        return


def perguntar_periodo():
    ini, fim = rd.mes_anterior()
    while True:
        try:
            data_ini = rd.ler_data(perguntar('Data inicial (DD/MM/AAAA)', f'{ini:%d/%m/%Y}'))
            data_fim = rd.ler_data(perguntar('Data final   (DD/MM/AAAA)', f'{fim:%d/%m/%Y}'))
            return data_ini, data_fim
        except rd.ErroRelatorio as e:
            print(e)


def executar(args):
    arquivo = args.config
    try:
        config = rd.carregar_config(arquivo)
    except rd.ConfigAusente:
        if not sys.stdin.isatty():
            raise rd.ErroRelatorio(
                f'Arquivo de configuração não encontrado: {arquivo}\n'
                'Execute o programa de forma interativa para criá-lo.'
            )
        configurar(arquivo)
        config = rd.carregar_config(arquivo)

    if args.data_ini:
        data_ini, data_fim = rd.ler_data(args.data_ini), rd.ler_data(args.data_fim)
    else:
        data_ini, data_fim = perguntar_periodo()

    print(f'\nGerando relatório de {data_ini:%d/%m/%Y} a {data_fim:%d/%m/%Y}...')
    print(rd.formatar_resumo(rd.gerar(config, data_ini, data_fim)))


def main():
    parser = argparse.ArgumentParser(description='Relatório de Receitas — Escriba Document')
    parser.add_argument('data_ini', nargs='?', help='DD/MM/AAAA ou AAAA-MM-DD')
    parser.add_argument('data_fim', nargs='?', help='DD/MM/AAAA ou AAAA-MM-DD')
    parser.add_argument(
        '--config', type=Path, default=rd.pasta_do_programa() / rd.CONFIG_NOME,
        help='caminho do config.ini (padrão: pasta do programa)',
    )
    args = parser.parse_args()
    if bool(args.data_ini) != bool(args.data_fim):
        parser.error('informe as duas datas, ou nenhuma para responder às perguntas')

    rd.configurar_log(args.config.resolve().parent)
    interativo = not args.data_ini
    codigo = 0
    try:
        executar(args)
    except rd.ErroRelatorio as e:
        rd.log.error('%s', e)
        print(f'\nERRO: {e}', file=sys.stderr)
        codigo = 1
    except (KeyboardInterrupt, EOFError):
        print('\nCancelado.')
        codigo = 1
    except Exception:
        rd.log.exception('Erro inesperado')
        print('\nERRO inesperado. Os detalhes foram gravados em relatorio.log.', file=sys.stderr)
        codigo = 2

    # aberto com dois cliques: segura a janela para a pessoa ler o resultado
    if interativo and sys.stdin.isatty():
        try:
            input('\nPressione Enter para sair...')
        except (KeyboardInterrupt, EOFError):
            pass
    return codigo


if __name__ == '__main__':
    sys.exit(main())
