
import os
import pandas as pd
import numpy as np
from run_cascade import functions_general as g_func
from batch_gui.config_loader import load_json_config_file, load_json_dict
from plotting import functions_plots as fun_plot 
from network_analysis import network_analysis as net_analysis

_DEFAULT_CONFIG = load_json_config_file()
config = _DEFAULT_CONFIG

SUITE2P_STRUCTURE = {
    "F": ["suite2p", "plane0", "F.npy"],
    "Fneu": ["suite2p", "plane0", "Fneu.npy"],
    "spks": ["suite2p", "plane0", "spks.npy"],
    "stat": ["suite2p", "plane0", "stat.npy"],
    "iscell": ["suite2p", "plane0", "iscell.npy"],
    "deltaF": ["suite2p", "plane0", "deltaF.npy"],
    "ops":["suite2p", "plane0", "ops.npy"],
    "cascade_predictions": ["suite2p", "plane0", "predictions_deltaF.npy"],
    "network_deltaF": ["suite2p", "plane0", "F_network_normalized.npy"]

}

def load_npy_array(npy_path):
    """
    Load a NumPy `.npy` file into a NumPy array.
    
    This function loads the `.npy` file located at the specified `npy_path` and returns it as a NumPy array.
    The `allow_pickle` option is set to `True` to allow loading pickled objects.
    
    Args:
    ----------
        npy_path : (str or Path)
            The file path to the `.npy` file (e.g., `F.npy` or `Fneu.npy`)
    
    Returns:
    ----------
        numpy.ndarray : 2D Array
            The loaded NumPy array from the `.npy` file
    
    Example:
    ----------
        >>> load_npy_array('data/F.npy')
        array([1, 2, 3])
    """
    return np.load(npy_path, allow_pickle=True) #functionally equivalent to np.load(npy_array) but iterable; w/ Pickle

def load_npy_df(npy_path):
    """
    Load a NumPy `.npy` file as a Pandas DataFrame.
    
    This function loads the `.npy` file at the specified `npy_path` and converts it into a Pandas DataFrame.
    The `allow_pickle` option is set to `True` to allow loading pickled objects.
    
    Args:
    ----------
        npy_path : str or Path
            The file path to the `.npy` file (e.g., `F.npy` or `Fneu.npy`)
    
    Returns:
    ----------
        pd.DataFrame : DataFrame of NumPy file
            A Pandas DataFrame containing the loaded data from the `.npy` file
    
    Example:
    ----------
        >>> load_npy_df('data/F.npy')
        DataFrame with shape (3, 3)
    """
    return pd.DataFrame(np.load(npy_path, allow_pickle=True)) #load suite2p outputs as pandas dataframe

def load_npy_dict(npy_path):
    """
    Load a NumPy `.npy` file as a dictionary.
    
    This function loads the `.npy` file at the specified `npy_path` and returns the contents as a dictionary.
    The `allow_pickle` option is set to `True` to allow loading pickled objects.
    
    Args:
    ----------
        npy_path : str or Path
            The file path to the `.npy` file (e.g., `F.npy` or `Fneu.npy`)
    
    Returns:
    ----------
        dict : 
            The loaded dictionary from the `.npy` file.
    
    Example:
    ----------
        >>> load_npy_dict('data/stat.npy')
        {'key1': value1, 'key2': value2}
    """
    return np.load(npy_path, allow_pickle=True)[()] 

def check_for_suite2p_output(folder_name_list):
    """
    Verifies whether each folder in a list of folders contains Suite2p-style output files.
    
    This function checks if the `stat.npy` file exists in each folder in the provided `folder_name_list`.
    If any folder does not contain the required output files, the function will return `False`.
    
    Args:
    ----------
        folder_name_list : list of str
            A list of folder paths to check for Suite2p output files
    
    Returns:
    ----------
        boolean : `True` if all folders contain the required Suite2p files, `False` otherwise
    
    Example:
    ----------
        >>> check_for_suite2p_output(['/path/to/folder1', '/path/to/folder2'])
        True
    """

    for folder in folder_name_list:
        location = os.path.join(folder, *SUITE2P_STRUCTURE["stat"])
        if os.path.exists(location):
            continue
        if not os.path.isfile(os.path.join(folder, location)):
            return False
    return True


