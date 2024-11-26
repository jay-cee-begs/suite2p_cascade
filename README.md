# suite_cascade1p
Automated Calcium imaging detection (using suite2p) and deconvolution (using cascade) for primary neuronal cultures using widefield microscopy
- added simple GUI to both interact with the configurations file and start suite2p and cascade
- no need to manually change environments

The code itself is divided into 3 parts and 1 to run it. 

INSTALLING SUITE2P
navigate to the suite2p repository that is installed on your device
    Likely in Documents\GitHub\repo

create the suite2p environment with the command $conda env create -n suite2p -f suite2p-req.yml
suite2p requires python=3.8 and suite2p (version 0.14.0) to run

to make sure the setup.py file works, manually check to install $pip install chardet pyyaml$


Part 2: deconvolution / extrapolation of calcium events into underlying action potentials

An environment will need to be made for cascade

using $conda env create -n cascade -f cascade-req.yml

to make sure the setup.py file works, manually check to install $pip install chardet pyyaml$

Separately, you will also need to download a copy of the Cascade-master repository from GitHub (https://github.com/HelmchenLabSoftware/Cascade)

Once you extract all the files from the zip file. You will also need to replace the 'cascade2p' folder in the Cascade-master folder created with the 'cascade2p' zipped folder found above in this repository

This will fix some of the errors in calling Cascade on your local device (the provided code is tailored for a Google Collab workbook; we run Cascade locally and call functions in a pipeline
#TODO fork the cascade env and make the changes there

INSTALLING DATA_ENV
- for statannotations it is advised to install getzzes frk instead: pip3 install git+https://github.com/getzze/statannotations.git@compat-seaborn-13

you can create the environment

conda env create -n data_env -f statannotations-req.txt


now in terminal in the repo head

pip install -e .[*ENV_NAME*]
you will need to pip install for each name

if there are errors:
run $python setup.py develop$

to see exactly where the errors occur

- filepaths in the following files will have to be adjusted before first usage: run_default_ops.bat, run_plots.bat, run_s2p_gui.bat, run_sequence.bat (need to find a way to streamline)


The gui can be found in jd_gui_extended.py
it can be launched with $python -m jd_gui_extended$
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