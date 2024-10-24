import pandas as pd

from configurations import main_folder, TimePoints, Groups22, pairs, parameters
from functions_plots import *
from statannotations.Annotator import Annotator
from jd_plot_functions import ez_sign_plot, load_and_adjust



##Dictionaries and lists
# TimePoints = {
#     'ACS' : 'ACSF',
#     'NBA': 'NBA',
#     'NaO': 'NaOH'
# }

# Groups22 ={
#     'ACSF_baseline' : 'Baseline',
#     'ACSF_GBZ' : 'GBZ',
#     'ACSF_TTX' : 'TTX',
#     'NBA_baseline' : 'Baseline',
#     'NBA_GBZ' : 'GBZ',
#     'NBA_TTX' : 'TTX',
#     'NaOH_baseline' : 'Baseline',
#     'NaOH_GBZ' : 'GBZ',
#     'NaOH_TTX' : 'TTX'
#     }

#filepath = main_folder + r'\new_experiment_summary.csv'
# pairs = [('Baseline', 'GBZ'), ('Baseline', 'TTX')]



df2 = load_and_adjust(TimePoints, Groups22) #run once but only once since it cant edit the already edited df
s1 = ez_sign_plot(df=df2, **parameters)  # Added pairs here

plt.show(s1)
