import os
import numpy as np
import tqdm
from pathlib import Path
from PIL import Image
import shutil
import sys
# sys.path.insert(0, 'D:/users/JC/suite2p-0.14.0')
from suite2p import run_s2p
from batch_gui.config_loader import load_json_config_file, load_json_dict
from run_cascade import functions_data_transformation
# import convert_nd2_to_tiff

_DEFAULT_CONFIG = load_json_config_file()
config = _DEFAULT_CONFIG

def export_image_files_to_suite2p_format(parent_directory, file_ending =  config.general_settings.data_extension):
    """
    Move image files into their own subfolders.
     
    This function takes image files with a given file extension and copies them into
    their own subfolder to give 1 image per subfolder where the image name is preserved
    in the folder name itself. This is necessary for Suite2p processing without the settings
    'look_one_level_down'.

    Args:
    ----------
        parent_directory : path / str
            Path-like object pointing to main folder to search through
        file_ending : str
            File type / file ending for image file
            example endings ('nd2', 'tif')

    Returns:
    ----------
        Files organized in the following tree
            /path/to/parent_folder
            ├───experiment_condition_folder_1
            │   ├───image_folder_1
            |        ├───image_1
            │   ├───image_folder_2
            |        ├───image_2              
            ├───experiment_condition_folder_2
            │   ├───image_folder_1
            |        ├───image_1
            │   ├───image_folder_2
            |        ├───image_2
    """

    if not os.path.exists(parent_directory):
        print(f"Provided path does not exist: {parent_directory}")
        return
    
    # Process each directory within the parent directory
    for dir_name in os.listdir(parent_directory):
        dir_path = os.path.join(parent_directory, dir_name)
        if not os.path.isdir(dir_path):
            print(f"Skipping non-directory path: {dir_path}")
            continue

        # Processing each file within the directory
        files = []
        for file in os.listdir(dir_path):
            if os.path.isfile(os.path.join(dir_path, file) and file.endswith(file_ending)):
                files.append(file)
            
            if len(files) == 0:
                print(f"No {file_ending} files in {dir_path}")
                continue

        for file in files:
                name, _ = os.path.splitext(file)
                folder_path = os.path.join(dir_path, name)
                os.makedirs(folder_path, exist_ok=True)

                source = os.path.join(dir_path, file)
                destination = os.path.join(folder_path, file)

                try:
                    shutil.copy2(source, destination)
                    os.remove(source)
                    print(f"Processed and moved {file} to {folder_path}")
                except Exception as e:
                    print(f"Failed to process {file} due to {e}")
            
def count_image_files_in_folder(current_path, file_ending):
    """
    Count the number of image files (or files with a certain file ending) present
    in the current path.

        Args:
    ----------
        current_path : path / str
            Path-like object pointing to a folder containing image files
        file_ending : str
            File type / file ending for image file
            example endings ('nd2', 'tif')

    Returns:
    ----------
        Count : int
            Number of files matching a file ending within a given folder
    """
    count = 0
    for file in os.listdir(current_path):
        if file.endswith(file_ending):
            count += 1
    return count

def get_all_image_folders_in_path(path, file_ending = config.general_settings.data_extension):
    """
    Find all folders within a given path that contain exactly one `.nd2` file in their deepest subfolder.

    This function traverses the directory tree from the specified `path`, identifies all the folders that
    contain exactly one `.nd2` file in the deepest subfolder, and returns a list of those folders.

    Args:
    ----------
        path : str
            The root directory path to begin the search from. The function will walk through all
            subdirectories starting from this path.

    Returns:
    ----------
        image_types : dict 
            A dictionary of either 'single' or 'concat' image paths that contain exactly one `.nd2` file in their deepest
            subfolder or multiple images per subfolder of each experiment conditions, respectively.

    Example:
        >>> get_all_image_folders_in_path("/home/user/images")
        ['/home/user/images/folder1', '/home/user/images/folder2']
    """
    image_types = {
        'single': [],
        'concat': []
    }

    found_image_folders = []
    for current_path, directories, files in os.walk(path):
        image_count = count_image_files_in_folder(current_path, file_ending)

        if image_count == 1:
            image_types['single'].append(current_path)
        elif image_count > 1:
            image_types['concat'].append(current_path)
    
    return image_types


