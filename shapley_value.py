import v_value
import pickle, os, datetime, time
from collections import defaultdict
from math import factorial


def unpickle_shapley() -> dict:
    filename = 'shapley.pickle'
    if os.path.isfile(filename):
        with open(filename, 'rb') as file:
            return pickle.load(file)
    return None    


def pickle_shapley(shapley_values: dict):
    filename = 'shapley.pickle'
    with open(filename, 'wb') as file:
        pickle.dump(shapley_values, file)


def shapley(channels: list, v_values: dict) -> dict:
    n: int = len(channels)
    res = defaultdict(float)
    count: int = 0
    for channel in channels:
        count += 1
        print(f'channel {count} of {n}')
        for A in v_values.keys():
            A_arr = A.split(',')
            if channel not in A_arr:
                cardinal_A = len(A_arr)
                A_with_channel = A_arr
                A_with_channel.append(channel)
                A_with_channel = ','.join(sorted(A_with_channel))
                res[channel] += (v_values[A_with_channel] - v_values[A])*(factorial(cardinal_A)*factorial(n-cardinal_A-1)/factorial(n))
        res[channel] += v_values[channel] / n
    return res


def main():
    shapley_vals = unpickle_shapley()
    if shapley_vals is None:   
        start_time: float = time.time()
        with open('conversion_groups_sp.pickle', 'rb') as file:
            C_values: dict = pickle.load(file)
        channels: list = sorted([c for c in C_values.keys() if ',' not in c])
        print(sum(C_values.values()))
        v_values: dict = v_value.get_v_values(channels, C_values)
        shapley_vals: dict = shapley(channels, v_values)
        end_time: float = time.time()
        pickle_shapley(shapley_vals)
    sorted_res = sorted(shapley_vals.items(), key=lambda kv: kv[1])
    from pprint import pprint
    pprint(sorted_res)
    print(sum(shapley_vals.values()))
    if 'end_time' in locals():
        print(f'Duração: {datetime.timedelta(seconds=end_time-start_time)}')

    
if __name__ == '__main__':
    main()
