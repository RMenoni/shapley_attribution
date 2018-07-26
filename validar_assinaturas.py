import pandas as pd
import numpy as np
import pickle
from collections import defaultdict

rejected_copies = set()
def copylist_to_writerlist(copy_list: str, copywriters: dict) -> str:
    copywriter_set = set()
    for copy in copy_list.split(','):
        copywriter: str = copywriters.get(copy, '')
        if copywriter != '':
            copywriter_set.add(copywriter)
        else:
            rejected_copies.add(copy)
    return ','.join(sorted(copywriter_set))


def get_copywriters_and_paidsubs() -> (dict, defaultdict):
    with open('copywriters.pickle', 'rb') as file:
        copywriters = pickle.load(file)
    with open('paid_subs.pickle', 'rb') as file:
        from collections import defaultdict
        paid_subs = defaultdict(float, pickle.load(file))
    return copywriters, paid_subs


def pickle_conversions(conversions: dict):
    with open('conversion_groups.pickle', 'wb') as file:
        pickle.dump(conversions, file)
    print('Sucesso')


def main():
    conversions = pd.read_csv('conversions2017.csv')
    conversions = conversions.drop(columns='Number of Records')
    copywriters, paid_subs = get_copywriters_and_paidsubs()
    # adicionar coluna 'Writer List' com os copywriters
    conversions['Writer List'] = conversions['Copy List'].apply(lambda x: copylist_to_writerlist(str(x), copywriters))
    # eliminar as conversões não pagas
    conversions['Valor'] = conversions['Assinatura'].apply(lambda x: paid_subs[x])
    conversions = conversions[conversions['Valor'] > 0]
    conversions = conversions[conversions['Fantasma']].groupby('Writer List').sum().to_dict()['Valor']
    del conversions['']
    pickle_conversions(conversions)
    
    
if __name__ == '__main__':
    main()
    