def process_files_with_suite2p(image_list, ops):
    """
    Process a list of image folders using the Suite2p pipeline.

    This function wraps Suite2p’s ``run_s2p`` function and applies a user-provided
    ``ops`` dictionary to each image folder. A temporary fast-disk directory is
    created if needed to store Suite2p-generated binary files.

    Args:
    ----------
        image_list : list of str or Path
            List of folder paths containing images to be processed by Suite2p.
        ops : dict
            The Suite2p ``ops`` settings dictionary, typically loaded from ``ops.npy``.
    
    Returns:
    ----------
        None

    Notes:
    ----------
    Each item in ``image_list`` is treated as a separate Suite2p input folder.
    Any exceptions raised during Suite2p processing are caught and reported,
    allowing the loop to continue.
    """
    for image_path in image_list:
        try:
                fast_disk_path = r'C:\BIN'
                if not os.path.exists(fast_disk_path):
                    os.makedirs(fast_disk_path)
                db = {
                'h5py': [], # a single h5 file path
                'h5py_key': 'data',
                'look_one_level_down': False, # whether to look in ALL subfolders when searching for images
                'data_path': [image_path], # a list of folders with images 
                                                    # (or folder of folders with images if look_one_level_down is True, or subfolders is not empty)
                                                    
                'subfolders': [], # choose subfolders of 'data_path' to look in (optional)
                'fast_disk': fast_disk_path, # string which specifies where the binary file will be stored (should be an SSD)
                }
        
                opsEnd = run_s2p(ops=ops, db=db)
        except (ValueError, AssertionError, IndexError, Exception) as e:
                print(f"Error processing {image_path}: {e}")

def main(config_file = None):
    """
    Run Suite2p preprocessing and analysis based on an (optional) configuration file.

    This function loads a JSON configuration, prepares Suite2p-compatible image
    folders, processes unprocessed recordings with Suite2p, and prepares recordings
    to be processed further by Cascade downstream in another virtual environment.
    A copy of the analysis configuration is saved as ``analysis_config.json`` 
    inside the main experiment folder.

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
        1. Load configuration and ``ops.npy`` Suite2p settings.
        2. Export raw images into Suite2p format.
        3. Identify all image folders and detect existing Suite2p outputs for concatenation or single image processing.
        4. Run Suite2p on unprocessed folders (or all folders if overwrite_suite2p is enabled).
        5. Save the analysis configuration used for reproducibility.

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

        main_folder = config.general_settings.main_folder
        data_extension = config.general_settings.data_extension
        ops_path = config.general_settings.ops_path
        ops = np.load(ops_path, allow_pickle=True).item()
        ops['frame_rate'] = config.general_settings.frame_rate
        ops['input_format'] = data_extension
        ops['delete_bin'] = 1
        print("Attempting to run Suite2p")
        if not config.analysis_params.multivid_processing:
            export_image_files_to_suite2p_format(main_folder, config)
        # if convert_to_tiff is True:
            # convert_nd2_to_tiff.iterConvert(config)
            # ops['input_format'] = 'tif'
        # export_image_files_to_suite2p_format(main_folder, config)
        image_folder_dict = get_all_image_folders_in_path(main_folder, file_ending= data_extension)
        suite2p_samples = functions_data_transformation.get_file_name_list(config.general_settings.main_folder, file_ending="samples", supress_printing=True)
        unprocessed_samples = []

        if not config.analysis_params.overwrite_suite2p:
            if config.analysis_params.multivid_processing == True:

                for image in image_folder_dict['concat']:
                    if image not in suite2p_samples:
                        unprocessed_samples.append(image)
                ops['do_registration'] = 1
                process_files_with_suite2p(unprocessed_samples, ops)
            else:
                for image in image_folder_dict['single']:
                    if image not in suite2p_samples:
                        unprocessed_samples.append(image)
                process_files_with_suite2p(unprocessed_samples, ops)
        else:
            if config.analysis_params.multivid_processing == False:
                ops['do_registration'] = 0
                process_files_with_suite2p(image_folder_dict['single'], ops)
            else:
                ops['do_registration'] = 1
                process_files_with_suite2p(image_folder_dict['concat'], ops)

        import json
        with open(os.path.join(main_folder, 'analysis_config.json'), 'w') as f:
            json.dump(config_dict, f, indent = 4)
        print(f"Analysis parameters saved in {main_folder} as analysis_config.json")
        from datetime import datetime

        now = datetime.now()

        current_time = now.strftime("%H:%M:%S")
        print("Current Time =", current_time)

    except KeyboardInterrupt as e:
        print(e, '\n')
        print("Analysis was interrupted by user")
    finally:
        import json
        with open(os.path.join(main_folder, 'analysis_config.json'), 'w') as f:
            json.dump(config_dict, f, indent = 4)
        print(f"Analysis parameters saved in {main_folder} as analysis_config.json")
        from datetime import datetime

        now = datetime.now()

        current_time = now.strftime("%H:%M:%S")
        print("Current Time =", current_time)

if __name__ == "__main__":
    main()


"""
To Run:
activate suite2p
import run_suite2p 
if __name__ == "__main__":
    run_suite2p.main()

or simply in ipynb file: run_suite2p_main()

"""