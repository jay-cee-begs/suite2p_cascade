### suite2p and Cascade workflow

A semi-automated calcium imaging detection (using suite2p) and deconvolution (using cascade) pipeline for primary neuronal culture calcium imaging using widefield microscopy
Designed to make calcium imagin 

- added simple GUI to both interact with the configurations file and start suite2p and cascade
- no need to manually change environments

## Before we begin

There are several things that should be done before we install the actual repository itself. 

--First: You will need to use a python interpretter (either Anaconda, miniforge, python.exe, etc)

## Setup and Installation 

to start you will need to create a fork of this repository to your current machine. This will allow you to copy all the files found in the project and also 
will allow you to stay up-to-date on any future changes that come with this project

you will also need to create a fork of Cascade so that you can create an editable installation

# INSTALLING SUITE2P

It is easiest to follow the instructions of Carsen Stringer's lab on the suite2p Github (https://github.com/MouseLand/suite2p)

Please follow their instructions for installing suite2p and the GUI user interface (e.g. python -m pip install suite2p[gui])

once the environment is activated, please also install *nd2* and *nd2reader* using either conda or pip


# INSTALLING CASCADE

There are multiple options for installing cascade. 

The preferred method (for me and this project) is to fork the cascade master repository from Github to your own github (https://github.com/HelmchenLabSoftware/Cascade)

From here you will then create a new environment using python 3.7 (conda create -n Cascade python=3.7)

--Then navigate to the local cascade repository (most likely in ..\Documents\GitHub\Cascade) using cd and the directory you want to navigate to

To install cascade, then run pip install -e . within the forked and cloned local repository

**NOTE**: in order for this to work properly, you will have to install the language Rust (using all of the default options) if it is not installed already (https://rustup.rs/) and enabled Desktop development with C++ in Visual Studio (https://visualgdb.com/support/getvcpp/)


Alternatively: you can follow the installation instructions in the Cascade master repository (https://github.com/HelmchenLabSoftware/Cascade)

# INSTALLING DATA_ENV for plotting
- for statannotations it is advised to install getzzes frk instead: pip3 install git+https://github.com/getzze/statannotations.git@compat-seaborn-13

you can create the environment for plotting (conda create -n <your_env_name>)

- for statannotations it is advised to install getzzes frk instead: pip3 install git+https://github.com/getzze/statannotations.git@compat-seaborn-13


# Environment pip editable installations

You can make custom scripts installable by users so they are easily accessible within the virtual environment

first navigate to your local copy of this repository (cd ..\Documents\Github\suite_cascade1p)

pip install -e .[*ENV_NAME*]
you will need to pip install for each name

OR

activate each environment (e.g. conda activate suite2p, conda activate Cascade, etc.) and then run pip install -e . 


if there are errors:
run $python setup.py develop$

to see exactly where the errors occur

## Workflow

Part 2: deconvolution / extrapolation of calcium events into underlying action potentials

An environment will need to be made for cascade

using $conda env create -n cascade -f cascade-req.yml

to make sure the setup.py file works, manually check to install $pip install chardet pyyaml$


### ***----------------------------------------------------------------------------------------------------------------***


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