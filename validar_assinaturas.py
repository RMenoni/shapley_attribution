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
        if copywriter != '' and category in copywriter:
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


def pickle_conversions(conversions_dict: dict, model: str):
    """ Armazena dict com conversoes/receita por copywriters em um arquivo pickle

    :param conversions_dict:
    :param model: modelo 'lc'/'sp'/'sf'
    """
    with open(f'conversion_groups_{model}.pickle', 'wb') as file:
        pickle.dump(conversions_dict, file)
    print('Sucesso')


def get_conversions_from_csv(model: str) -> pd.DataFrame:
    """ Extrai dataframe de conversoes de csv

    :param model: se for 'lc', last click, senao shapley
    :return:
    """
    conversions = pd.read_csv('conversions_lastclick2017.csv') if model == 'lc' else pd.\
        read_csv('conversions2017.csv')
    conversions = conversions.drop(columns='Number of Records')
    return conversions


def filter_category(conversions: pd.DataFrame, fb: str) -> pd.DataFrame:
    """ Filtra as conversoes para que so haja frontend ou backend

    :param conversions: dataframe de conversoes
    :param fb: string 'frontend' ou 'backend'
    :return: dataframe filtrado
    """
    conversions = conversions[conversions['Categoria'] == f'{fb}']
    return conversions


def process_conversions(conversions: pd.DataFrame, copywriters: dict, paid_subs: dict,
                        category: str) -> pd.DataFrame:
    """ Cruza as conversoes do BigQuery com as assinaturas no Redshift

    :param conversions: dataframe de conversoes
    :param copywriters: dict de chaves copies e valores copywriters
    :param paid_subs: dict de chaves assinatura e valores (receita nova liquida, categoria)
    :param category: 'Frontend' ou 'Backend'
    :return:
    """
    conversions['Valor'] = conversions['Assinatura'].apply(lambda x: paid_subs.get(x, (0, ''))[0])
    conversions = conversions[conversions['Valor'] > 0]
    conversions['Categoria'] = conversions['Assinatura'].apply(lambda x: paid_subs.get(x, (0, ''))[1])
    conversions = filter_category(conversions, category)
    conversions = conversions.dropna(subset=['Copy List'])
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
    conversions = conversions.groupby('Writer List')
    if conv_or_revenue == 'conversoes':
        conversions_dict = conversions.count().to_dict()['Valor']
    else:
        conversions_dict = conversions.sum().to_dict()['Valor']
    del conversions_dict['']
    return conversions_dict


def main(conv_or_revenue: str, model: str, category: str):
    copywriters, paid_subs = get_copywriters_and_paidsubs()
    conversions: pd.DataFrame = process_conversions(get_conversions_from_csv(model), copywriters,
                                                    paid_subs, category)
    conversions_dict: dict = make_conversion_dict(conversions, conv_or_revenue, model)
    pickle_conversions(conversions_dict, model)
    
    
if __name__ == '__main__':
    if len(sys.argv) >= 4 and sys.argv[1] in ('conversoes', 'receita') and sys.argv[2] in \
            ('lc', 'sp', 'sf') and sys.argv[3] in ('frontend', 'backend'):
        main(sys.argv[1], sys.argv[2], f'{str(sys.argv[3]).title()}')
    else:
        print('Argumento(s) inválido(s).\nUso: python validar_assinaturas.py [conversoes/receita]'
              ' [lc/sp/sf] [frontend/backend]')
