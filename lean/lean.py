from pathlib import Path
import arrow
import pygal
import shutil
import json
import fire
import math
from dateutil import tz
import sys

TZ = 'US/Eastern'
tz = tz.gettz(TZ)

time_format = 'YYYY-MM-DD-HH-mm-ss'
date_format = 'YYYY-MM-DD'

def get_timestamp():
    return arrow.utcnow().to(TZ).format(time_format)

def get_datestamp():
    return arrow.utcnow().to(TZ).format(date_format)

def date_to_str(date):
    return date.format(date_format)

def str_to_date(string):
    return arrow.get(string).replace(tzinfo=tz)

class Lean:

    def __init__(self):

        script_dir = Path(__file__).absolute().parent
        backup_dir = script_dir / '.bak'
        backup_fn = backup_dir / f'lean-{get_timestamp()}.json'
        self.data_fn = script_dir / 'lean.json'
        
        if not backup_dir.exists():
            backup_dir.mkdir()

        if self.data_fn.exists():
            shutil.copyfile(self.data_fn, backup_fn)
            with self.data_fn.open('r') as fh:
                data = json.load(fh)
                self.load(data)
        else:
            self.samples = []
            self.rate = 1
            self.target = 0

        self.save()

    def load(self, data):

        self.samples = [{ 
            'date' : str_to_date(d['date']),
            'weight' : float(d['weight'])
            } 
            for d in data['samples'] ]
        
        self.rate = float(data['rate'])
        self.target = float(data['target'])

    def save(self):

        samples = [
            { 'date' : date_to_str(d['date']), 'weight' : d['weight'] }
            for d in self.samples ]
        
        data = {
            'samples' : samples,
            'rate' : self.rate,
            'target' : self.target
        }

        with self.data_fn.open('w') as fh:
            json.dump(data, fh, sort_keys=True, indent=4)

    def set_target(self, target, rate):

        target = float(target)
        rate = float(rate)

        print(f'setting target: {target}, rate: {rate}')

        if target < 0 or rate <= 0:
            raise ValueError('target must be >= 0, rate > 0')
        
        self.target = target
        self.rate = rate

        self.save()

    def insert(self, weight, date=None):

        if date is None:
            date = get_datestamp()
           
        # make sure its a valid datetime
        date = str_to_date(date)

        print(f'inserting {weight}lbs on {date}')

        self.samples.append({
            'date' : date,
            'weight' : float(weight)
        })

        self.save()

    def plot(self, target=None, rate=None):

        target = self.target if target is None else target
        rate = self.rate if rate is None else rate

        if len(self.samples) == 0:
            print('no samples to plot')
            sys.exit(1)

        pds = [ s['date'] for s in self.samples ]
        pws = [ s['weight'] for s in self.samples ]
   
        pdsi, pwsi = pds[0], pws[0]

        days = math.ceil((pwsi - target) / rate)

        tws = [(pwsi - k * rate) for k in range(days+1)]
        tds = [pdsi.shift(days=k) for k in range(len(tws))]

        pds = [ d.timestamp() for d in pds ]
        tds = [ d.timestamp() for d in tds ]

        psamples = list(zip(pds, pws))
        tsamples = list(zip(tds, tws))
      
        chart = pygal.DateLine(x_label_rotation=45, show_dots=False)
        chart.add('progress', psamples)
        chart.add('target', tsamples)

        chart.title = 'progress'
        chart.x_title = 'time'
        chart.y_title = 'weight'

        chart.render_to_file('./lean.svg')

if __name__ == '__main__':
    fire.Fire(Lean)


