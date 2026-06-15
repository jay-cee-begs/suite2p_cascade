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
from batch_gui.config_loader import load_json_config_file, load_json_dict


_DEFAULT_CONFIG = load_json_config_file()
config = _DEFAULT_CONFIG


def main(config_file = None):
    """
    Run Cascade deconvolution  preprocessing and analysis pipeline based on a configuration file.

    This function loads a JSON configuration, containing all information of Cascade location,
    Cascade pre-trained models, and other parameters. If the given pre-trained model is not available,
    it is downloaded. Raw fluorescence files are converted into deltaF / F0 files (deltaF.npy), and 
    process deltaF.npy files into Cascade predictions_deltaF.npy files for all files (if overwrite_cascade)
    or for unprocessed files (if not overwrite_cascade) in the config.json file. 
    The function again saves a analysis_config.json copy of the configurations used for analysis.

    Args:
    ----------
        config_file : str or Path, optional
            Path to a JSON configuration file. If omitted, the default configuration
            from ``config_loader`` is used.

    Returns:
    ----------
        None
            The function performs processing and file I/O but does not return a value.


    Workflow:
    ----------
        1. Load configuration (config.json) file.
        2. Check if the pre-trained Cascade model is available locally.
        3. Identify all image folders and processed Suite2p folders.
        4. Run Cascade on unprocessed folders (or all folders if overwrite_cascade is enabled).
        5. Save the Cascade deconvolution as predictions_deltaF.npy in each Suite2p output directory.
    """
    try:
        global config  # <- important
        global config_dict
        if config_file is not None:
            config = load_json_config_file(config_file)
            config_dict = load_json_dict(config_file)

        else:
            config = load_json_config_file()
            config_dict = load_json_dict()
            
        CASCADE_functions.check_for_cascade_model(config)
        
        if config.analysis_params.overwrite_cascade:
            F_traces = functions_data_transformation.get_file_name_list(folder_path = config.general_settings.main_folder, file_ending ="F.npy", supress_printing = True)
            for f in F_traces:
                functions_general.calculate_deltaF(f, config)
            suite2p_folders = functions_data_transformation.get_file_name_list(folder_path = config.general_settings.main_folder, file_ending ="samples", supress_printing = True)
            deltaF = functions_data_transformation.get_file_name_list(folder_path = config.general_settings.main_folder, file_ending = "deltaF.npy", supress_printing = True)

            for file in deltaF:
                CASCADE_functions.plots_and_basic_info(file, config)
                CASCADE_functions.cascade_this(file, config)

        else:
            predictions_deltaF_files = functions_data_transformation.get_file_name_list(folder_path = config.general_settings.main_folder, file_ending = "predictions_deltaF.npy") ## get the names of the predicted spike files
            F_traces = functions_data_transformation.get_file_name_list(folder_path = config.general_settings.main_folder, file_ending ="F.npy", supress_printing = True)
            for f in F_traces:
                functions_general.calculate_deltaF(f, config)
            suite2p_folders = functions_data_transformation.get_file_name_list(folder_path = config.general_settings.main_folder, file_ending ="samples", supress_printing = True)
            deltaF = functions_data_transformation.get_file_name_list(folder_path = config.general_settings.main_folder, file_ending = "deltaF.npy", supress_printing = True)
            unprocessed_folders = []
            cascade_suffix = 'suite2p\plane0\predictions_deltaF.npy'
            cascade_processed_files = []
            for file in predictions_deltaF_files:
                cascade_processed_files.append(file.split(cascade_suffix)[-1])
            for folder in suite2p_folders:
                if folder not in cascade_processed_files:
                    unprocessed_folders.append(folder)

            for folder in unprocessed_folders:
                folder = os.path.join(folder, *functions_data_transformation.SUITE2P_STRUCTURE['deltaF'])
                CASCADE_functions.plots_and_basic_info(folder, config)
                CASCADE_functions.cascade_this(folder, config)
            
        import json
        with open(os.path.join(config.general_settings.main_folder, 'analysis_config.json'), 'w') as f:
            json.dump(config_dict, f, indent = 4)
        print(f"Analysis parameters saved in {config.general_settings.main_folder} as analysis_config.json")
        from datetime import datetime

        now = datetime.now()

        current_time = now.strftime("%H:%M:%S")
        print("Current Time =", current_time)
    except KeyboardInterrupt as e:
        print("Cascade Processing interrupted by user", '\n')
    finally:
        import json
        with open(os.path.join(config.general_settings.main_folder, 'analysis_config.json'), 'w') as f:
            json.dump(config_dict, f, indent = 4)
        print(f"Analysis parameters saved in {config.general_settings.main_folder} as analysis_config.json")
        from datetime import datetime

        now = datetime.now()

        current_time = now.strftime("%H:%M:%S")
        print("Current Time =", current_time)
if __name__ == "__main__":
    main()


"""To run:
activate cascade
import run_cascade
if __name__ == "__main__":
    run_cascade.main()
    
    """