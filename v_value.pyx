import numpy as np
cimport numpy as cnp
from itertools import combinations
from libcpp.string cimport string
DTYPE = np.unicode_

cpdef list subseq_list(list seq):
    cdef int n = len(seq)
    cdef int i, j
    cdef list combos
    cdef list all_subseq = []
    for i in range(1, n+1):
        combos = list(combinations(seq, i))
        for j in range(0, len(combos)):
            all_subseq.append(','.join(sorted(combos[j])))
    return all_subseq
    

def subseq(list seq) -> generator:
    cdef int n = len(seq)
    cdef int i
    cdef tuple s
    for i in range(1, n+1):
        for s in itertools.combinations(seq, i):
            yield ','.join(sorted(s))


cdef int v_function_count = 0
cdef dict C_values
cpdef int v_function(A):
    global v_function_count
    v_function_count += 1
    if v_function_count % 10000 == 0:
        print(v_function_count)
    cdef int worth_of_A = 0
    cdef str subset
    for subset in subseq(A.split(',')):
        if subset in C_values.keys():
            worth_of_A += C_values[subset]
    return worth_of_A


cpdef dict get_v_values(list channels, dict conversions):
    import os.path
    import pickle
    cdef str filename = 'v_values.pickle'
    if os.path.isfile(filename):
        with open(filename, 'rb') as file:
            return pickle.load(file)
    cdef cnp.ndarray all_subseq = np.array(subseq_list(channels))
    cdef cnp.ndarray v_values_array = np.zeros(2**len(channels)-1)
    global C_values
    C_values = conversions
    vector_v_function = np.vectorize(v_function)
    v_values_array = vector_v_function(all_subseq)
    cdef int i
    cdef dict v_values = {}
    for i in range(v_values_array.size):
        v_values[all_subseq[i]] = v_values_array[i]
    with open(filename, 'wb') as file:
        pickle.dump(v_values, file)
    return v_values
