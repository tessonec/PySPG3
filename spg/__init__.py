version_number   = '5.0.0'
database_version = '2.0'
release_date = '04 Dec 2020'

from .base.iterator import *
from .base.parser   import *
from .simulation.simple import *
from .runner.single import *


import os.path

#SPG_HOME = os.path.expanduser("~/opt/lib")


#ROOT_DIR = os.path.expanduser("~/opt")

CONFIG_DIR = os.path.expanduser("~/.pyspg")
#VAR_PATH = os.path.abspath(CONFIG_DIR+"/spool")
#BINARY_PATH = os.path.abspath(ROOT_DIR+"/bin")
# RUN_DIR = os.path.expanduser("~/run")

TIMEOUT = 120


class ValueContainer(dict):
    # :::~ class that allows to take the values as items
    # :::~ http://stackoverflow.com/questions/1325673/python-how-to-add-property-to-a-class-dynamically
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __str__(self):
        ret = ":\n"
        for k in self.keys():
            ret += "%s = %s\n" % (k, self[k])
        return ret
