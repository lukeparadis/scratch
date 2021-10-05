import numpy as np
import fire

def calc_quantities(scalars, ratios):

    results = []

    for scalar in scalars:
        scaled = scalar * ratios
        values = scaled.round().astype('int')
        errors = scaled - values
        error = np.abs(errors).sum()
        results.append({
            'error' : error,
            'pct_error' : 100*error / scalar,
            'values' : values,
            'errors' : errors,
            'scalar' : scalar,
        })

    return sorted(results, key=lambda k: k['error'])

def load_csv(filename):
    with open(filename, 'r') as fh:
        lines = [ f.split(',') for f in fh.read().strip().split()]
        keys = [line[0] for line in lines]
        values = np.array([float(line[1]) for line in lines])
        return keys, values

def process(filename, mins=100, maxs=2000, deltas=1, top=5):

    keys, ratios = load_csv(filename)

    if type(deltas) != int or type(mins) != int or type(maxs) != int:
        print(f'mins: {mins}, maxs: {maxs}, deltas: {deltas} must all be int')
        sys.exit(1)

    scalars = np.arange(mins, maxs+deltas, deltas)
    results = calc_quantities(scalars, ratios)

    print('target ratios')
    for k,key in enumerate(keys):
        print(f' {key:20} {ratios[k]:10.5f}')
    print()

    for k in range(top):
        print(f'rank: {k+1}')
        print(f' total:      {results[k]["scalar"]:5}')
        print(f' error:      {results[k]["error"]:5.3}')
        print(f' pct error:  {results[k]["pct_error"]:5.3f}')
        print(f' components:')
        for c,key in enumerate(keys):
            value = results[k]['values'][c]
            error = results[k]['errors'][c]
            print(f'  {key+":":20} {value:3}  ({error:5.2f})')
        print()

if __name__ == '__main__':
    fire.Fire(process)
