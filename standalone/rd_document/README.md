# Relatório de Receitas — Escriba Document

Versão standalone do relatório de receitas do AFINCO (`app/relatorios/_make_rd_txt_file.py`).
Lê do banco `document` (TD / PJ / Certidões) e gera um TXT no mesmo layout, só com receitas.

## Uso

```bash
cp .env.example .env    # preencher DB_USER e DB_PASSWORD
docker compose run --rm rd_document 2026-10-01 2026-10-31
```

O arquivo sai em `./saida/RecDoc_<ini>.<fim>.txt`.

Sem Docker:

```bash
pip install pymysql==1.1.1
DB_USER=... DB_PASSWORD=... python rd_document.py 2026-10-01 2026-10-31 --saida ./saida
```

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