def check_deltaF(folder_name_list, config):
    """
    Checks if `deltaF.npy` exists in each folder in a list. If deltaF.npy does not exist the pipeline will calculate and generate it.
    
    This function checks each folder in the `folder_name_list` to see if the `deltaF.npy` file exists. If it doesn't,
    the function will automatically calculate and generate `deltaF.npy` using the `detector_utility.calculate_deltaF` function.
    
    Args:
    ----------
        folder_name_list : list of str
            A list of folder paths containing Suite2p-generated files
            
    Returns:
    ----------
        None : 
            If `deltaF.npy` is missing, it will be calculated and generated automatically
    
    Example:
    ----------
        >>> check_deltaF(['/path/to/folder1', '/path/to/folder2'])
    """
    for folder in folder_name_list:
        location = os.path.join(folder, *SUITE2P_STRUCTURE["deltaF"])
        if os.path.exists(location):
            continue
        elif not config.analysis_params.baseline_correction:
            g_func.calculate_deltaF(location.replace("deltaF.npy","F.npy"), config=config)
            if os.path.exists(location):
                continue
        elif config.analysis_params.baseline_correction and config.analysis_params.correction_method == 'airPLS':
            g_func.calculate_deltaF_airPLS(location.replace("deltaF.npy","F.npy"), config=config, 
                                           event_threshold=config.analysis_params.MAD_baseline_filter_threshold,
                                           lambda_window=config.analysis_params.lambda_window)
            if os.path.exists(location):
                continue
        elif config.analysis_params.baseline_correction and config.analysis_params.correction_method == 'rolling median':
            g_func.rolling_correction_deltaF(location.replace("deltaF.npy","F.npy"), config = config,
                                             event_threshold= config.analysis_params.MAD_baseline_filter_threshold,
                                             lambda_window=config.analysis_params.lambda_window)
            if os.path.exists(location):
                continue
            else:
                print("something went wrong, please calculate delta F manually by inserting the following code above: \n F_files = get_file_name_list(folder_path = main_folder, file_ending = 'F.npy') \n for file in F_files: calculate_deltaF(file)")

def check_network_deltaF(folder_name_list, config):
    """
    Checks if a `network_deltaF.npy` file exists in each folder in a list. If network_deltaF.npy does not exist the pipeline will calculate and generate it.
    
    This function checks each folder in the `folder_name_list` to see if the `deltaF.npy` file exists. If it doesn't,
    the function will automatically calculate and generate `deltaF.npy` using the `detector_utility.calculate_deltaF` function.
    
    Args:
    ----------
        folder_name_list : list of str
            A list of folder paths containing Suite2p-generated files.
            
    Returns:
    ----------
        None : 
            If `network_deltaF.npy` is missing, it will be calculated and generated automatically.
    
    Example:
    ----------
        >>> check_network_deltaF(['/path/to/folder1', '/path/to/folder2'])
    """
    for folder in folder_name_list:
        location = os.path.join(folder, *SUITE2P_STRUCTURE["network_deltaF"])
        if os.path.exists(location):
            continue
        else:
            g_func.calculate_network_deltaF(location.replace("F_network_normalized.npy","F.npy"), config = config)
            
        # elif config.analysis_params.baseline_correction and config.analysis_params.correction_method == 'airPLS':
        #     g_func.calculate_deltaF_airPLS(location.replace("network_deltaF.npy","F.npy"), config = config,
        #                                    event_threshold=config.analysis_params.MAD_baseline_filter_threshold)
        #     if os.path.exists(location):
        #         continue
        # elif config.analysis_params.baseline_correction and config.analysis_params.correction_method == 'rolling median':
        #     g_func.rolling_correction_deltaF(location.replace("network_deltaF.npy","F.npy"), config = config,
        #                                      event_threshold= config.analysis_params.MAD_baseline_filter_threshold,
        #                                      lambda_window=config.analysis_params.lambda_window)
        #     if os.path.exists(location):
        #         continue

def get_file_name_list(folder_path, file_ending, supress_printing = False):
    """
    Searches the given parent folder for specific Suite2p-generated files or subfolders containing recordings.
    
    This function recursively searches the `folder_path` for files matching the specified `file_ending` (e.g., `F.npy`,
    `deltaF.npy`, `predictions_deltaF.npy` or `samples`). It can also return subfolders containing both image and Suite2p analysis files.
    
    Args:
    ----------
        folder_path: str / Path
            The root folder path to search for Suite2p files.
        file_ending : str
            The file type to search for. Accepted values: `F.npy`, `deltaF.npy`, `samples`
        config : SimpleNameSpace dict 
            Configurations should be loaded separately with  config_loader.load_json_config_file(file = None)
        suppress_printing : bool, optional
            Whether to suppress printing the found files/folders. Defaults to `False`
    
    Returns:
    ----------
        list of str : A list of file or folder paths matching the specified `file_ending`.
    
    Example:
    ----------
        >>> get_all_suite2p_outputs_in_path('/path/to/data', 'F.npy')
        ['/path/to/data/subject1/suite2p/plane0/F.npy', '/path/to/data/subject2/suite2p/plane0/F.npy']
        >>> get_all_suite2p_outputs_in_path('/path/to/data', 'samples')
        ['/path/to/data/subject1', '/path/to/data/subject2']
    """

    #TODO check if `config` should be added as a variable to this function
    file_names = []
    other_files = []
    try:
        config = load_json_config_file(folder_path)
    except FileNotFoundError as e:
        config = load_json_config_file()

    
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file_ending=="F.npy" and file.endswith(file_ending) and not file.endswith("deltaF.npy"):
                    file_names.append(os.path.join(root, file))
            elif file_ending=="deltaF.npy" and file.endswith(file_ending) and not file.endswith("predictions_deltaF.npy"):
                    file_names.append(os.path.join(root, file))
            elif file_ending=="predictions_deltaF.npy" and file.endswith(file_ending):
                 file_names.append(os.path.join(root, file))
            elif file_ending=="samples":
                if file.endswith("stat.npy"):
                    file_names.append(os.path.join(root, file)[:-24])
            else:
                 if file.endswith(file_ending): other_files.append(os.path.join(root, file))
    if file_ending=="F.npy" or file_ending=="deltaF.npy" or file_ending=="predictions_deltaF.npy":
        if not supress_printing:
            print(f"{len(file_names)} {file_ending} files found:")
            print(file_names)
        return file_names
    elif file_ending=="samples":
        check_deltaF(file_names, config)  #checks if deltaf exists, else calculates it
        if not supress_printing:
            print(f"{len(file_names)} folders containing {file_ending} found:")
            print(file_names)
        return file_names
    else:
        print("Is the file ending spelled right?")
        return other_files

