# Empiricus - Shapley Attribution Model

run_all.py

- Descrição: Roda todos os programas na ordem certa
- Requer: conversions2017.csv, credenciais Redshift e caminho de Python em .env, copywriters.csv

copywriters.py

- Descrição: Cria um dicionário que associa copies a copywriters
- Requer: copywriters.csv
- Output: copywriters.pickle

assinaturas_redshift.py

- Descrição: Cria um dicionário que associa assinaturas a uma tupla com sua receita nova líquida e categoria
- Requer: banco de dados hmlredshift
- Output: paid_subs.pickle

validar_assinaturas.py

- Descrição: Cruza as assinaturas do BigQuery com a tabela de copywriters e a tabela tb_rep_receita, eliminando assinaturas não pagas. O cálculo de Last Click acaba aqui.
- Requer: copywriters.pickle, paid_subs.pickle, conversions2017.csv
- Output: Se last click, last_click\_{conversoes/receita}\_{categoria}.pickle. Se Shapley, shapley\_{sp/sf}\_{conversoes}\_{categoria}.pickle.
- Args: conversoes/receita lc/sp/sf frontend/backend

shapley_value.py

- Descrição: Calcula o valor Shapley
- Requer: conversion\_groups\_{sp/sf}\_{conversoes/receita}\_{categoria}.pickle
- Output: shapley\_{sp/sf}\_{conversoes/receita}\_{categoria}
- Args: sp/sf conversoes/receita frontend/backend

v_value.pyx

- Descrição: Arquivo Cython com funções auxiliares a shapley_value.py

setup.py

- Descrição: Compila o arquivo v_value.pyx para ser usado em arquivos Python
- Requer: Um compilador C++ no computador. Recomendado: [Visual Studio Build Tools][vstools-url]
- Args: build_ext --inplace

.env

- Descrição: Contém credenciais para acesso ao banco Redshift

## Dependências
> numpy, pandas, Cython, psycopg2, dotenv

Cada um desses módulos pode ser instalado com o comando

```commandline
pip install nome_do_modulo
```


[vstools-url]: https://visualstudio.microsoft.com/downloads/
