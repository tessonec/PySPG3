#!/usr/bin/env python3

from model import CascadeWattsModel
import networkx as nx
import sys

import numpy as np
import math as m
import numpy.random as nprnd

from tqdm import tqdm
import csv, time, optparse
import concurrent.futures






def parse_command_line():

    parser = optparse.OptionParser()

    parser.add_option("--workers", action='store', dest="workers", type='int',
                      default=None, help="number of workers")
    parser.add_option("--rewrite", action='store_true', dest="rewrite",
                        help = "if the csv file - if existing - should be rewritten. If not added, append operation is performed" )

    command = sys.argv[0]
    options, args = parser.parse_args()

    return command, options, args


def run_simulation(_p):
    # The argument to this function is a dictionary with the parameter values

    no_agents = _p["no_agents"]

    amean = _p["threshold_mean"]
    astd = _p["threshold_std"]
    if _p["threshold_distribution"] == "uniform":
        threshold_vec = nprnd.uniform(amean - m.sqrt(3) * astd, amean + m.sqrt(3) * astd,no_agents)
    elif _p["threshold_distribution"] == "normal":
        threshold_vec = nprnd.normal(amean, astd, no_agents)


    topology  = _p['network_topology']


    if topology == "erdos_renyi":
        p = _p["network_er_p"]
        net_p2p = nx.fast_gnp_random_graph(no_agents, p)

    elif topology == "barabasi_albert":
        ba_m = _p["network_ba_m"]
        net_p2p = nx.barabasi_albert_graph(no_agents, ba_m)


    model = CascadeWattsModel(_p["no_agents"], net_p2p , threshold_vec)
    model.initalise_agents( _p['p0'])

    while not model.in_equilibrium:
        model.iterate()

    _o = {}
    _o['cascade_size'] = model.get_cascade_size()
    _o['convergence_time'] = model.time



    # add exogenous data to data_point
    for i in variables:
        _o[i] = _p[i]

    return _o


##############################################################################
#### RUN MULTIPROCESS SIMULATION #############################################

import csv, os, os.path, pickle
import pandas as pd

command, options, args = parse_command_line()


start = time.perf_counter()
for arg in args:

    fbase, fext= os.path.splitext(arg)

    dr = pd.read_csv(f'{fbase}_inputs.csv')
    parameter_list = dr.to_dict('records')


    print(f"running {arg} ... for {len(parameter_list)} iterations")



    (variables,all_csv_fields)  = pickle.load(open(f"{fbase}_configuration.pickle","rb"))
#        = pickle.load(open(f"{fbase}_output_columns.pickle","rb"))

    if os.path.exists(f"{fbase}.csv") and not options.rewrite:
        writer = csv.DictWriter(open(f"{fbase}.csv", "a+"), fieldnames=all_csv_fields)
    else:
        writer = csv.DictWriter(open(f"{fbase}.csv", "w"), fieldnames=all_csv_fields)
        writer.writeheader()

#
    start = time.perf_counter()

    if options.workers in {0,1}:

        for el in tqdm(parameter_list):
            _r = run_simulation(el)
            writer.writerow(_r)


    elif options.workers == None: # number of workers is not setup, so all resources are taken
        with concurrent.futures.ProcessPoolExecutor() as executor:
            results = list(
                tqdm(
                    executor.map(run_simulation, parameter_list), total=len(parameter_list)
                )
            )
        for _r in results:
            writer.writerow(_r)
    else:
        with concurrent.futures.ProcessPoolExecutor( max_workers=options.workers ) as executor:
            results = list(
                tqdm(
                    executor.map(run_simulation, parameter_list), total=len(parameter_list)
                )
            )
        for _r in results:
            writer.writerow(_r)




finish = time.perf_counter()
print(
    f"Run time: {round((finish-start),2)} secs | {round((finish-start)/60,2)} minutes | {round((finish-start)/(60*60),2)} hours"
)


