import numpy as np
import fire

def calc_score(scalar, ratios):
    scaled = scalar * ratios
    return np.abs((scaled.round()-scaled)).sum()

def load_csv(filename):
    with open(filename, 'r') as fh:
        lines = [ f.split(',') for f in fh.read().strip().split()]
        keys = [line[0] for line in lines]
        values = np.array([float(line[1]) for line in lines])
        return keys, values

def process(filename, mins=100, maxs=2000, top=5):

    keys, ratios = load_csv(filename)
    scalars = np.arange(mins, maxs)

    results = [(scalar, calc_score(scalar, ratios)) for scalar in scalars]

    top = sorted(results, key=lambda k: k[1])

    print('target ratios')
    for k,r in enumerate(ratios):
        print(f' {keys[k]+":20"} {r:10.2f}')
    print()

    for k in range(5):
        scalar = top[k][0]
        scaled = scalar * ratios
        #score = f'{top[k][1]:.3f}'.rstrip('0').rstrip('.')
        score = top[k][1]
        print(f'rank: {k+1}')
        print(f' total:      {scalar:3}')
        print(f' error:      {score:5.3}')
        print(f' components:')
        for p,s in enumerate(scaled):
            print(f'  {keys[p]+":":20} {s:10.2f}')
        print()

if __name__ == '__main__':
    fire.Fire(process)
