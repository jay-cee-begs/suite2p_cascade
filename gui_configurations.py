main_folder = r'C:/Users/Justus/data/test_data_binned'
group1 = main_folder + r'\ACSF_baseline'
group2 = main_folder + r'\ACSF_GBZ'
group3 = main_folder + r'\NaOH_baseline'
group4 = main_folder + r'\NaOH_GBZ'
group5 = main_folder + r'\NBA_baseline'
group6 = main_folder + r'\NBA_GBZ'
group_number = 6
data_extension = 'tif'
frame_rate = 10
ops_path = r'C:\Users\Justus\data\test_data_binned\qm2.npy'
TimePoints = {
}
Groups22 = {
    'ACSF_baseline': '',
    'ACSF_GBZ': '',
    'NaOH_baseline': '',
    'NaOH_GBZ': '',
    'NBA_baseline': '',
    'NBA_GBZ': '',
}
pairs = [ ('Baseline', 'GBZ'), ('Baseline', 'TTX') ]
parameters = {
    'testby': pairs,
    'x': 'Group',
    'feature': 'Total_Estimated_Spikes',
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
EXPERIMENT_DURATION = 60
FRAME_INTERVAL = 1 / frame_rate
BIN_WIDTH = 20
FILTER_NEURONS = True
groups = []
for n in range(group_number):
    group_name = f"group{n + 1}"
    groups.append(eval(group_name))
for name, value in Groups22.items():
    # Add your logic to handle Groups22
    pass
