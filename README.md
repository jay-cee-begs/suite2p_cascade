# Suite2p and CASCADE workflow

A semi-automated calcium imaging detection (using Suite2p from https://github.com/MouseLand/suite2p) and deconvolution (using Cascade from https://github.com/HelmchenLabSoftware/Cascade) 
pipeline for analyzing somatic calcium imaging signals from primary neuronal cultures with 1P widefield microscopy


## Before we begin

There are several things that should be done *in advance* before we install the actual repository itself. 

 1) You will need to use a python interpretter (either Anaconda, miniforge, python.exe version 3.8, etc.)

## Setup and Installation 

To start you will need to create a fork of this repository to your current machine. This will allow you to copy all the files found in the project and also 
will allow you to stay up-to-date on any future changes that come with this project. NOTE: likely would be for someone _easier_ to just make a package with the src code on PyPi

### INSTALLING SUITE2P in its virtual environment

1. Navigate to the local copy you have of the suite2p_cascade repository in a terminal window using the `cd` command and the path to the copied repository

2. Create a virtual environment in anaconda / miniforge / PyPy for suite2p using python 3.8 by running the command `conda create -n suite2p python=3.8`

3. Run the command `python -m pip install suite2p[gui]` to install all necessary packages for analysis

4. You will also need to install other packages for analysis such as `pip install nd2 seaborn BaselineRemoval` etc. 

5. To confirm suite2p installed correctly, `python -m suite2p` If the GUI does not launch for some reason read the error and install the missing package. If other errors persist, please force reinstallation with
    `python -m pip install suite2p[gui] --no-cache`

6. Lastly, please run `pip install -e .` from the forked GitHub suite2p_cascade repo on your machine to install the setup.py file 


### INSTALLING CASCADE in its virtual environment

1. Create a virtual environment in anaconda / miniforge for cascade using python 3.8 by running the command `conda create -n cascade python=3.8`

2. You will need to fork the repository cascade_local from https://github.com/jay-cee-begs/Cascade/tree/cascade_local 
    which will allow you to install models for deconvolution based on experimental setups. This version of Cascade's code has been modified by me to run locally rather than a Google Collab server.

3. After downloading, install this version of Cascade into your cascade evnironment on your local PC using the command `pip3 install git+https://github.com/jay-cee-begs/Cascade.git@cascade_local`

4. Navigate to the suite2p_cascade repository and run `pip install -e .` to create an editable installation of the package. 

5. Navigate to the cascade (cascade_local) directory using `cd` and run `pip install -e .` to have access to an editable Cascade


