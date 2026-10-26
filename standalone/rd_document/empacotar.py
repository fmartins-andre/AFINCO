"""
Gera os executáveis (PyInstaller) e o pacote de distribuição para o
sistema atual: ZIP no Windows, tar.gz no Linux.

Uso:
    pip install pymysql==1.1.1 pyinstaller==6.11.1
    python empacotar.py [versao]

O pacote sai em dist/RelatorioReceitas-<versao>-<sistema>.<zip|tar.gz>.
O config.ini não vai no pacote: o programa pergunta os dados do banco
na primeira execução e cria o arquivo.
"""
import os
import shutil
import sys
from pathlib import Path

import PyInstaller.__main__

AQUI = Path(__file__).resolve().parent
NOME = 'RelatorioReceitas'
WINDOWS = sys.platform == 'win32'


def executavel(script, nome, janela, destino, temporario):
    PyInstaller.__main__.run([
        str(AQUI / script),
        '--onefile',
        '--noconfirm',
        '--windowed' if janela else '--console',
        '--name', nome,
        '--add-data', f'{AQUI / "rd_document.sql"}{os.pathsep}.',
        '--add-data', f'{AQUI / "config.exemplo.ini"}{os.pathsep}.',
        '--distpath', str(destino),
        '--workpath', str(temporario / 'work'),
        '--specpath', str(temporario),
    ])


def main():
    versao = sys.argv[1] if len(sys.argv) > 1 else 'dev'
    versao = versao.removeprefix('rd-document-')  # tag do GitHub: rd-document-v1.0.0
    sistema = 'windows' if WINDOWS else 'linux'

    dist = AQUI / 'dist'
    temporario = AQUI / 'build'
    pacote = dist / f'{NOME}-{versao}-{sistema}'
    shutil.rmtree(pacote, ignore_errors=True)
    shutil.rmtree(temporario, ignore_errors=True)

    executavel('janela.py', NOME, True, pacote, temporario)
    executavel('terminal.py', f'{NOME}-Terminal', False, pacote, temporario)

    distribuicao = AQUI / 'distribuicao'
    leia_me = (distribuicao / f'LEIA-ME-{sistema}.txt').read_text(encoding='utf-8')
    if WINDOWS:  # Bloco de Notas antigo: CRLF e BOM
        (pacote / 'LEIA-ME.txt').write_text(leia_me, encoding='utf-8-sig', newline='\r\n')
    else:
        (pacote / 'LEIA-ME.txt').write_text(leia_me, encoding='utf-8')
    if not WINDOWS:
        atalho = pacote / f'{NOME}.desktop'
        shutil.copyfile(distribuicao / f'{NOME}.desktop', atalho)
        atalho.chmod(0o755)

    formato = 'zip' if WINDOWS else 'gztar'  # tar.gz preserva a permissão de execução
    arquivo = shutil.make_archive(str(pacote), formato, root_dir=dist, base_dir=pacote.name)
    print(f'\nPacote gerado: {arquivo}')


if __name__ == '__main__':
    main()
