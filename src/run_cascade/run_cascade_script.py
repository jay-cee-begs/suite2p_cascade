import os, warnings
import sys
import glob
import numpy as np
import scipy.io as sio
import ruamel.yaml as yaml
yaml = yaml.YAML(typ='rt')



from run_cascade import CASCADE_functions
from run_cascade import functions_data_transformation 
from plotting import functions_plots as fun_plot
from batch_process import gui_configurations as configurations


def main():
    # ## get the names of the deltaF files from the functions_data_transformation.py file
    functions_data_transformation.get_file_name_list(folder_path = configurations.main_folder, file_ending ="samples", supress_printing = True)
    deltaF = functions_data_transformation.get_file_name_list(folder_path = configurations.main_folder, file_ending = "deltaF.npy")
    if len(deltaF) == 0:
        deltaF_files = functions_data_transformation.get_file_name_list(folder_path = configurations.main_folder, file_ending = "deltaF.npy")
    deltaF_files = functions_data_transformation.get_file_name_list(folder_path = configurations.main_folder, file_ending = "deltaF.npy")
    try:

        predictions_deltaF_files = functions_data_transformation.get_file_name_list(folder_path = configurations.main_folder, file_ending = "predictions_deltaF.npy") ## get the names of the predicted spike files
        if len(predictions_deltaF_files) == 0:
            predictions_deltaF_files = []
    except FileNotFoundError as e:
        print("Cascade Predictions do not exist yet")
        predictions_deltaF_files = []
    #TODO find a way to go through the directories and search for predictions deltaF; if for sample; != prediction file; calculate prediction file
    if len(predictions_deltaF_files) != len(deltaF_files):
        print("Cascade predictions for this dataset are missing, generating now...")
        for file in deltaF_files:
            CASCADE_functions.plots_and_basic_info(file)
            CASCADE_functions.cascade_this(file, configurations.nb_neurons)
        print("Done Generating Prediction Files")
    else:
        print("Cascade prediction files already exist")
    
if __name__ == "__main__":
    main()


"""To run:
activate cascade
import run_cascade
if __name__ == "__main__":
    run_cascade.main()
    
    """