**NOTE**: in order for this to work properly, users have have to install the language Rust (using all of the default options) if it is not installed already (https://rustup.rs/). During installation, please also install Windows C++ Developer tools and repeat all steps from 3


### Creating an analysis virtual environment for plotting

We rely on more modern python versions for plotting (e.g., Python 3.13)

1. Create the environment for analysis / plotting (conda create -n <your_env_name>: `conda create -n analysis python=3.13`)

**NOTE** IF the environment name is not `analysis` it needs to be updated manually in the run_sequence.bat files along with python paths so that the GUI and pipeline work correctly.

2. Install all necessary Python packages such as `pip install BaselineRemoval pynapple seaborn numpy pandas matplotlib numba networkx rastermap scipy` 

3. An example package for automatic plotting in Python with statistical significance is `statannotations`.

    - It is best to install the getzzes frk of statannotations instead of the main version: 
    `pip3 install git+https://github.com/getzze/statannotations.git@compat-seaborn-13`

### Updating .bat files for pipeline processing

The filepaths in the processing batch (.bat) file(s) will need to be updated *first* before the pipeline will run correctly:
    run_sequence.bat

    To find the correct filepath to change, run `conda env list` and replace the .bat filepath root stems up to "Scripts\activate.bat" with whatever is printed as the 'base' conda environment

    This needs to be done for all file paths (one for each environment: suite2p, cascade, analysis)


# Running the GUI

-- The gui can be found the folder batch_gui
-- All backend GUI functions are found in batch_core
-- navigate to the batch_gui folder from the suite2p_cascade folder by calling the command `cd src\batch_gui`
-- it can be launched from the batch_gui folder with the command `python -m run_gui`


## Workflow

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
* Both image files and folders with images are acceptable. The code will look inside an experiment folder for experimental conditions. These conditions should contain image fies of a particular type (e.g., tiff, nd2) that are unsorted or pre-sorted into subfolders (if multiple images exist for similar regions). When the experiment_condition folder contains multiple images, the code will automatically sort each image file into its own folder so that it can be processed individually by Suite2p. 


1. AFTER THE INSTALL: Please open up batch files using Visual Studio Code or another code editor.

2. For every `CALL` `path_to_conda_activate.bat`, please update the path to your own base conda path. you can find this path by running `conda env list` and replacing everything before `\Scripts\activate.bat` This will only need to be done the first time openning the analysis pipeline.

### In the GUI

3. The GUI will now run the analysis pipeline correctly.
To launch the gui, navigate to the gui_config folder using `cd path\to\GitHub\folder\suite2p_cascade\src\batch_gui` followed by `python -m run_gui`

4. After launching the GUI change the `Experiment / Main Folder Path:` using the `Browse` button or by manually typing in the folder containing all imaging files already presorted into experimental treatments (and potentially similar regions if running registration and comparing the same synapses over time)

5. Enter the `Data Extension` for your imaging files without `.` (e.g. `tif`, `tiff`, or `nd2`) and click `Add Experiment Conditions` to automatically add the subfolders containing images as experimental groups. The Experiment Conditions will automatically populate a dictionary visible lower in the GUI. 

* It is essential that the '.' is not in the data extension / file ending so Suite2p will run and process the data appropriately!

6. `Browse` for or copy/paste the folder directory for your locally installed cascade (e.g., path\to\GitHub\folder\cascade)

7. In the `Suite2p settings (ops.npy):` Browse or manually enter your own suite2p detection settings (`.npy` file). Example Suite2p_ops files for 4x and 10x calcium imaging recordings are provided in the repository; however, custom suite2p settings files can be generated and checked for accuracy using the Suite2p GUI. From the suite2p virtual env run `python -m suite2p`

8. Enter the frame rate of your images in frames per second<br>
Enter the `Experiment Duration` in number of seconds<br>
Enter the `Network Bin Width` in numbers of frames to group for synchronous synapse detection (default 5 frames)

### Editing Analysis Parameters

9. `Edit Analysis Parameters` to change the analysis_params section of the `config.json` file to adjust post-processing analysis settings for suite2p data
```
Editable Analysis Parameters
    overwite_suite2p: boolean 
        Allows pipeline to overwrite pre-existing suite2p files and deltaF files

    overwrite_cascade: boolean
        Allows pipeline to overwrite pre-existing cascade (predictions_deltaF.npy files)

    multivid_processing: boolean
        Tells the pipeline that multiple images exist per region, per subfolder.
        IF this is selected, it will automatically launch a Pop-up GUI for these settings later. 

    use_suite2p_ROI_classifier: boolean
        Utilizes Suite2p in-built classifier
        *This is not recommended on a first pass of the data, only after manual curation. 
        *Users can make their own classifiers for synaptic calcium imaging data if desired. 

    update_suite2p_iscell: boolean 
        Update the Suite2p `iscell.npy` file for filtering "real" and "noise" ROIs from one another. 
        1 = "cells" or included ROIs and 0 = "non-cells" or excluded ROIs

    Img_Overlay: str ("max_proj" or "meanImg") 
        choice of max projection (max_proj) or mean image (meanImg) as a base for overlaying synaptic ROIs
        default: meanImg
    
    cascade_activity_threshold: float
        Number of cascade-predicted spikes required for for an ROI to be considered active
        default: 0.1 (determined by testing active neurons in the presence of TTX)

    nb_neurons: int
        Number of Neurons to show if cascade plots are generated (default settings for Cascade that is not used; most users can ignore)

    model_name: str
        Name of pre-trained Cascade model to use for predicting spikes. The model should match the frame rate used; longer smoothing times lead to less gaussian corrections.
        A list of pre-trained models can be found in the cascade_available_models.ipynb file
    
    
    MAD_baseline_filter_threshold: float
        Number of MAD-estimated standard deviations above MAD to use as a cutoff for isolating baseline / noise frames

    baseline_correction: boolean
        Whether or not to perform baseline correction (optimal for network activity calculations)
    
    correction_method: str, optional ("airPLS" or "rolling_median")
        User choice of baseline correction between airPLS algorithm from NMR analysis or rolling median. These functions are used to generate dF / F0 files

    lambda_window: int, optional
        The lambda_ value for optmizing airPLS correction (recommended value: 10); higher values (e.g., 100, 1000) remove baseline fluctuations less rigorously)
        The _window value for number of frames to calculate rolling median over (recommended value: ~100-500 frames out of 3600)

    normalize_peaks: bool
        If true, will normalize all activity traces between 0-1 for looking at network activity

    F Normalization: str, optional ("Cell" or "Population")
        If normalize_peaks is True, normalize fluorescence within cells (e.g., all cells have same min / max fluorescence) or for the population (normalize between min / max of the population fluorescence)
    
Multivid_Registration_Params
        saved in config.json as general_settings['multivid_params'] or as general namespace object general_settings.multivid_params
    
    Treatment_No: Number of treatments / Videos (including baseline)
        Interactive to control for number of videos within a given subfolder
        e.g., Treatment_No = 3; baseline -> treatment1 -> treatment2
    
    equal_baseline_and_treatments: boolean
        Are all videos (e.g., baseline and treatments the same number of frames?)
        
        IF not selected, other settings display listed below

        Treatment length units: "seconds" or "frames"
            Units for the length of each video provided. Seconds and Frames for each video are possible units
        
        Video Lengths: user input
            Video lengths for Baseline and Treatment 1, Treatment 2, etc.      
```

10. Save the configurations to update the .json configurations that will be used for analysis

11. Click Process to run 

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


