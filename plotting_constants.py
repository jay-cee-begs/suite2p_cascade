import pandas as pd
from gui_configurations import *
from gui_configurations import main_folder, parameters, TimePoints, Groups22
from functions_plots import *
from statannotations.Annotator import Annotator
from jd_plot_functions import ez_sign_plot, load_and_adjust



df2 = load_and_adjust(TimePoints, Groups22) #run once but only once since it cant edit the already edited df
s1 = ez_sign_plot(df2, **parameters)  # Added pairs here

plt.show(s1)