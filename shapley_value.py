"""
    Calcula os valores Shapley
"""


import v_value
import pickle, os, datetime, time, sys
from collections import defaultdict
from math import factorial
from pprint import pprint


def unpickle(filename: str) -> dict:
    if not os.path.isfile(filename):
        return None
    with open(filename, 'rb') as file:
        return pickle.load(file)


def pickle_dict(p_dict: dict, filename: str):
    with open(filename, 'wb') as file:
        pickle.dump(p_dict, file)


def get_writers(conversions: dict) -> set:
    """ Cria conjunto de copywriters a partir do dicionario de conversoes

    :param conversions: dicionario de chaves combinacao de writers e valores conversoes/receita
    :return: conjunto de copywriters
    """
    writers: set = set()
    for k in conversions.keys():
        for writer in k.split(','):
            writers.add(writer)
    print(writers)
    return writers


def make_or_get_v_values(writers: set, conversions: dict, model: str, conv_or_revenue: str, category: str):
    """ Chama a função get_v_values ou extrai os valores de um pickle se já existe

    :param writers: conjunto de copywriters
    :param conversions: dicionário de conversões
    :param model: 'sp'/'sf'
    :param conv_or_revenue: 'conversoes'/'receita'
    :param category: 'frontend'/'backend'
    :return: dicionário de conversões/receita de todas as combinações de copywriters
    """
    filename: str = f'v_values_{model}_{conv_or_revenue}_{category}.pickle'
    v_values: dict = unpickle(filename)
    if v_values is None:
        v_values = v_value.get_v_values(writers, conversions)
        pickle_dict(v_values, filename)
    return v_values


def shapley(writers: set, v_values: dict) -> dict:
    """ Aplica a formula Shapley (primeira na pagina https://en.wikipedia.org/wiki/Shapley_value)

    :param writers: lista de copywriters
    :param v_values: dicionario com chaves combinacao de copywriters e valores conversoes/receita
    gerados
    :return: dicionario com chaves copywriters e valores valores shapley (conversao/receita)
    """
    n: int = len(writers)
    shapley_dict = defaultdict(float)
    count: int = 0
    for writer in writers:
        #if writer == '':
        #    continue
        count += 1
        print(f'writer {count} of {n}')
        for combo in v_values.keys():
            combo_arr: list = combo.split(',')
            if writer not in combo_arr:
                cardinal_combo: int = len(combo_arr)
                combo_with_writer: list = combo_arr
                combo_with_writer.append(writer)
                combo_with_writer: str = ','.join(sorted(combo_with_writer))
                shapley_dict[writer] += (v_values[combo_with_writer] - v_values[combo]) * \
                                        (factorial(cardinal_combo)*factorial(n-cardinal_combo-1) /
                                         factorial(n))
        shapley_dict[writer] += v_values[writer] / n
    #shapley_dict[''] = v_values['']
    return shapley_dict


def main(model: str, conv_or_revenue: str, category: str):
    shapley_filename: str = f'shapley_{model}_{conv_or_revenue}_{category}.pickle'
    shapley_vals = unpickle(shapley_filename)
    if shapley_vals is None:   
        start_time: float = time.time()
        conversions: dict = unpickle(f'conversion_groups_{model}_{conv_or_revenue}_{category}.pickle')
        writers: set = get_writers(conversions)
        print(sum(conversions.values()))
        v_values: dict = make_or_get_v_values(writers, conversions, model, conv_or_revenue, category)
        shapley_vals: dict = shapley(writers, v_values)
        pickle_dict(shapley_vals, shapley_filename)
        print(f'Duração: {datetime.timedelta(seconds=time.time()-start_time)}')
    sorted_res: list = sorted(shapley_vals.items(), key=lambda kv: kv[1])
    pprint(sorted_res)
    print(sum(shapley_vals.values()))

    
if __name__ == '__main__':
    if len(sys.argv) < 4 or sys.argv[1] not in ('sp', 'sf') or sys.argv[2] not in \
            ('conversoes', 'receita') or sys.argv[3] not in ('frontend', 'backend'):
        print('Argumento inválido.\nUso: python shapley_value.py [sp/sf] [conversoes/receita]'
              ' [frontend/backend]')
    else:
        main(sys.argv[1], sys.argv[2], sys.argv[3])
