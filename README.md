# suite_cascade1p
Automated Calcium imaging detection (using suite2p) and deconvolution (using cascade) for primary neuronal cultures using widefield microscopy
- added simple GUI to both interact with the configurations file and start suite2p and cascade
- no need to manually change environments
- needed: seperate environments for suite2p, cascade and plotting, an already existing gui_configurations.py file
- additionally to suite2p/cascade packages: seaborn, statannotations 
- filepaths in the following files will have to be adjusted before first usage: run_default_ops.bat, run_plots.bat, run_s2p_gui.bat, run_sequence.bat (need to find a way to streamline)
- the GUI needs an already existing gui_configurations file*
- call the GUI by executing jd_gui_test.py (plan to adjust so it can be launched by doubleclick)

*minimal necessary structure: 

### please type in your main folder path manually for the first time and set group_number to 0: ###

main_folder = r'C:/Users/YourName/ExperimentFolder/Experiment' 
group_number = 0

### the pairs list and the parameters dictionary will have to be initiated as well, all the values will be changable in the GUI ###
pairs = [ ]
parameters = {
    'testby': pairs,
    'feature': ['Active_Neuron_Proportion', 'Total_Estimated_Spikes_proportion_scaled'],
    'x': 'Group',
    'type': 'swarm',
    'plotby': 'Time_Point',
    'y_label': 'y label',
    'x_label': '',
    'stat_test': 'Mann-Whitney',
    'legend': 'auto',
    'location': 'inside',
    'palette': 'viridis',
}