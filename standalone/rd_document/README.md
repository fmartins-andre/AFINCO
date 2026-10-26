# Relatório de Receitas — Escriba Document

Versão standalone do relatório de receitas do AFINCO (`app/relatorios/_make_rd_txt_file.py`).
Lê do banco `document` (TD / PJ / Certidões) e gera um TXT no mesmo layout, só com receitas.

## Para o usuário final

Baixe o pacote do sistema na página de **Releases** do GitHub (`RelatorioReceitas-<versão>-windows.zip` ou `-linux.tar.gz`), extraia e siga o `LEIA-ME.txt`. Cada pacote traz dois executáveis:

- `RelatorioReceitas`: janela para escolher o período e gerar o relatório;
- `RelatorioReceitas-Terminal`: o mesmo no terminal, interativo, ou direto com `01/10/2026 31/10/2026`.

Na primeira execução, o programa pergunta servidor, porta, usuário e senha, testa a conexão e cria o `config.ini` na pasta do programa. O TXT e o `relatorio.log` (erros) também ficam nessa pasta.

## Configuração (`config.ini`)

Tudo que é configurável fica no `config.ini`. Só o SQL fica embutido no programa. O modelo é o [config.exemplo.ini](config.exemplo.ini):

| Seção | Conteúdo |
|---|---|
| `[banco]` | host, porta, usuário e senha (preenchidos pelo programa na primeira execução) |
| `[saida]` | pasta do TXT (vazio = pasta do programa) |
| `[contas]` | contas contábeis (7 dígitos) |
| `[prefixos]` | prefixo do documento por tipo (2 dígitos, sem repetir) |
| `[siglas]` | sigla do histórico quando difere do tipo (`EX = ED`) |

## Proteção do banco de dados

Cada conexão é aberta com:

- `max_execution_time = 90000`: o **próprio servidor** interrompe qualquer SELECT acima de 90 s e libera os recursos (requer MySQL 5.7.8+);
- `transaction_read_only = 1`: a sessão não grava nada, mesmo que o usuário tenha permissão;
- `transaction_isolation = READ-COMMITTED`: não mantém uma visão antiga dos dados aberta.

Se o servidor não interromper, o cliente desiste aos 105 s e executa `KILL QUERY` por outra conexão, para a consulta não continuar rodando sozinha.

Quando o limite estoura, o programa grava `diagnostico_consulta_<data>.txt` na pasta do programa e orienta o usuário a reduzir o período ou procurar o suporte. O arquivo traz período, tempo, erro, versão do MySQL, `EXPLAIN` e o SQL com os parâmetros. A senha não vai no arquivo.

Os limites ficam em `rd_document.py`: `LIMITE_CONSULTA`, `FOLGA_CLIENTE` e `TEMPO_CONEXAO`.

## Desenvolvimento

| Arquivo | Papel |
|---|---|
| `rd_document.py` | núcleo: config, consulta, layout do TXT |
| `rd_document.sql` | query (parâmetros `%(data_ini)s` e `%(data_fim)s`) |
| `janela.py` | interface em janela (Tkinter) |
| `terminal.py` | interface de terminal |
| `empacotar.py` | gera executáveis e pacote (PyInstaller) |
| `distribuicao/` | LEIA-ME e atalho `.desktop` que vão no pacote |

```bash
pip install pymysql==1.1.1
python janela.py                              # janela
python terminal.py                            # terminal interativo
python terminal.py 01/10/2026 31/10/2026      # direto
```

O Python precisa ter Tkinter para a janela (no Linux, pacote `python3-tkinter` ou `python3-tk`).

Com Docker (só modo terminal; `config.ini`, log e TXT ficam em `./dados`):

```bash
docker compose run --rm rd_document                          # interativo
docker compose run --rm rd_document 01/10/2026 31/10/2026
```

## Empacotamento e publicação

O workflow [`.github/workflows/rd-document.yml`](../../.github/workflows/rd-document.yml) compila no Windows e no Ubuntu 22.04.

- **Publicar uma versão**: criar e enviar uma tag `rd-document-vX.Y.Z`. Os pacotes são anexados a uma Release.
- **Testar sem publicar**: rodar o workflow manualmente (Actions → rd-document → Run workflow). Os pacotes ficam como artefatos do run.

Localmente, gera o pacote do sistema atual em `dist/`:

```bash
pip install pymysql==1.1.1 pyinstaller==6.11.1
python empacotar.py v1.0.0
```

O executável Windows não é assinado. Na primeira execução, o SmartScreen mostra um aviso, e o LEIA-ME explica como seguir.

## O que entra

| HP | Origem | Débito | Crédito | Histórico |
|----|--------|--------|---------|-----------|
| 1 | `cx` com valor > 0 | 1000001 | 9010001 | `CX SERVICO` |
| 2 | (linha extra de cada HP 1) | 1010001 | 1000001 | `DP SERVICO` |
| 6 | `cx` com valor < 0 | 9300008 | 1000001 | `CX DEVOLUCAO` |
| 6 | (linha extra de cada devolução) | 1000001 | 1010001 | `DP DEVOLUCAO` |
| 4 | selos confirmados no eSelo, por protocolo e dia | 1010002 | 1010001 | `DP EMOLUMENTO` |

- Documento: prefixo (2 dígitos) + protocolo (7 dígitos). O prefixo só identifica a origem, sem valor contábil.
  O 1º dígito é a natureza: 9 ato, 8 certidão, 7 exame, 6 despesa. O 2º dígito é o tipo: repetido no
  Registro de Imóveis (AFINCO) e decrescente no Document.

  | Sistema | Sigla | Significado | Prefixo |
  |---|---|---|---|
  | RI (AFINCO) | RE | Registro | 99 |
  | Document | TD | Títulos e Documentos | 98 |
  | Document | PJ | Pessoa Jurídica | 97 |
  | Document | MT | Matrícula | 95 |
  | Document | LV | Livro *(reservado)* | 94 |
  | Document | AP | Apostila *(reservado)* | 93 |
  | Document | IR | *(reservado)* | 92 |
  | RI (AFINCO) | CE | Certidão | 88 |
  | Document | CT | Certidões TD/PJ | 87 |
  | RI (AFINCO) | EX | Exame e Cálculo | 77 *(reservado)* |
  | Document | ED | Exame e Cálculo (`EX` no banco) | 76 |
  | AFINCO | — | Despesas | 66 |

- Histórico: `<texto> PROT. <sigla>.<protocolo>`, por exemplo `DP EMOLUMENTO PROT. TD.165`.
  A sigla é o tipo do banco, exceto o exame, que vira `ED`, porque `EX` já é o exame do RI no AFINCO.
- Selos de processos cancelados não entram.
- Se algum lançamento não tiver processo vinculado, o relatório não é gerado e os casos são listados.

## Layout da linha (81 caracteres, CRLF)

```
DD MM DEBITO  CREDITO DOCUMENTO HP VALOR(12)    HISTORICO(32)
01 10 1010002 1010001 870000109  4 000000001856 DP EMOLUMENTO PROT. CT.109
```

## Diferença em relação ao relatório do AFINCO

Os selos são agrupados por **protocolo e dia de confirmação**. No AFINCO, o agrupamento é só por protocolo, e a data da linha fica arbitrária quando os selos de um protocolo são confirmados em dias diferentes.
A query também roda com `ONLY_FULL_GROUP_BY` ligado.
