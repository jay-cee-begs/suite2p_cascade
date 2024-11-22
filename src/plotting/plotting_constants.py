import pandas as pd
import batch_process.gui_configurations as gui_configurations
from batch_process.gui_configurations import main_folder, parameters, TimePoints, exp_condition 
#from functions_plots import *
from statannotations.Annotator import Annotator
from plotting.jd_plot_functions import ez_sign_plot, load_and_adjust
import importlib # to reload the gui_configurations file

# Reload the gui_configurations module to ensure changes are picked up
importlib.reload(gui_configurations)
parameters = gui_configurations.parameters
#print(f"Loaded parameters: {parameters}")  # Debugging statement


df2 = load_and_adjust(TimePoints, exp_condition) #run once but only once since it cant edit the already edited df

s1 = ez_sign_plot(df2,  **parameters)  # Added pairs here




