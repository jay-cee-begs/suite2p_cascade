from run_cascade import functions_data_transformation
from plotting import functions_plots as fun_plot
from network_analysis import rastermapping, networkx_functions
from batch_gui.config_loader import load_json_config_file, load_json_dict

_DEFAULT_CONFIG = load_json_config_file()
config = _DEFAULT_CONFIG

def main(config_file = None):
    global config  # <- important
    global config_dict
    if config_file is not None:
        config = load_json_config_file(config_file)
        config_dict = load_json_dict(config_file)

    else:
        config = load_json_config_file()
        config_dict = load_json_dict()
    suite2p_folders = functions_data_transformation.get_file_name_list(config.general_settings.main_folder, 'samples', supress_printing=True)
    functions_data_transformation.check_deltaF(suite2p_folders, config)
    functions_data_transformation.check_network_deltaF(suite2p_folders, config)

    predictions_deltaF_files = functions_data_transformation.get_file_name_list(folder_path = config.general_settings.main_folder, file_ending = "predictions_deltaF.npy") ## get the names of the predicted spike files
    output_directories = functions_data_transformation.get_file_name_list(folder_path = config.general_settings.main_folder, file_ending = "samples")
    
    spike_maximum = fun_plot.get_max_spike_across_frames(predictions_deltaF_files)
    for file, output in zip(predictions_deltaF_files, output_directories):
            fun_plot.plot_total_spikes_per_frame(file, spike_maximum, output)
            fun_plot.plot_average_spike_probability_per_frame(file, output)
#translate_suite2p_outputs_to_csv(main_folder, config, overwrite=False, check_for_iscell=True, update_iscell = True):
    functions_data_transformation.translate_suite2p_outputs_to_csv(main_folder = config.general_settings.main_folder, config = config, overwrite = True, 
                                                    check_for_iscell=bool(config.analysis_params.use_suite2p_ROI_classifier), 
                                                    update_iscell=bool(config.analysis_params.update_suite2p_iscell))#overwrite = config.general_settings.overwrite, iscell_check = config.general_settings.iscell_check, update_iscell=config.general_settings.update_iscell)
    functions_data_transformation.csv_to_pickle(config.general_settings.main_folder, overwrite = True)
    #TODO add an output for final_df for within python stuff
    # create_final_df(config.general_settings.main_folder)
    functions_data_transformation.create_experiment_overview(config, config.analysis_params.use_suite2p_ROI_classifier)
    functions_data_transformation.create_experiment_summary(config.general_settings.main_folder)
if __name__=="__main__":
    main()
    rastermapping.main()
    # networkx_functions.main()

