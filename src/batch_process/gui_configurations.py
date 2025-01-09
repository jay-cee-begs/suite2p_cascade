import numpy as np 
main_folder = r'F:/JC_calcium_imaging/LB_hiPSC'
group1 = main_folder + r'\LB_iN'
group2 = main_folder + r'\LB_iN_iA'
group3 = main_folder + r'\LB_iN_ioA'
group_number = 3
data_extension = 'tif'
frame_rate = 10
cascade_file_path = r'C:\Users\jcbegs\Cascade-master'
ops_path = r'C:/Users/jcbegs/python3/suite2p_ops/Fabian_ops-4x.npy'
ops = np.load(ops_path, allow_pickle=True).item()
ops['frame_rate'] = frame_rate
ops['input_format'] = data_extension
BIN_WIDTH = 0
EXPERIMENT_DURATION = 60
FRAME_INTERVAL = 1 / frame_rate
FILTER_NEURONS = True
TimePoints = {
    'LB_': 'LB_',
}
exp_condition = {
    'LB_iN': 'LB_iN',
    'LB_iN_iA': 'LB_iN_iA',
    'LB_iN_ioA': 'LB_iN_ioA',
}
pairs = [ ('LB_iN', 'LB_iN_iA'), ('LB_iN_iA', 'LB_iN_ioA') ]
parameters = {
    'testby': pairs,
    'feature': ['Active_Neuron_Proportion', 'Total_Estimated_Spikes', 'Avg_Estimated_Spikes_per_cell'],
    'x': 'Group',
    'plotby': 'Time_Point',
    'stat_test': 'Mann-Whitney',
    'type': 'box',
    'legend': 'auto',
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