def get_experimental_dates(main_folder):
    """
    Extract experimental dates from folder names and assign replicates to each unique date.
    
    This function scans the folder names in `main_folder` and extracts the dates from the beginning of each folder name.
    It then assigns each unique date a corresponding replicate number (e.g., `sample1`, `sample2`).
    
    Args:
    ----------
        main_folder : str / Path-like Object
            The path to the main folder containing subfolders with experiment data.
    
    Returns:
    ----------
        dict : A dictionary mapping each folder path to its corresponding sample/replicate number.
    S
    Example:
    ----------
        >>> get_experimental_dates('/path/to/main_folder')
        {'/path/to/main_folder/experimental_condition/251030_file_image': 'sample_1', '/path/to/main_folder/experimental_condition/251126_file_image': 'sample_2'}
    """
    well_folders = get_file_name_list(main_folder, "samples", supress_printing = True)
    date_list= []
    sample_dict = {}
    try:
        for well in well_folders:
            date_list.append(os.path.basename(well)[0:6]) #date_list.append(os.path.basename(well).split("_")[0]) ## append dates; should change if the date is not in the beginning of the file name usually [:6]
        distinct_dates = [i for i in set(date_list)]
        distinct_dates.sort(key=lambda x: int(x))
    except (TypeError, ValueError) as e:
        for well in well_folders:
            date_list.append('000123')
        distinct_dates = [i for i in set(date_list)]
        # distinct_dates.sort(key=lambda x: int(x))
        
    for i1 in range(len(well_folders)):
        for i2, date in enumerate(distinct_dates):
            if date in well_folders[i1]: # if date in list
                sample_dict[well_folders[i1]]=f"sample_{i2+1}"

    return sample_dict

def df_from_suite2p_dict(suite2p_dict, config): ## creates df structure for single sample (e.g. well_x) csv file, input is dict resulting from load_suite2p_paths
    """
    Translate Suite2p output dictionaries into raw and processed DataFrames.

    Event detection, amplitude extraction, decay extraction, and ROI
    classification are performed using detector and plotting utilities.

    Args:
    -----
        suite2p_dict : dict
            Dictionary produced by suite2p_utility.load_suite2p_output().
        config : SimpleNameSpace dict
            configurations.json file
    Returns:
    --------
        tuple of pandas.DataFrame
            (raw_df, processed_df)
            raw_df : unfiltered ROI data
            processed_df : ROIs with full computed metrics and filtering applied

    """

    ## spike_amplitudes = find_predicted_peaks(suite2p_dict["cascade_predictions"], return_peaks = False) ## removed
    # spikes_per_neuron = find_predicted_peaks(suite2p_dict["cascade_predictions"]) ## removed
    masked_cascade_prediction = np.array(g_func.filter_cascade_predictions(suite2p_dict['cascade_predictions'], config))
    estimated_spike_total = np.array(g_func.summed_spike_probs_per_cell(masked_cascade_prediction))
    # estimated_spike_std = np.std(np.array(summed_spike_probs_per_cell(suite2p_dict["cascade_predictions"])))
    basic_cell_stats = g_func.basic_estimated_stats_per_cell(masked_cascade_prediction)
    F_baseline = g_func.return_baseline_F(suite2p_dict["F"], suite2p_dict["Fneu"])
    avg_instantaneous_spike_rate, avg_cell_sds, avg_cell_cvs, avg_time_stamp_mean, avg_time_stamp_sds, avg_time_stamp_cvs = g_func.basic_stats_per_cell(masked_cascade_prediction)
    activity_threshold = config.analysis_params.cascade_activity_threshold
    activity_mask = []
    for spike_total in estimated_spike_total:
        activity_mask.append(spike_total >= activity_threshold)
   
    df = pd.DataFrame({
                       "Baseline_F": F_baseline,
                       "EstimatedSpikes": estimated_spike_total,
                       "SD_Estimated_Spks":basic_cell_stats[1],
                       "cv_Estimated_Spks":basic_cell_stats[2],
                       "Total Frames": len(suite2p_dict["F"].T), 
                       "SpikesFreq": avg_instantaneous_spike_rate, 
                       "group": suite2p_dict["Group"],
                       "dataset":suite2p_dict["sample"],
                       "file_name": suite2p_dict["file_name"]},
                       index = range(0,len(suite2p_dict["F"])))
    
    
    df.index.set_names("NeuronID", inplace=True)
    use_iscell = config.analysis_params.use_suite2p_ROI_classifier
    if use_iscell:
        df["IsUsed"] = suite2p_dict["iscell"][:,0]

    else:
        fluorescence_keys = []
        stat = suite2p_dict['stat']
        F = suite2p_dict['F']
        Fneu = suite2p_dict['Fneu']
        for n in range(stat.shape[0]): #         for n in range(stat.shape[0]):

            radius = stat.iloc[n]['radius']

            sample_F = F[n]
            sample_Fneu = Fneu[n]

            med_pixel_weight = np.median(stat.iloc[n]['lam'])
            if med_pixel_weight > 0.5 and radius > 3 and sample_F.min() > sample_Fneu.min():
                fluorescence_keys.append(True)
            else:
                fluorescence_keys.append(False)
        df['IsUsed'] = fluorescence_keys
    df["ActiveROI"] = (df["EstimatedSpikes"] > 0.1) & (df['IsUsed'] == True)
    df.index.set_names("NeuronID", inplace=True)
    
    return df

