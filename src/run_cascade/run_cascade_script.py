import os, warnings
import sys
import glob
import numpy as np
import scipy.io as sio
import ruamel.yaml as yaml
yaml = yaml.YAML(typ='rt')



from run_cascade import CASCADE_functions
from run_cascade import functions_data_transformation, functions_general
from plotting import functions_plots as fun_plot
from batch_process.config_loader import load_json_config_file, load_json_dict

config = load_json_config_file()


def main():
    # ## Needs to be cleaned fully
    CASCADE_functions.check_for_cascade_model()
    
    if config.cascade_settings.overwrite_existing_cascade_output:
        F_traces = functions_data_transformation.get_file_name_list(folder_path = config.general_settings.main_folder, file_ending ="F.npy", supress_printing = True)
        for f in F_traces:
            functions_general.calculate_deltaF(f)
    functions_data_transformation.get_file_name_list(folder_path = config.general_settings.main_folder, file_ending ="samples", supress_printing = True)
    deltaF = functions_data_transformation.get_file_name_list(folder_path = config.general_settings.main_folder, file_ending = "deltaF.npy")
    if len(deltaF) == 0:
        deltaF_files = functions_data_transformation.get_file_name_list(folder_path = config.general_settings.main_folder, file_ending = "deltaF.npy")
    deltaF_files = functions_data_transformation.get_file_name_list(folder_path = config.general_settings.main_folder, file_ending = "deltaF.npy")
    try:

        predictions_deltaF_files = functions_data_transformation.get_file_name_list(folder_path = config.general_settings.main_folder, file_ending = "predictions_deltaF.npy") ## get the names of the predicted spike files
        if len(predictions_deltaF_files) == 0:
            predictions_deltaF_files = []
    except FileNotFoundError as e:
        print("Cascade Predictions do not exist yet")
        predictions_deltaF_files = []
    #TODO find a way to go through the directories and search for predictions deltaF; if for sample; != prediction file; calculate prediction file
    if config.cascade_settings.overwrite_existing_cascade_output or len(predictions_deltaF_files)==0:
        for file in deltaF_files:
            CASCADE_functions.plots_and_basic_info(file)
            CASCADE_functions.cascade_this(file, int(config.cascade_settings.nb_neurons))
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