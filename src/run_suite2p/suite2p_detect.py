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
from plotting import functions_plots 
from run_cascade import functions_data_transformation 

## import gui_configurations ##
from batch_process import gui_configurations as configurations


## Activate suite2p
from run_suite2p import run_suite2p 

configurations.data_extension = 'nd2'
configurations.main_folder = r'D:\users\JC\pipeline\HA processing xs\240619_DIV13_HA_culture'
# gui_configurations.data_extension = 'tif'
run_suite2p.main()
configurations.main_folder = r'D:\users\JC\pipeline\HA processing xs\240703_HA_Ambient_CO2_survival_imaging'
run_suite2p.export_image_files_to_suite2p_format(configurations.main_folder)
run_suite2p.main()

configurations.main_folder = r'D:\users\JC\pipeline\HA processing xs\240814_HA_DIV13_calcium_imaging'
run_suite2p.export_image_files_to_suite2p_format(configurations.main_folder)
run_suite2p.main()

# run_suite2p.export_image_files_to_suite2p_format(r'D:\users\JC\pipeline\cysteine toxicity\001-DMEM replicates\DMEM replicates\240322 DMEM high pH acute toxicity')
