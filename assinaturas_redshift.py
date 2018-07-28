import pandas as pd
from psycopg2 import connect
import pickle
import os
from dotenv import load_dotenv
from pathlib import Path


def get_credentials() -> (str, str):
    """ Extrai usuario e senha do banco Redshift HML do arquivo '.env'

    :return: (usuario, senha)
    """
    env_path = Path('.') / '.env'
    load_dotenv(dotenv_path=env_path)
    return os.getenv('REDSHIFT_USERNAME'), os.getenv('REDSHIFT_PASSWORD')


def get_df_from_query() -> pd.DataFrame:
    """ Cria dataframe de vendas a partir da tabela sales.tb_rep_receita no Redshift

    :return: dataframe de vendas
    """
    username, password = get_credentials()
    con = connect(host='analytics-bi.cdlqehqrgcus.us-east-1.redshift.amazonaws.com',
                  dbname='hmlredshift', port=5439, user=username, password=password)
    query: str = """
        SELECT
            subscription_id,
            CAST(rec_liq_novo AS REAL),
            categoria_detalhe
        FROM
            sales.tb_rep_receita
        WHERE
            subscription_id IS NOT NULL
            AND CAST(rec_liq_novo AS REAL) > 0.0
            AND ult_dia_mes BETWEEN '2017-07-01' AND '2017-12-31';
    """
    df: pd.DataFrame = pd.read_sql(query, con=con)
    con.close()
    return df
    
    
def clean_df(df: pd.DataFrame) -> pd.DataFrame:
    """ Regulariza a coluna 'categoria' como somente 'Frontend' e 'Backend'

    :param df:
    :return:
    """
    df['categoria'] = df['categoria_detalhe'].apply(lambda s: 'Frontend' if s in
                                                    {'Frontend', 'Bundle Front'} else 'Backend')
    df = df.drop(columns='categoria_detalhe')
    return df


def main():
    df: pd.DataFrame = get_df_from_query()
    df = clean_df(df)
    paid_subs: dict = {}
    for index, row in df.iterrows():
        paid_subs[row['subscription_id']] = (row['rec_liq_novo'], row['categoria'])
    with open('paid_subs.pickle', 'wb') as file:
        pickle.dump(paid_subs, file)
    print('Sucesso')

        
if __name__ == '__main__':
    main()
