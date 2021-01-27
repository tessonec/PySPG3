#!/usr/bin/env python3

import os, sys
import time
import logging

from spg.simulation import MultIteratorList
from spg.utils import SPGSettings
import spg
import optparse

import csv
import optparse


def parse_command_line():
    parser = optparse.OptionParser()

    parser.add_option("--repeat", action='store', dest="repeat", type='int',
                      default=1, help="number of repetitions to run")
#    parser.add_option("--workers", action='store', dest="workers", type='int',
#                      default=None, help="number of workers")
#    parser.add_option("--rewrite", action='store_true', dest="rewrite",
#                        help = "if the csv file - if existing - should be rewritten. If not added, append operation is performed" )

    options, args = parser.parse_args()

    return options, args




if __name__ == "__main__":

    options, args = parse_command_line()


    for arg in args:
        print(f"Processing '{arg}'...")
        mil = MultIteratorList(arg)

        ensemble = mil.generate_ensemble(all=True)
        total_combinations = len(ensemble)
        ensemble = options.repeat*ensemble
        print(f"     to execute '{mil.command}' -> {len(ensemble)} combinations ({total_combinations} in each repetition)")

        fout_ = open(f"{mil.base_name}_inputs.csv", "w")
        fout = csv.DictWriter(fout_, fieldnames=ensemble[0].keys())
        fout.writeheader()
        csv_header = mil.get_csv_header()

        for r in ensemble:
            fout.writerow(r)
        fout_.close()

        import pickle

        varying_parameters = mil.get_variables()
        pickle.dump((varying_parameters, csv_header), open(f"{mil.base_name}_configuration.pickle", "wb"))
#        pickle.dump(csv_header, open(f"{mil.base_name}_output_columns.pickle", "wb"))

        sys.exit()

