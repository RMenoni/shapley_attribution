"""
    Realiza cruzamento entre conversões no BigQuery e vendas no Redshift, eliminando
    assinaturas que geraram 0.00 receita.
    Também faz a conversão de copies para copywriters.
    Dependendo dos argumentos dados, considera
        - Número de conversões ou receita gerada
        - Modelo Last Click, Shapley Value, ou Shapley Value só com vendas fantasmas
        - Vendas de front ou de back
"""


import pandas as pd
import pickle
import sys


def copylist_to_writerlist(copy_list: str, copywriters: dict, category: str) -> str:
    """ Traduz lista de copies para lista de copywriters

    :param copy_list: lista de copies separados por virgula
    :param copywriters: dict com chaves copy e valores copywriter
    :param category: 'frontend' ou 'backend'
    :return: lista de copywriters separados por virgula
    """
    copywriter_set: set = set()
    for copy in copy_list.split(','):
        copywriter: str = copywriters.get(copy, '')
        if copywriter == '' or category in copywriter:
            copywriter_set.add(copywriter)
    return ','.join(sorted(copywriter_set))


def get_copywriters_and_paidsubs() -> (dict, dict):
    """ Extrai dois dicts de pickles:
            - um de copies e copywriters
            - um de assinaturas e (receita nova liquida, categoria)

    :return: dois dicts
    """
    with open('copywriters.pickle', 'rb') as file:
        copywriters = pickle.load(file)
    with open('paid_subs.pickle', 'rb') as file:
        paid_subs = pickle.load(file)
    return copywriters, paid_subs


def pickle_conversions(conversions_dict: dict, model: str, conv_or_revenue: str, category: str):
    """ Armazena dict com conversoes/receita por copywriters em um arquivo pickle

    :param conversions_dict:
    :param model: modelo 'lc'/'sp'/'sf'
    :param conv_or_revenue: 'conversions'/'revenue'
    :param category: 'frontend'/'backend'
    """
    filename = (f'last_click_{conv_or_revenue}_{category}.pickle' if model == 'lc' else
                f'conversion_groups_{model}_{conv_or_revenue}_{category}.pickle')
    with open(filename, 'wb') as file:
        pickle.dump(conversions_dict, file)
    print('Sucesso')


def get_conversions_from_csv() -> pd.DataFrame:
    """ Extrai dataframe de conversoes de csv

    :return:
    """
    conversions = pd.read_csv('conversions2017.csv')
    conversions = conversions.drop(columns='Number of Records')
    conversions['Copy List'] = conversions['Copy List'].apply(lambda x: x if type(x) == str else '')
    conversions['Last Copy'] = conversions['Last Copy'].apply(lambda x: x if type(x) == str else '')
    return conversions


def process_conversions(conversions: pd.DataFrame, copywriters: dict, paid_subs: dict,
                        category: str, model: str) -> pd.DataFrame:
    """ Cruza as conversoes do BigQuery com as assinaturas no Redshift

    :param conversions: dataframe de conversoes
    :param copywriters: dict de chaves copies e valores copywriters
    :param paid_subs: dict de chaves assinatura e valores (receita nova liquida, categoria)
    :param category: 'Frontend' ou 'Backend'
    :param model: 'lc'/'sp'/'sf'
    :return:
    """
    conversions['Valor'] = conversions['Assinatura'].apply(lambda x: paid_subs.get(x, (0, ''))[0])
    conversions = conversions[conversions['Valor'] > 0]
    conversions['Categoria'] = conversions['Assinatura'].apply(lambda x: paid_subs.get(x, (0, ''))[1])
    conversions = conversions[conversions['Categoria'] == category]
    if model == 'lc':
        conversions['Writer List'] = conversions['Last Copy'].apply(lambda x: copylist_to_writerlist(
            x, copywriters, category))
    else:
        conversions['Writer List'] = conversions['Copy List'].apply(lambda x: copylist_to_writerlist(
            x, copywriters, category))
    return conversions


def make_conversion_dict(conversions: pd.DataFrame, conv_or_revenue: str, model: str) -> dict:
    """ Agrupa vendas por 'Writer List' e transforma em dict

    :param conversions: dataframe de vendas
    :param conv_or_revenue: 'conversoes' ou 'receita'
    :param model: 'lc', 'sp', ou 'sf'
    :return: dict com chaves lista de writers e valores # de conversoes ou receita gerada
    """
    if model == 'sf':
        conversions = conversions[conversions['Fantasma']]
    if conv_or_revenue == 'conversoes':
        conversions_dict = conversions.groupby('Writer List').count().to_dict()['Valor']
    else:
        conversions_dict = conversions.groupby('Writer List').sum().to_dict()['Valor']
    return conversions_dict


def main(conv_or_revenue: str, model: str, category: str):
    copywriters, paid_subs = get_copywriters_and_paidsubs()
    conversions: pd.DataFrame = process_conversions(get_conversions_from_csv(), copywriters,
                                                    paid_subs, category, model)
    conversions_dict: dict = make_conversion_dict(conversions, conv_or_revenue, model)
    pickle_conversions(conversions_dict, model, conv_or_revenue, category)
    
    
if __name__ == '__main__':
    if len(sys.argv) >= 4 and sys.argv[1] in ('conversoes', 'receita') and sys.argv[2] in \
            ('lc', 'sp', 'sf') and sys.argv[3] in ('frontend', 'backend'):
        main(sys.argv[1], sys.argv[2], f'{str(sys.argv[3]).title()}')
    else:
        print('Argumento(s) inválido(s).\nUso: python validar_assinaturas.py conversoes/receita'
              ' lc/sp/sf frontend/backend')
