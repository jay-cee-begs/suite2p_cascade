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
# from functions_general import *
# from CASCADE_functions import *
# from plotting.functions_plots import *
# from functions_data_transformation import *


## import configurations ##


"""Activate cascade env"""
from batch_process import gui_configurations as configurations
from run_cascade import run_cascade_script
from plotting.functions_plots import *
if __name__ == "__main__":
    run_cascade_script.main()

configurations.groups

