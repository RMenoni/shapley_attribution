import numpy as np
cimport numpy as cnp
import itertools
import os.path
import pickle
DTYPE_FLOAT = np.float64
ctypedef cnp.float64_t DTYPE_FLOAT_t
    
    
def unpickle_values():
    with open('v_values.pickle', 'rb') as file:
        return pickle.load(file)
    
    
def subseq(list seq) -> generator:
    """ Gerador de todas as subcombinacoes de uma sequencia (exceto a sequencia vazia)
    
    :param seq: combinacao de copywriters, separado por virgulas
    :return: iterador de todas as subsequencias
    """
    cdef int n = len(seq)
    cdef int i
    cdef tuple s
    for i in range(1, n+1):
        for s in itertools.combinations(seq, i):
            yield ','.join(sorted(s))

            
cdef int g_count = 0
cdef dict g_conversions
cpdef double v_function(combo):
    """ Soma todas as conversoes geradas pela combinacao de writers combo e suas subcombinacoes
    
    :param combo: lista de writers
    :return: conversoes geradas por todas as subcombinacoes de combo
    """
    global g_count
    g_count += 1
    if g_count % 10000 == 0:
        print(g_count)
    cdef double worth_of_combo = 0
    cdef str subset
    for subset in subseq(combo.split(',')):
        if subset in g_conversions.keys():
            worth_of_combo += g_conversions[subset]
    return worth_of_combo


cpdef dict get_v_values(set writers, dict conversions):
    """ Cria um dicionario com todas as combinacoes possiveis de writers e seus 'v_values'
    
    :param writers: conjunto de todos os copywriters
    :param conversions: dicionario de chaves combinacao de writers e valores conversoes
    :return: dicionario com todas as combinacoes e a soma das conversoes de todas suas subcombinacoes
    """
    if os.path.isfile('v_values.pickle'):
        return unpickle_values()
    cdef cnp.ndarray all_subseq = np.array(list(subseq(list(writers))))
    cdef cnp.ndarray[DTYPE_FLOAT_t] v_values_array = np.zeros(2**len(writers)-1, dtype=DTYPE_FLOAT)
    global g_conversions
    g_conversions = conversions
    vector_v_function = np.vectorize(v_function)
    v_values_array = vector_v_function(all_subseq)
    cdef dict v_values = dict(zip(all_subseq, v_values_array))
    with open('v_values.pickle', 'wb') as file:
        pickle.dump(v_values, file)
    return v_values
