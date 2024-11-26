import pandas as pd
#from functions_plots import *
from statannotations.Annotator import Annotator
from plotting import jd_plot_functions as stat_plot 
import importlib # to reload the gui_configurations file
from batch_process import gui_configurations as configurations 

# Reload the gui_configurations module to ensure changes are picked up
importlib.reload(configurations)
parameters = configurations.parameters
#print(f"Loaded parameters: {parameter s}")  # Debugging statement


df2 = stat_plot.load_and_adjust(configurations.TimePoints, configurations.exp_condition) #run once but only once since it cant edit the already edited df

s1 = stat_plot.ez_sign_plot(df2,  **parameters)  # Added pairs here




 