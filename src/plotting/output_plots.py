from run_cascade import functions_data_transformation
from plotting import functions_plots as fun_plot
from batch_process import gui_configurations as configurations

def main():
    predictions_deltaF_files = functions_data_transformation.get_file_name_list(folder_path = configurations.main_folder, file_ending = "predictions_deltaF.npy") ## get the names of the predicted spike files
    output_directories = functions_data_transformation.get_file_name_list(folder_path = configurations.main_folder, file_ending = "samples")
    
    # for file, output in zip(predictions_deltaF_files, output_directories):
    #     fun_plot.histogram_total_estimated_spikes(file, output)
    # # # #TODO figure out how to compile group histograms
    # # # # for group in groups:
    # # # #     plot_group_histogram(group, predictions_deltaF_files)
    
    #     spike_maximum = fun_plot.get_max_spike_across_frames(predictions_deltaF_files)

    # for file, output in zip(predictions_deltaF_files, output_directories):
    #     fun_plot.plot_total_spikes_per_frame(file, spike_maximum, output)
    #     fun_plot.plot_average_spike_probability_per_frame(file, output)

    functions_data_transformation.create_output_csv(configurations.main_folder, overwrite = configurations.overwrite, iscell_check = configurations.iscell_check, update_iscell=configurations.update_iscell)
    functions_data_transformation.csv_to_pickle(configurations.main_folder, overwrite = True)
    #TODO add an output for final_df for within python stuff
    # create_final_df(configurations.main_folder)
    functions_data_transformation.create_experiment_overview(configurations.main_folder, configurations.groups)

if __name__=="__main__":
    main()