def load_suite2p_paths(data_folder, config, use_iscell = False):  ## creates a dictionary for the suite2p paths in the given data folder (e.g.: folder for well_x)
    """
    Load all Suite2p output files for a given recording into a single dictionary.

    This includes fluorescence traces, neuropil signals, ROI statistics,
    Suite2p processing options, and classification arrays. Optionally replaces
    Suite2p's ``iscell.npy`` classification with user-defined skew-thresholding.

    Args:
    ----------
        data_folder : str or Path
            Path to the folder containing the Suite2p output directory.
        groups : list of str
            Names of experimental groups present inside ``main_folder``.
        main_folder : str or Path
            Root directory containing all experimental condition folders.
        use_iscell : bool, optional
            If ``True``, use Suite2p's ``iscell.npy`` array for ROI selection.
            If ``False`` (default), compute ``IsUsed`` via skewness thresholding.

    Returns:
    ----------
        dict
            Dictionary containing all Suite2p arrays and metadata associated with
            the recording, including assigned group and replicate label.
    Example:
    ----------
            >>> load_suite2p_output('/path/to/data_folder', config_dict['general_settings']['groups'], config_dict['general_settings']['main_folder'], use_iscell = False)
            {"F": [5,6,7,8...],
            "Fneu": [0,1,2,3...],
            "stat": {npix: [7], skew: [0.56], radius: 25,...}
            "ops": {dict}
            "iscell": 2D array [[1, 0.5602], [0, 0.1123]...],
            "deltaF": [0.25, 0.5, 0.67, 0.012,...],
            "IsUsed": [True, False, True, True, False, False, ...],
            "Group": 'Experimental_Treatment_Condition',
            "sample": 'Replicate01',
            "file_name": '202511_this_is_the_calcium_imaging_video_file_w_extension" 
            }
        
    """
    suite2p_dict = {
        "F": load_npy_array(os.path.join(data_folder, *SUITE2P_STRUCTURE["F"])),
        "Fneu": load_npy_array(os.path.join(data_folder, *SUITE2P_STRUCTURE["Fneu"])),
        "stat": load_npy_df(os.path.join(data_folder, *SUITE2P_STRUCTURE["stat"]))[0].apply(pd.Series),
        "ops": load_npy_array(os.path.join(data_folder, *SUITE2P_STRUCTURE["ops"])).item(),
        "deltaF": load_npy_array(os.path.join(data_folder, *SUITE2P_STRUCTURE['deltaF'])),
        "cascade_predictions": load_npy_array(os.path.join(data_folder, *SUITE2P_STRUCTURE["cascade_predictions"])),
        "iscell": load_npy_array(os.path.join(data_folder, *SUITE2P_STRUCTURE['iscell'])),
        "network_deltaF": load_npy_array(os.path.join(data_folder, *SUITE2P_STRUCTURE['network_deltaF']))

    }
    if config.analysis_params.use_suite2p_ROI_classifier is False or use_iscell is False:
        fluorescence_keys = []
        stat = suite2p_dict['stat']
        F = suite2p_dict['F']
        Fneu = suite2p_dict['Fneu']
        for n in range(stat.shape[0]): #         for n in range(stat.shape[0]):

            radius = stat.iloc[n]['radius']

            sample_F = F[n]
            sample_Fneu = Fneu[n]

            med_pixel_weight = np.median(stat.iloc[n]['lam'])
            if med_pixel_weight > 0.5 and radius > 3 and sample_F.min() > sample_Fneu.min():
                fluorescence_keys.append(True)
            else:
                fluorescence_keys.append(False)

    else:
        print(f"Sample: {data_folder}")
        print(f"iscell shape: {suite2p_dict['iscell'].shape}")
        print(f"iscell dtype: {suite2p_dict['iscell'].dtype}")
        try:

            suite2p_dict['IsUsed'] = suite2p_dict['iscell'][:,0].astype(bool)
        except IndexError as e:
            suite2p_dict['IsUsed'] = suite2p_dict['iscell']
 #TODO make sure that changing "path" to "data_folder" for using IsCell natively will still work
    suite2p_dict['data_folder'] = data_folder

    main_folder = str(config.general_settings.main_folder)
    groups = config.general_settings.groups

    if not groups:
        raise ValueError("The 'groups' list is empty. Please provide valid group names.")
    print(f"Data folder: {data_folder}")
    print(f"Groups: {groups}")
    print(f"Main folder: {main_folder}")
    found_group = False
    if groups is not None:
        for group in groups: ## creates the group column based on groups list from configurations file
            if (str(group)) in data_folder:
                group_name = group.split(main_folder)[-1].strip("\\/")
                suite2p_dict["Group"] = group_name
                found_group = True
                print(f"Assigned Group: {suite2p_dict['Group']}")
        
    # debugging
    if "iscell" not in suite2p_dict:
        raise KeyError ("'IsUsed' was not defined correctly either")
    sample_dict = get_experimental_dates(main_folder) ## creates the sample number dict
   
    suite2p_dict["sample"] = sample_dict[data_folder]  ## gets the sample number for the corresponding well folder from the sample dict
 
    suite2p_dict["file_name"] = str(os.path.join(data_folder.split('\\')[-1], *SUITE2P_STRUCTURE["cascade_predictions"]))
 
    return suite2p_dict

