import pandas as pd
import numpy as np
from psycopg2 import connect
import pickle


def get_df_from_query() -> pd.DataFrame:
    con = connect(host='analytics-bi.cdlqehqrgcus.us-east-1.redshift.amazonaws.com', dbname='hmlredshift', port=5439, user='', password='')
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
    df['categoria'] = df['categoria_detalhe'].apply(lambda s: 'Frontend' if s in {'Frontend', 'Bundle Front'} else 'Backend')
    return df.drop(columns='categoria_detalhe')


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
    