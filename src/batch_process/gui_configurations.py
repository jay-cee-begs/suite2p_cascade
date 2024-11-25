import numpy as np 
main_folder = r'D:/241104_DIV0_vacuum_test_withGCaMP/plate01_HA_plate02_NBA_ACSF'
group1 = main_folder + r'C:/Users/Justus/data/test_data_binned\ACSF_baseline'
group2 = main_folder + r'C:/Users/Justus/data/test_data_binned\ACSF_GBZ'
group3 = main_folder + r'C:/Users/Justus/data/test_data_binned\NaOH_baseline'
group4 = main_folder + r'C:/Users/Justus/data/test_data_binned\NaOH_GBZ'
group5 = main_folder + r'C:/Users/Justus/data/test_data_binned\NBA_baseline'
group6 = main_folder + r'C:/Users/Justus/data/test_data_binned\NBA_GBZ'
group7 = main_folder + r'\ACSF74_base'
group8 = main_folder + r'\ACSF74_GBZ'
group9 = main_folder + r'\ACSF74_TTX'
group10 = main_folder + r'\ACSF78_base'
group11 = main_folder + r'\ACSF78_GBZ'
group12 = main_folder + r'\ACSF78_TTX'
group13 = main_folder + r'\HA_base'
group14 = main_folder + r'\HA_cys_base'
group15 = main_folder + r'\HA_cys_FBS_base'
group16 = main_folder + r'\HA_cys_FBS_GBZ'
group17 = main_folder + r'\HA_cys_FBS_TTX'
group18 = main_folder + r'\HA_cys_GBZ'
group19 = main_folder + r'\HA_cys_TTX'
group20 = main_folder + r'\HA_GBZ'
group21 = main_folder + r'\HA_TTX'
group22 = main_folder + r'\NBA_base'
group23 = main_folder + r'\NBA_GBZ'
group24 = main_folder + r'\NBA_TTX'
group_number = 24
data_extension = 'nd2'
frame_rate = 10
cascade_file_path = r''
ops_path = r'C:\Users\Justus\data\test_data_binned\qm2.npy'
ops = np.load(ops_path, allow_pickle=True).item()
ops['frame_rate'] = frame_rate
ops['input_format'] = data_extension
BIN_WIDTH = 20
EXPERIMENT_DURATION = 60
FRAME_INTERVAL = 1 / frame_rate
FILTER_NEURONS = True
TimePoints = {
    'HA_': 'HA_',
    'NBA': 'NBA',
    'ACS': 'ACS',
    'NaO': 'NaO',
}
exp_condition = {
    'ACSF74_base': 'ACSF74_base',
    'ACSF74_GBZ': 'ACSF74_GBZ',
    'ACSF74_TTX': 'ACSF74_TTX',
    'ACSF78_base': 'ACSF78_base',
    'ACSF78_GBZ': 'ACSF78_GBZ',
    'ACSF78_TTX': 'ACSF78_TTX',
    'HA_base': 'HA_base',
    'HA_cys_base': 'HA_cys_base',
    'HA_cys_FBS_base': 'HA_cys_FBS_base',
    'HA_cys_FBS_GBZ': 'HA_cys_FBS_GBZ',
    'HA_cys_FBS_TTX': 'HA_cys_FBS_TTX',
    'HA_cys_GBZ': 'HA_cys_GBZ',
    'HA_cys_TTX': 'HA_cys_TTX',
    'HA_GBZ': 'HA_GBZ',
    'HA_TTX': 'HA_TTX',
    'NBA_base': 'NBA_base',
    'NBA_GBZ': 'NBA_GBZ',
    'NBA_TTX': 'NBA_TTX',
}
pairs = [ ('Baseline', 'GBZ'), ('Baseline', 'TTX') ]
parameters = {
    'testby': pairs,
    'feature': ['Active_Neuron_Proportion', 'Total_Estimated_Spikes_proportion_scaled'],
    'x': 'Group',
    'type': 'violin',
    'plotby': 'Time_Point',
    'y_label': 'y label',
    'x_label': '',
    'stat_test': 'Mann-Whitney',
    'legend': 'auto',
    'location': 'outside',
    'palette': 'viridis',
}
## Additional configurations
nb_neurons = 16
model_name = "Global_EXC_10Hz_smoothing200ms"
FILTER_NEURONS = True
groups = []
for n in range(group_number):
    group_name = f"group{n + 1}"
    if group_name in locals():
        groups.append(locals()[group_name])