def load_local_suite2p_output(data_folder, groups = None, main_folder = None, load_local_suite2p = True, use_iscell = False):  ## creates a dictionary for the suite2p paths in the given data folder (e.g.: folder for well_x)
    """
    Load an example Suite2p output file from a local directory without needing to open a configurations file.

    This includes fluorescence traces, neuropil signals, ROI statistics,
    Suite2p processing options, and classification arrays. Optionally replaces
    Suite2p's ``iscell.npy`` classification with user-defined skew-thresholding.

    Args:
    ----------
        data_folder : str or Path
            Path to the folder containing the Suite2p output directory.
        groups : list of str
            Names of experimental groups present inside ``main_folder``.
        main_folder : str or Path
            Root directory containing all experimental condition folders.
        use_iscell : bool, optional
            If ``True``, use Suite2p's ``iscell.npy`` array for ROI selection.
            If ``False`` (default), compute ``IsUsed`` via skewness thresholding.

    Returns:
    ----------
        dict
            Dictionary containing all Suite2p arrays and metadata associated with
            the recording, including assigned group and replicate label.
    Example:
    ----------
            >>> load_local_suite2p_output('/path/to/data_folder', 
                                          groups = None, main_folder = None, 
                                          load_local_suite2p = True, use_iscell = True)
            {"F": [5,6,7,8...],
            "Fneu": [0,1,2,3...],
            "stat": {npix: [7], skew: [0.56], radius: 25,...}
            "ops": {dict}
            "iscell": 2D array [[1, 0.5602], [0, 0.1123]...],
            "deltaF": [0.25, 0.5, 0.67, 0.012,...],
            "IsUsed": [True, False, True, True, False, False, ...],
            "Group": 'Experimental_Treatment_Condition',
            "sample": 'Replicate01',
            "file_name": '202511_this_is_the_calcium_imaging_video_file_w_extension" 
            }
        
    """
    suite2p_dict = {
        "F": load_npy_array(os.path.join(data_folder, *SUITE2P_STRUCTURE["F"])),
        "Fneu": load_npy_array(os.path.join(data_folder, *SUITE2P_STRUCTURE["Fneu"])),
        "stat": load_npy_df(os.path.join(data_folder, *SUITE2P_STRUCTURE["stat"]))[0].apply(pd.Series),
        "ops": load_npy_array(os.path.join(data_folder, *SUITE2P_STRUCTURE["ops"])).item(),
        "deltaF": load_npy_array(os.path.join(data_folder, *SUITE2P_STRUCTURE['deltaF'])),
        "cascade_predictions": load_npy_array(os.path.join(data_folder, *SUITE2P_STRUCTURE["cascade_predictions"])),
        "iscell": load_npy_array(os.path.join(data_folder, *SUITE2P_STRUCTURE['iscell'])),
        "network_deltaF": load_npy_array(os.path.join(data_folder, *SUITE2P_STRUCTURE['network_deltaF']))

}
    if not use_iscell:
        suite2p_dict["IsUsed"] = [(suite2p_dict["stat"]["skew"] >= 1)] 

    else:
        suite2p_dict["IsUsed"] = pd.DataFrame(suite2p_dict["iscell"]).iloc[:,0].values.T
        suite2p_dict["IsUsed"] = np.squeeze(suite2p_dict["iscell"])
        suite2p_dict['IsUsed'] = suite2p_dict['iscell'][:,0].astype(bool)
 #TODO make sure that changing "path" to "data_folder" for using IsCell natively will still work
    suite2p_dict['data_folder'] = data_folder

    if load_local_suite2p:
        main_folder = suite2p_dict['data_folder'].split('\\')[:-2]
        main_folder = "\\".join(main_folder)

        print(main_folder)
        groups = suite2p_dict['data_folder'].split("\\")[0:-1]
        groups = ["\\".join(groups)]
    if not groups:
        raise ValueError("The 'groups' list is empty. Please provide valid group names.")
    print(f"Data folder: {data_folder}")
    print(f"Groups: {groups}")
    print(f"Main folder: {main_folder}")
    found_group = False
    if groups is not None:
        for group in groups: ## creates the group column based on groups list from configurations file
            if (str(group)) in data_folder:
                group_name = group.split(main_folder)[-1].strip("\\/")
                suite2p_dict["Group"] = group_name
                found_group = True
                print(f"Assigned Group: {suite2p_dict['Group']}")
        
    # debugging
    if "iscell" not in suite2p_dict:
        raise KeyError ("'IsUsed' was not defined correctly either")
    # if "Group" not in suite2p_dict:
    #     raise KeyError("'Group' key not found in suite2p_dict.")
    #     #TODO find a way to ignore files not in the group list if manually removed
    # if not found_group:
    #     raise KeyError(f"No group found in the data_folder path: {data_folder}")
    suite2p_dict["file_name"] = str(os.path.join(data_folder.split('\\')[-1], *SUITE2P_STRUCTURE["cascade_predictions"]))

    if main_folder is not None:
        sample_dict = get_experimental_dates(main_folder) ## creates the sample number dict
   
        suite2p_dict["sample"] = sample_dict[data_folder]  ## gets the sample number for the corresponding well folder from the sample dict
    else:
        suite2p_dict['sample'] = suite2p_dict['file_name'].split('\\')[-1]
 
    return suite2p_dict


