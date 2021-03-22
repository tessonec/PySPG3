from spg.simulation import MultIteratorList
import os.path, time
from tqdm import tqdm
import concurrent.futures
import csv


class SingleRunner:


    def __init__(self, simulation, repeat = 1):
        self.fbase, fext= os.path.splitext(simulation)
        mil = MultIteratorList(simulation)
        self.simulation = simulation

        print(f"generating parameters for {simulation} ... ")
        self.parameters = mil.generate_ensemble(all=True, repeat= repeat)
        self.all_csv_fields = mil.get_csv_header()
        self.variables = mil.get_variables()

    def filter(self, s):
        s = s.replace("{", "_['").replace("}", "']")
        old_len = len(self.parameters)
        self.parameters = [_ for _ in self.parameters if eval(s)]
        print(f"   ... the parameter set was filtered from {old_len} to {len(self.parameters)} ")


    def run(self, run_simulation,workers= None):

        print(f"running {self.simulation} ... for {len(self.parameters)} iterations")
        start = time.perf_counter()

        if workers in {0,1}:
            self.results = [ run_simulation(el)  for el in tqdm(self.parameters) ]
        elif workers == None: # number of workers is not setup, so all resources are taken
            with concurrent.futures.ProcessPoolExecutor() as executor:
                self.results = list(
                    tqdm(
                        executor.map(run_simulation, self.parameters), total=len(self.parameters)
                    )
                )
        else:
            with concurrent.futures.ProcessPoolExecutor( max_workers=workers ) as executor:
                self.results = list(
                    tqdm(
                        executor.map(run_simulation, self.parameters), total=len(self.parameters)
                    )
                )
        finish = time.perf_counter()
        print(
            f".... run time: {round((finish - start), 2)} secs | {round((finish - start) / 60, 2)} minutes | {round((finish - start) / (60 * 60), 2)} hours"
        )

    def save_results(self, rewrite=False):

        if os.path.exists(f"{self.fbase}.csv") and not rewrite:
            writer = csv.DictWriter(open(f"{self.fbase}.csv", "a+"), fieldnames=self.all_csv_fields)
        else:
            writer = csv.DictWriter(open(f"{self.fbase}.csv", "w"), fieldnames=self.all_csv_fields)
            writer.writeheader()

        for (_p,_r) in zip(self.parameters, self.results):
            _o = _r.copy()
            for _v in self.variables:
                _o[_v] = _p[_v]
            writer.writerow(_o)

    def get_data(self, mean=False):

        import pandas as pd
        orecs = []
        for (_p,_r) in zip(self.parameters, self.results):
            _o = _r.copy()
            for _v in self.variables:
                _o[_v] = _p[_v]
            orecs.append( _o )

        df = pd.DataFrame.from_records(orecs)
        if mean:
            df = df.groupby(self.variables).mean().reset_index()


        return df

