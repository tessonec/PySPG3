'''
Created on 12 Apr 2014

@author: tessonec
'''

import spg.plot as spgp
import spg.base as spgb
import spg.utils as spgu


import pandas as pd
import numpy as np
import math as m



import os.path





from spg import CONFIG_DIR

# from spg.utils import newline_msg, evaluate_string, load_configuration




class DataFrameIterator:

    def __init__(self, df, filter = [] ):
        self.data = df
        self.filter = filter

    def __iter__(self):
        if len(self.filter) > 0:
            df_coalesced = self.data.groupby(self.filter)

            for minimal_gr in sorted(df_coalesced.groups):
                minimal_idx = df_coalesced.groups[minimal_gr]
                minimal_df = self.data.loc[minimal_idx]

                yield minimal_df

        else:
            yield self.data


from spg.plot import DataFrameIterator

class BaseDataLoader:

    def describe_variables(self):
        for v in self.variables:
            red_d = self.data[ v ].unique()
            print("%-16s: %4s values || %s -- %s"%(v, len(red_d), min(red_d), max(red_d) ))


    def describe_configuration(self):
        print("variables      : %s"%( ", ".join(self.variables ) ))
        print("  + separated  : %s"%(self.separated_vars))
        print("  + coalesced  : %s"%(self.coalesced_vars))
        print("  + independent: %s"%(self.independent_var))
        print("output columns : %s "%( ", ".join(self.output_columns) ))




    def setup_output_columns(self, oc):
        self.output_columns = oc
        self.data = self.full_dataframe[self.variables + self.output_columns]

    #

    def get_separated_values(self):

        ret = []
        for outer_df in DataFrameIterator(self.data, self.separated_vars):
            ret.append( [ outer_df[v].unique()[0] for v in self.separated_vars ] )
        return ret

    def get_coalesced_values(self):

        ret = []
        for inner_df in DataFrameIterator(self.data, self.coalesced_vars):
            ret.append( [ inner_df[v].unique()[0] for v in self.coalesced_vars ] )

        return ret


class SPGDataLoader(BaseDataLoader):
    """
     A class that constructs the plots.
     It exposes
     self.parameter_file: spg file name
     self.base_name:
     self.datafile_name:

     self.simulation: the MultIterator that describes the simulation

     self.full_dataframe : ALl the data in the table
     self.variables
     self.constants
    """

    def __init__(self, simulation_filename):

        full_name, self.path, self.base_name, extension = spgu.translate_name(simulation_filename)
        self.simulation = spgb.MultIteratorParser(open(f"{self.base_name}.spg"))
        self.datafile_name = "%s.csv"%(self.base_name)

        self.full_dataframe = pd.read_csv(self.datafile_name)

        settings_output = self.simulation.stdout_configuration
        self.output_columns = list( settings_output.keys() )

        self.constants = {}
        self.variables = []
        for vn in list(self.full_dataframe.keys()):
            if vn in self.output_columns:
                continue
            all_values = self.full_dataframe[vn].unique()
            if len(all_values) > 1:
                self.variables.append(vn)
            else:
                self.constants[vn] = self.full_dataframe[vn].unique()[0]


        self.settings = self.simulation.input_configuration

        self.settings.update(settings_output)


        self.data = self.full_dataframe[self.variables + self.output_columns]

        print("[__init__] constants: %s"% list(self.constants.keys()))
        print("[__init__] independent variables:", self.separated_vars, self.coalesced_vars, self.independent_var)
        print("[__init__] output columns: %s"% self.output_columns)



    def mean(self):
        self.data = self.data.groupby(self.separated_vars + self.coalesced_vars + [self.x_axis]).mean().reset_index()

    def std(self):
        self.data = self.df.groupby(self.separated_vars + self.coalesced_vars + [self.x_axis]).std().reset_index()

