# Suite2p and CASCADE workflow

A semi-automated calcium imaging detection (using suite2p) and deconvolution (using cascade) pipeline for primary neuronal culture calcium imaging using widefield microscopy


## Before we begin

There are several things that should be done before we install the actual repository itself. 

--First: You will need to use a python interpretter (either Anaconda, miniforge, python.exe version 3.8)

## Setup and Installation 

To start you will need to create a fork of this repository to your current machine. This will allow you to copy all the files found in the project and also 
will allow you to stay up-to-date on any future changes that come with this project. NOTE: likely would be for someone _easier_ to just make a package with the src code on PyPi

Alternatively you should download a zip file of the code and save it somewhere you can access easily

### INSTALLING SUITE2P

1. Navigate to the local copy you have of the suite2p_cascade repository in a terminal window using the `cd` command and the path to the copied repository

2. Create a virtual environment in anaconda / miniforge / PyPy for suite2p using python 3.8 by running the command `conda create -n suite2p python=3.8`

3. Run the command `python -m pip install suite2p[gui]` to install all necessary packages for analysis

4. You will also need to install other packages for analysis such as `pip install nd2 seaborn` etc. 

5. To confirm suite2p installed correctly, `python -m suite2p` If the GUI does not launch for some reason read the error and install the missing package

6. Lastly, please run `pip install -e .` from the forked GitHub suite2p_cascade repo on your machine to install the setup.py file 


### INSTALLING CASCADE

1. Create a virtual environment in anaconda / miniforge for cascade using python 3.8 by running the command `conda create -n cascade python=3.8`

2. Lastly you will need to fork the repository cascade_local from https://github.com/jay-cee-begs/Cascade/tree/cascade_local 
which will allow you to install models for deconvolution based on experimental setups

3. Install cascade2p for deconvolution on your local PC using the command `pip3 install git+https://github.com/jay-cee-begs/Cascade.git@cascade_local`


**NOTE**: in order for this to work properly, you might have to install the language Rust (using all of the default options) if it is not installed already (https://rustup.rs/). During installation, please also install Windows C++ Developer tools


### INSTALLING DATA_ENV for plotting
We utilize a separate python environment for plotting to get out of python 3.8

1. Create the environment for analysis / plotting (conda create -n <your_env_name>)

**NOTE** The environment name should be reflected in the bat files so that the pipeline works correctly

2. A Nice Package for automatic plotting in python with statistical significance is statannotations.

- It is best to install the getzzes frk of statannotations instead of the main version: 
`pip3 install git+https://github.com/getzze/statannotations.git@compat-seaborn-13`

3. Update the filepaths in the following files before first using the pipeline: run_default_ops.bat, run_plots.bat, run_s2p_gui.bat, run_sequence.bat (need to find a way to streamline this)


-- The gui can be found in soma_gui.py
-- navigate to the batch_process folder from the suite2p_cascade folder by calling the command `cd src\batch_process`
-- it can be launched with `python -m soma_gui`


# Workflow

* Prior to starting you should organize your data into the following experiment structure
```
    \path\to\experiment\folder
    ├───experiment_condition_folder_1
    │   ├───image_or_image_folder_1
    │   ├───image_or_image_folder_2
    │   ├───image_or_image_folder_3
    │       
    ├───experiment_condition_folder_2
    │   ├───image_or_image_folder_1
    │   ├───image_or_image_folder_2
    │   └───image_or_image_folder_3
    │       
    ├───experiment_condition_folder_3
    │   ├───image_or_image_folder_1
    │   ├───image_or_image_folder_2
    │   └───image_or_image_folder_3
    │       
    ├───experiment_condition_folder_4
    │   ├───image_or_image_folder_1
    │   ├───image_or_image_folder_2
    │   ├───image_or_image_folder_3
```
* Both image files and folders with images are acceptable. The code will look for image folders containing single image files; if it finds none, it will move all image files of a particular type (e.g. nd2 / tif) into folders of the same name automatically


1. AFTER THE INSTALL: Please open up batch files using Visual Studio Code or another variant to look at windows batch files

2. For every `CALL` `path_to_conda_activate.bat`, please update the path to your own base conda path. you can find this path by running `conda env list` and replacing everything before `\Scripts\activate.bat` This will only need to be done the first time openning the analysis pipeline

3. The GUI will now run the analysis pipeline correctly.
To launch the gui either double click `run_analysis_gui.bat` found in `suite2p_cascade\src\batch_process\Scripts` or navigate to the batch_process folder using `cd .\suite2p_cascade\src\batch_process` followed by `python -m soma_gui`

4. After launching the soma_gui change the `experiment / main_folder` using the `Browse` button (the folder containing experimental conditions as subfolders)

5. Enter the file extension for your image type without `.` (e.g. `tif`, `tiff`, or `nd2`) and click `Add Experiment Conditions` to automatically add the subfolders containing images as experimental groups

6. `Browse` for your locally installed cascade (Usually titled Cascade-MASTER or Cascade depending on if it was installed as a .zip file or forked from GitHub)

7. Find your own suite2p detection settings (`.npy` file) using `Browse` or `Create New Ops File` using the suite2p GUI
NOTE: please wait for the GUI to launch, it will take some time and then open the settings for testing using `CTRL+R` or File -> Run_Suite2p

8. Enter the frame rate of your images

9. 

10. Save the configurations to update the .json configurations that will be used for analysis

11. Select which process you would like to run from Suite2p and Cascade: `Skip Suite2p` starts analyzing suite2p data with cascade `Run Full Process` analyzes image files with suite2p and cascade together

Select `use iscell.npy` if you would like to rerun analysis using manually currated suite2p ROI data, or if you want to use Suite2p's in-built classifier to identify appropriate cells (***NOT RECOMMENDED***)

12. Click Process to run 

At the end of the processing, there will be summary files in each of the image folders

Cascade predicted spikes will be saved in `suite2p\plane0\predictions_deltaF.npy`
`suite2p\plane0\iscell.npy` will be updated based on activity in predicted spikes
<br>
Each image folder will contain graphical depictions of Total Estimated Spikes across all neurons and the Average Estimated Spikes across all neurons
<br>
Each experimental condition folder will have ROIs circled overlayed on a meanImg or max_proj depending on which is chosen in the analysis_params settings
<br> 
Summary statistics are exported in csv file format in the file `Experiment Summary.csv`

### ***----------------------------------------------------------------------------------------------------------------***


