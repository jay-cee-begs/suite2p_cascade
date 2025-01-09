#Manual Mode
import os, warnings
import sys
import glob
import numpy as np
import scipy.io as sio
import ruamel.yaml as yaml
yaml = yaml.YAML(typ='rt')
#%matplotlib widget # can be commented back in to make plots interactive
import pandas as pd
import seaborn as sns
import scipy.stats as stats
import pickle
## import functions ##
from run_cascade import functions_general
from run_cascade import CASCADE_functions
from plotting.functions_plots import *
from run_cascade import functions_data_transformation


## import configurations ##
import configurations

"""Activate cascade env"""
from batch_process import gui_configurations as configurations
from plotting import functions_plots as fun_plots

"""Activate cascade env"""
from run_cascade import run_cascade_script
from plotting import networkx_functions

if __name__ == "__main__":
    run_cascade_script.main()
    networkx_functions.main()


