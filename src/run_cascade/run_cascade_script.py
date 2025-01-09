import os, warnings
import sys
import glob
import numpy as np
import scipy.io as sio
import ruamel.yaml as yaml
yaml = yaml.YAML(typ='rt')

from run_cascade import CASCADE_functions
from run_cascade import functions_data_transformation 
from plotting import functions_plots as fun_plot, networkx_functions as nx_plot
from batch_process import gui_configurations as configurations


def main():
    # ## get the names of the deltaF files from the functions_data_transformation.py file

    deltaF = functions_data_transformation.get_file_name_list(folder_path = configurations.main_folder, file_ending = "deltaF.npy")
    # if len(deltaF_files) == 0:
    #     deltaF_files = get_file_name_list(folder_path = configurations.main_folder, file_ending = "deltaF.npy")
    deltaF_files =functions_data_transformation.get_file_name_list(folder_path = configurations.main_folder, file_ending = "deltaF.npy")
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
    

    predictions_deltaF_files = functions_data_transformation.get_file_name_list(folder_path = configurations.main_folder, file_ending = "predictions_deltaF.npy") ## get the names of the predicted spike files
    output_directories = functions_data_transformation.get_file_name_list(folder_path = configurations.main_folder, file_ending = "samples")
    
    for file, output in zip(predictions_deltaF_files, output_directories):
        fun_plot.histogram_total_estimated_spikes(file, output)
    # # #TODO figure out how to compile group histograms
    # # # for group in groups:
    # # #     plot_group_histogram(group, predictions_deltaF_files)
    
        spike_maximum = fun_plot.get_max_spike_across_frames(predictions_deltaF_files)

    for file, output in zip(predictions_deltaF_files, output_directories):
        fun_plot.plot_total_spikes_per_frame(file, spike_maximum, output)
        fun_plot.plot_average_spike_probability_per_frame(file, output)

    functions_data_transformation.create_output_csv(gui_configurations.main_folder, overwrite = gui_configurations.overwrite, iscell_check = gui_configurations.iscell_check, update_iscell=gui_configurations.update_iscell)
    functions_data_transformation.csv_to_pickle(gui_configurations.main_folder, overwrite = True)
    #TODO add an output for final_df for within python stuff
    # create_final_df(configurations.main_folder)
    functions_data_transformation.create_experiment_overview(configurations.main_folder, configurations.groups)

if __name__ == "__main__":
    main()
    nx_plot.main()


"""To run:
activate cascade
import run_cascade
if __name__ == "__main__":
    run_cascade.main()
    
    """