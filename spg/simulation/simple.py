import os.path
import sys

from .. import utils
from ..base import MultIteratorParser


class MultIteratorList(MultIteratorParser):
    # In this class:
    # - self.command     contains the name of the executed file (from which input and stdout are derived)
    # - self.base_name   contains the name of the simulation (iterated) parameters
    # - self.default_parameters is the dict (SPGSettings) of default values of all parameters
    # - self.input_configuration     is the dict (SPGSettings) of the input configuration
    # - self.stdout_configuration    is the dict (SPGSettings) of the output configuration
    # = self.names =     contains all variables in the right order
    # - varying_parameters = returns only the varying parameters

    def __init__(self, arg, command=None):

        full_name, self.path, self.base_name, extension = utils.translate_name(arg)

        MultIteratorParser.__init__(self, open(f"{self.base_name}.spg"))
        if command is not None:
            self.command = command

        self.command, ext = os.path.splitext(self.command)

        if not utils.check_params.consistency(self.command, self):
            utils.newline_msg("ERR", "simulation configuration is not consistent.")
            sys.exit(1)

        self.input_configuration = utils.read_input_configuration(
            f"{self.command}.input"
        )

        self.default_parameters = utils.SPGSettings()

        for k, v in self.input_configuration.items():

            if v.var_type != "str":
                self.default_parameters[k] = eval(f"{v.var_type}({v.default})")
            else:
                self.default_parameters[k] = v.default

        self.stdout_configuration = utils.read_output_configuration(self.command)

    #        print(self.names)
    #        print(self.stdout_contents)

    def generate_ensemble(self, all=False, repeat=None):
        # generates all possible combinations

        ret = [{j: self[j] for j in self.names} for i in self]

        if all:
            additional_values = {
                k: self.default_parameters[k]
                for k in self.default_parameters
                if k not in self.names
            }
            for _ in ret:
                _.update(additional_values)

        if repeat is not None:
            ret = repeat * ret

        return ret

    def get_csv_header(self, only_varying=True):
        if only_varying:
            return self.get_variables() + list(self.stdout_configuration.keys())
        else:
            return self.names + list(self.stdout_configuration.keys())

    def get_parameters(self, all=False):
        ret = utils.SPGSettings({j: self[j] for j in self.names})

        if all:
            additional_values = {
                k: self.default_parameters[k]
                for k in self.default_parameters
                if k not in self.names
            }

            ret.update(additional_values)
        return ret

    def get_row(self, return_values, only_varying=True):
        #        print(">>>>",  return_values)
        #        print(">>>>", self.stdout_configuration.keys())
        assert set(return_values.keys()) == set(self.stdout_configuration.keys())

        ret = return_values.copy()

        if only_varying:
            ret.update({_: self[_] for _ in self.get_variables()})
        #            return self.varying_parameters() + list(self.stdout_configuration.keys())
        else:
            ret.update({_: self[_] for _ in self.names})
        #            return self.names + list( self.stdout_configuration.keys() )

        return ret

    def __getitem__(self, name):
        """the values of the multiterator are supposed to be accessed
        only by the operator[] (or by the returned value of next()
        """
        #      print name, self.names
        #      if name == "id":
        #          return self.current_iteration_id

        assert name in self.input_configuration.keys(), (
            "the requested variable '%s' was not found in the multiterator" % name
        )
        ret = MultIteratorParser.__getitem__(self, name)
        #      print(ret, self.input_configuration[name])

        if self.input_configuration[name].var_type != "str":
            #          print(self.input_configuration[name].var_type)
            ret = eval(f"{self.input_configuration[name].var_type}({ret})")
        return ret