def translate_suite2p_outputs_to_csv(main_folder, config, overwrite=False, check_for_iscell=False, update_iscell = True): ## creates output csv for all wells and saves them in .csv folder
    """
    Convert Suite2p output folders into raw and processed CSV files.

    Args:
    --------
        main_folder : str
            Path containing Suite2p output folders.
        check_for_iscell : bool, optional
            Whether to classify ROIs using Suite2p's iscell.npy.
        update_iscell : bool, optional
            Whether to overwrite the iscell.npy file based on reclassification.

    Returns:
    --------
        None

    """

    well_folders = get_file_name_list(main_folder, "samples", supress_printing = True)

    output_path = os.path.join(main_folder, "csv_files")

    if not os.path.exists(output_path):
        os.mkdir(output_path)
    
    for folder in well_folders:
        output_directory = (os.path.relpath(folder, main_folder)).replace("\\", "-")
        translated_path = os.path.join(output_path, f"{output_directory}.csv")
        if os.path.exists(translated_path) and not overwrite:
            print(f"CSV file {translated_path} already exists!")
            continue

        suite2p_dict = load_suite2p_paths(folder, config)

        output_df = df_from_suite2p_dict(suite2p_dict, config)
    

        output_df.to_csv(translated_path)
        print(f"csv created for {folder}")

        ops = suite2p_dict["ops"]
        Img = fun_plot.getImg(ops)
        scatters, nid2idx, nid2idx_rejected, pixel2neuron,nid2idx_neuron, nid2idx_glia = fun_plot.getStats(suite2p_dict, Img.shape, output_df, config, use_iscell=check_for_iscell)
        iscell_path = os.path.join(folder, *SUITE2P_STRUCTURE['iscell'])
        parent_iscell = load_npy_array(iscell_path)
        print("parent_iscell type:", type(parent_iscell))
        print("parent_iscell shape:", np.shape(parent_iscell))
        updated_iscell = parent_iscell.copy()
        # update_iscell[nid2idx, 0] = 1.0
        # update_iscell[nid2idx_rejected, 0] = 0.0
        if update_iscell:
            for idx in nid2idx:
                updated_iscell[idx, 0] = 1.0  # Update only the first column
            for idxr in nid2idx_rejected:
                updated_iscell[idxr, 0] = 0.0

            np.save(iscell_path, updated_iscell)
            print(f"Updated iscell.npy saved for {folder}")

        else:
            print("Using iscell from suite2p to classify ROIs")

        
        image_save_path = os.path.join(main_folder, f"{folder}_plot.png") #TODO explore changing "input path" to "folder" to save the processing in the same 
        fun_plot.dispPlot(Img, scatters, nid2idx, nid2idx_rejected, pixel2neuron, nid2idx_neuron, nid2idx_glia,suite2p_dict["F"], suite2p_dict["Fneu"], image_save_path)

    print(f"{len(well_folders)} .csv files were saved under {config.general_settings.main_folder+r'/csv_files'}")

def get_pkl_file_name_list(folder_path): 
    """
    Get all pickle (.pkl) files from a given folder path into a list of files.

    Args:
    --------
        folder_path : str
            Path containing pickle (.pkl) output files

    Returns:
    --------
        pkl_files : list
            List of pkl files from the provided `folder_path`
    """
    pkl_files = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".pkl"):
                pkl_files.append(os.path.join(root, file))
    return pkl_files


def list_all_files_of_type(input_path, filetype):
    """
    List all files in a directory with a specific extension.

    Args:
    -----
        input_path : str
            Directory to search.
        filetype : str
            File extension filter.

    Returns:
    --------
        list of str
            Filenames matching the requested extension.

    """

    return [os.path.join(input_path, path) for path in os.listdir(input_path) if path.endswith(filetype)]

