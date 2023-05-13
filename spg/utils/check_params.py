#!/usr/bin/env python3

import copy
import os.path

from .load_configs import *
from .tools import evaluate_string, newline_msg

# from math import *


# from spg import CONFIG_DIR


############################################################################################################
############################################################################################################
############################################################################################################
############################################################################################################
############################################################################################################
############################################################################################################
############################################################################################################
############################################################################################################
############################################################################################################
############################################################################################################
############################################################################################################
############################################################################################################


def consistency(exec_file, miparser):
    """Checks the consistency of a spg simulation file"""
    consistent_param = True

    # if exec_file[:2] == "ct" and exec_file[3] == "-" :  exec_file = exec_file[4:]

    exec_file, ext = os.path.splitext(exec_file)

    #    try:
    possible_lines = read_input_configuration("%s.input" % (exec_file))
    # except:
    #    possible_lines = read_input_configuration("%s/spg-conf/%s.input" % (CONFIG_DIR, exec_file))

    assert (
        len(set(miparser.names) - set(possible_lines.keys())) == 0
    ), "not all the variables are recognised: offending vars: %s" % (
        set(miparser.names) - set(possible_lines.keys())
    )
    #  print(possible_lines)
    #  print(miparser.data)

    for el in miparser.data:
        #    print el.name,
        it = copy.copy(el)
        pc = possible_lines[it.name]
        #      print(pc)
        #   print  family, var_type, default,
        #        print it.name
        values = [i for i in it]
        if len(values) == 0:
            values = it.data
        for val in values:
            if pc.family == "choice" and str(val) not in pc.categories:
                newline_msg(
                    "VAL",
                    "choice value '%s' not recognised: possible values: %s"
                    % (val, pc.categories),
                )
                consistent_param = False
            elif pc.var_type == "str":
                try:
                    str(f"{pc.var_type}({evaluate_string(val, miparser)})")
                except:
                    newline_msg(
                        "VAL",
                        f"wrong type for '{it.name}' expected '{pc.var_type}' ",
                    )
                    consistent_param = False

            elif pc.var_type in {"float", "int", "bool"}:  # in set(["float","double"]):
                #    print it.name, var_type, val, evaluate_string(val, miparser)
                try:
                    eval(f"{pc.var_type}({evaluate_string(val, miparser)})")
                except:
                    newline_msg(
                        "VAL",
                        f"wrong type for '{it.name}' expected '{pc.var_type}' ",
                    )
                    consistent_param = False

    return consistent_param


# d = {'x':pi,'y_3':1}

# v = string_evaluator("exp({x}+{y_3})",d)
# print get_variables("exp({x}+{y_3})",d)
##st='/home/tessonec/running/alpha_max_20312_3424-0.5_size-100/beta-324.3242_gamma--90.2E-4.234_fjs-1E-4.dat'

# print st
# print parameterGuess(st)
