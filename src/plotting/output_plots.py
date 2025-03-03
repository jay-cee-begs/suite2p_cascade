from run_cascade import functions_data_transformation
from plotting import functions_plots as fun_plot
from plotting import rastermapping, networkx_functions
from batch_process.config_loader import load_json_config_file, load_json_dict
config = load_json_config_file()

def main():
    predictions_deltaF_files = functions_data_transformation.get_file_name_list(folder_path = config.general_settings.main_folder, file_ending = "predictions_deltaF.npy") ## get the names of the predicted spike files
    output_directories = functions_data_transformation.get_file_name_list(folder_path = config.general_settings.main_folder, file_ending = "samples")
    if config.graph_settings.total_estimated_spike_histogram:
        for file, output in zip(predictions_deltaF_files, output_directories):
            fun_plot.histogram_total_estimated_spikes(file, output)
    # # #TODO figure out how to compile group histograms
    # # # for group in groups:
    # # #     plot_group_histogram(group, predictions_deltaF_files)
    
    spike_maximum = fun_plot.get_max_spike_across_frames(predictions_deltaF_files)
    if config.graph_settings.total_estimated_spikes_per_frame or config.graph_settings.avg_estimated_spikes_per_frame:
        for file, output in zip(predictions_deltaF_files, output_directories):
            fun_plot.plot_total_spikes_per_frame(file, spike_maximum, output)
            fun_plot.plot_average_spike_probability_per_frame(file, output)

    functions_data_transformation.create_output_csv(config.general_settings.main_folder, overwrite = True, 
                                                    iscell_check=bool(config.cascade_settings.use_suite2p_ROI_classifier), 
                                                    update_iscell=bool(config.cascade_settings.update_suite2p_iscell))#overwrite = config.general_settings.overwrite, iscell_check = config.general_settings.iscell_check, update_iscell=config.general_settings.update_iscell)
    functions_data_transformation.csv_to_pickle(config.general_settings.main_folder, overwrite = True)
    #TODO add an output for final_df for within python stuff
    # create_final_df(config.general_settings.main_folder)
    functions_data_transformation.create_experiment_overview(config.general_settings.main_folder, config.general_settings.groups)

if __name__=="__main__":
    main()
    if config.graph_settings.rastermap_plot:
        rastermapping.main()
    # networkx_functions.main()

