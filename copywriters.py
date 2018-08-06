"""
    Lê o csv copywriters.csv, que é a primeira página da planilha
    https://docs.google.com/spreadsheets/d/1kykFgj3o45BYN8_-fDmfHhCAY8kozViMWfOaS74hEvA/edit#gid=1794656425
    e cria um dicionário que associa copies a copywriters
"""


import pandas as pd
import numpy as np
import pickle


def read_copy_csv() -> pd.DataFrame:
    df = pd.read_csv('copywriters.csv')
    df = df.drop(columns=['Unnamed: 0', 'nome do copy', 'sigla', 'familia produto', 'link do copy',
                          'data de criação', 'data da ultima revisão', 'status', 'externo',
                          'observações', 'gauntlets', 'agrupador', 'multiplicador',
                          'data da ultima revisão.1', 'NÂO APAGAR'])
    df = df.drop(0)
    df = df.dropna(subset=['codigo do copy', 'copywriter'])
    df['codigo do copy'] = df['codigo do copy'].map(lambda x: x.strip().lower() if
                                                    type(x) == str else np.nan)
    df['tipo'] = df['tipo'].map(lambda x: 'Frontend' if (x.strip() == 'Essencial') else
                                ('Backend' if (x.strip() == 'Premium') else ''))
    df['copywriter_id'] = df['copywriter_id'].astype(int)
    df['copywriter_completo'] = df['copywriter'] + ' - ' + df['tipo']
    return df


def make_copywriter_dict(df: pd.DataFrame) -> dict:
    copywriter_dict = df.set_index('codigo do copy').to_dict()['copywriter_completo']
    copywriter_dict['ie'] = copywriter_dict['ie06']
    copywriter_dict['bter01'] = copywriter_dict['bterf01']
    return copywriter_dict


def pickle_copywriters(copywriter_dict: dict):
    with open('copywriters.pickle', 'wb') as file:
        pickle.dump(copywriter_dict, file, pickle.HIGHEST_PROTOCOL)


def main():
    df: pd.DataFrame = read_copy_csv()
    copywriter_dict = make_copywriter_dict(df)
    pickle_copywriters(copywriter_dict)
    print('Sucesso com copywriters')


if __name__ == '__main__':
    main()