def csv_to_pickle(main_folder, overwrite=True):
    """
    Convert spike CSV files into pickled analysis dictionaries.

    Args:
    -----
        input_path : str
            Path containing a 'csv_files' directory.

    Returns:
    --------
        None

    """

    csv_files = list_all_files_of_type(main_folder+r"/csv_files", ".csv")
    print((csv_files))
    output_path = main_folder+r"/pkl_files"
    if not os.path.exists(output_path):
        os.mkdir(output_path)

    for file in csv_files:
        df = pd.read_csv(file)
        pkl_path = os.path.join(output_path, 
                                        f"{os.path.basename(file[:-4])}"
                                        f"Dur{int(config.general_settings.EXPERIMENT_DURATION)}s"
                                        f"Int{int((1/config.general_settings.frame_rate)*1000)}ms"
                                        f"Bin{int(config.general_settings.BIN_WIDTH*1000)}ms"
                                         +
                                        ".pkl")
        if os.path.exists(pkl_path) and not overwrite:
            print(f"Processed file {pkl_path} already exists!")
            continue

        df.to_pickle(pkl_path)
        print(f"{pkl_path} created")
    print(f".pkl files saved under {main_folder+r'/pkl_files'}")

def create_final_df(main_folder):
    """
    Create a dataframe containing the analysis of all calcium imaging recordings present in the Experiment folder (main_folder).

    Args:
    --------
        main_folder : str
            Path to main_folder or Experiment folder containing all calcium imaging recordings to process. 

    Returns:
    --------
        None

    """
    
    pkl_files = get_pkl_file_name_list(main_folder)
    df_list = []
    for file in pkl_files:
        df = pd.read_pickle(file)
        df_list.append(df)
    final_df = pd.concat(df_list, ignore_index=True)
    if len(get_file_name_list(main_folder, "samples")) != len(pkl_files):
        raise Exception("The amount of .pkl files doesn't match the amount of samples, please delete all .csv and .pkl files and start over") ##Check this exception later
    return final_df
    ##alternative df from cell_stats dict, add previous functions back in then

def calculate_iqr_and_outliers(data):
    """
    Calculate IQR for a 1D input array (e.g., fluorescence trace, processed data, etc.)
    
    Args:
    --------
        data : 1D NumPy array
            1D array or column of pd.DataFrame from which median, Q1, Q3 and IQR can be calculated

    Returns:
    --------
        None

    """
    try:
        Q1 = np.percentile(data, 25)
        Q3 = np.percentile(data, 75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        outliers = ((data < lower_bound) | (data > upper_bound))
    except IndexError as e:
        Q1, Q3, IQR, lower_bound, upper_bound, outliers = np.nan() 
    return IQR, len(outliers)

def get_unique_prefixes(group_names, prefix_length=3):
    """
    Function to extract unique prefixes which correspond to unique treatments / timepoints for imaging

    Args:
    --------
        group_names : list
            Group names corresponds to a list of groups to process (usually subfolders containing multiple repeats of images)
        prefix_length : int, default = 3
            length of characters to assign as the prefix or time_point of each image

    Returns:
    --------
        dict : {name[:prefix_length] for name in group_names}

    """
    return {name[:prefix_length] for name in group_names}

def create_experiment_overview(main_folder, groups, use_iscell):
    """
    Final step in post-processing where csv files are generated for each file describing the overall activity of the cultures.
    
    Args:
    --------
        main_folder : str
            Path-like Object for the main folder containing all image folders and analysis
        groups : list
            List of subfolders (one-level-down) from main_folder that contain image file folders and/or multivid file folders
        use_iscell : boolean
            Whether or not to use the Suite2p classification of ROIs as cells or not cells; alternative is to use activity/based or morphology
            based measurements

    Returns:
    --------
        df : pd.DataFrame
            Pandas DataFrame containing all analyzed parameters for each image file
        summary_stats : pd.DataFrame (aggregated)
            Pandas DataFrame aggregated by Group and time_point including mean, median, and standard deviation calculations
    
    Workflow:
    --------
        1) Find all Cascade deconvolution (predictions_deltaF.npy) files
        2) For each Cascade prediction file, load all other suite2p output files
            (e.g., F, Fneu, iscell) 
        3) Calculate baseline fluorescence (from functions_general.return_baseline_F)
        4) Calculate cell instantaneous spike rate, sd, cv, and time_stamp means, sds, and cvs 
            through general_functions.basic_stats_per_cell function
        5) Mask array of neurons with iscell mask to return average active and inactive baseline (#TODO NEED TO UPDATE THIS)
        6) Create a dictionary containing all of the calculated data for individual cells
        7) Create an DataFrame from the dictionary
        8) Aggregate the DataFrame by treatment group and timepoint and calculate mean, median and std. dev. for all parameters
        9) Save the aggregated and base DataFrame to csv files in the main_folder
    """
    dictionary_list = []
    
    for group in groups:
        groups_predictions_deltaF_files = get_file_name_list(folder_path=os.path.join(config.general_settings.main_folder, group), 
                                                             file_ending="predictions_deltaF.npy", supress_printing=True)
        
        for file in groups_predictions_deltaF_files:
            
            # Load F, Fneu arrays
            F_file = file.replace('predictions_deltaF.npy', 'F.npy')
            iscell_file = file.replace('predictions_deltaF.npy', 'iscell.npy')
            Fneu_file = file.replace('predictions_deltaF.npy', 'Fneu.npy')
            F = np.load(rf"{F_file}", allow_pickle=True)
            Fneu = np.load(rf"{Fneu_file}", allow_pickle=True)
            baseline_F = g_func.return_baseline_F(F, Fneu)
            iscell = np.load(rf"{iscell_file}", allow_pickle=True)
            iscell_mask = iscell[:,0] == 1

            array = np.load(rf"{file}", allow_pickle=True)
            avg_cell_instantaneous_spike_rate, cell_sds, cell_cvs, time_stamp_means, time_stamp_sds, time_stamp_cvs = g_func.basic_stats_per_cell(array)
            neuron_count = len(array)
        

            if not use_iscell:
                active_neurons = sum(np.nansum(row) > 0.1 for row in array)
            # Separate and average the baseline fluorescence
                inactive_baseline = [cell for row, cell in zip(array, baseline_F) if np.nansum(row) < 0.1]
                active_baseline = [cell for row, cell in zip(array, baseline_F) if np.nansum(row) >= 0.1]
                estimated_spikes = [np.nansum(row) for row in array]


            else:
                active_neurons = sum(iscell[:,0] == 1)
                inactive_baseline = [cell for i, cell in enumerate(baseline_F) if iscell[i, 0] == 0]
                active_baseline = [cell for i, cell in enumerate(baseline_F) if iscell[i, 0] == 1]
                estimated_spikes = [np.nansum(row) for row, true_mask in zip(array, iscell_mask) if true_mask]

            avg_inactive_cell = np.nanmean(inactive_baseline)
            avg_active_cell = np.nanmean(active_baseline)
            total_estimated_spikes = round(sum(estimated_spikes), 2)
                    
            dictionary_list.append({
                'Prediction_File': file[len(main_folder)+1:], 
                'Neuron_Count': neuron_count,
                'Active_Neuron_Count': active_neurons, 
                'Active_Neuron_Proportion': round(active_neurons/neuron_count * 100, 2),
                'Active_Neuron_F0': avg_active_cell,
                "Inactive_Neuron_F0": avg_inactive_cell,
                'Total_Estimated_Spikes': total_estimated_spikes, 
                "Total_Estimated_Spikes_proportion_scaled": total_estimated_spikes / (active_neurons/neuron_count),
                'Avg_Estimated_Spikes_per_cell': total_estimated_spikes / active_neurons,
                "SC_Avg_Instantaneous_Firing_Rate(Hz)": avg_cell_instantaneous_spike_rate,
                "Instantaneous_Spikes_CV": cell_cvs,
                "Network_Framewise_Avg_Instantaneous_Firing_Freq": time_stamp_means,
                "Network_Framewise_CV": time_stamp_cvs,
                "Group": group[len(main_folder)+1:]
            })
    
    # Create DataFrame from dictionary list
    df = pd.DataFrame(dictionary_list)

    unique_prefixes = get_unique_prefixes(df['Group'])

    # Create a dynamic categorization function
    def categorize_time_point(group_name):
        """
        Iterator function to look through DataFrame column ('Group') for matching prefixes

        Args:
        --------
            group_name : str
                Name of subfolder one-level-down in main_folder which contains images and the prefix for the time_point of imaging
        Returns:
        --------
            Prefix : str
                3-character string of the time-point of a given recording
            N/A : NULL
                If no prefix exists for the given group or does not match, function returns "N/A"
     
        """
        for prefix in unique_prefixes:
            if group_name.startswith(prefix):
                return prefix
        return 'N/A'

    # Add a new column 'Time_Point' based on the unique prefixes
    df['Time_Point'] = df['Group'].apply(categorize_time_point)

    # Ensure 'N/A' categories are handled
    df = df[df['Time_Point'] != 'N/A']
    # Calculate summary statistics for each unique group
    summary_stats = df.groupby(['Group', 'Time_Point']).agg({
        'Neuron_Count': ['mean', 'std','median'],
        'Active_Neuron_Count': ['mean', 'std','median'],
        'Active_Neuron_Proportion': ['mean', 'std','median'],
        'Active_Neuron_F0': ['mean', 'std','median'],
        'Inactive_Neuron_F0': ['mean', 'std','median'],
        'Total_Estimated_Spikes': ['mean', 'std','median'],
        'Total_Estimated_Spikes_proportion_scaled': ['mean', 'std','median'],
        'Avg_Estimated_Spikes_per_cell': ['mean', 'std','median'],
        "SC_Avg_Instantaneous_Firing_Rate(Hz)": ['mean', 'std','median'],
        "Instantaneous_Spikes_CV": ['mean', 'std','median'],
        "Network_Framewise_Avg_Instantaneous_Firing_Freq": ['mean', 'std','median'],
        "Network_Framewise_CV": ['mean', 'std','median']
    })

    # Save both raw data and summary statistics to CSV
    experiment_folder = str(config.general_settings.main_folder).split('\\')[-1]
    df.to_csv(os.path.join(main_folder, f'{experiment_folder}_experiment_summary.csv'), index=False)
    summary_stats.to_pickle(os.path.join(main_folder, 'summary_stats.pkl'))
    summary_stats.to_csv(os.path.join(main_folder, 'summary_stats.csv'), index = True)

    return df, summary_stats
