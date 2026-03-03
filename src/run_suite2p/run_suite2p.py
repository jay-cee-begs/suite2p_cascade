import os
import numpy as np
import tqdm
from pathlib import Path
from PIL import Image
import shutil
import sys
# sys.path.insert(0, 'D:/users/JC/suite2p-0.14.0')
from suite2p import run_s2p
from batch_process.config_loader import load_json_config_file, load_json_dict
from run_cascade import functions_data_transformation
# import convert_nd2_to_tiff

_DEFAULT_CONFIG = load_json_config_file()
config = _DEFAULT_CONFIG

def export_image_files_to_suite2p_format(parent_directory, config):
    """Export each image file (with variable file extension) into its own folder for suite2p processing, for all directories within a given parent directory."""
    
    image_file_ending = '.' + config.general_settings.data_extension

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
        for file in os.listdir(dir_path):
            if file.endswith(image_file_ending):
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
            else:
                print(f"Skipping non-{image_file_ending} file: {file}")
#Loading in suite2p settings to begin processing



def get_all_image_folders_in_path(path):
    """
    Find all folders within a given path that contain exactly one .nd2 file in their deepest subfolder.
    
    Nested Function:
    - check_for_single_image_file_in_folder: Checks if a given directory contains exactly one .nd2 file.
    """

    def check_for_single_image_file_in_folder(current_path, file_ending = config.general_settings.data_extension):
        """
        Check if the specified path contains exactly one .nd2 file.
        """
        tiff_files = [file for file in os.listdir(current_path) if file.endswith(file_ending)]
        return len(tiff_files) == 1

    found_image_folders = []
    for current_path, directories, files in os.walk(path):
        # Check if current directory is a "deepest" directory (no subdirectories)
        if check_for_single_image_file_in_folder(current_path):
            #current_path = current_path.split("\\")[-2]
            found_image_folders.append(current_path)

    return found_image_folders

# Example Usage:
# image_folders = get_all_image_folders_in_path('/path/to/search')
# print(image_folders)

def process_files_with_suite2p(image_list, ops):
        """
        Processes a list of image paths using the run_s2p function, applying specified config.json.

        Args:
        image_list (list of str): List of file paths to the images to be processed.
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
    ops['do_registration'] = 0
    ops['delete_bin'] = 1
    copy_files = False
    convert_to_tiff = True
    if copy_files and convert_to_tiff is False:
        export_image_files_to_suite2p_format(main_folder, config)
    # if convert_to_tiff is True:
        # convert_nd2_to_tiff.iterConvert(config)
        # ops['input_format'] = 'tif'
    # export_image_files_to_suite2p_format(main_folder, config)
    image_folders = get_all_image_folders_in_path(main_folder)
    suite2p_samples = functions_data_transformation.get_file_name_list(config.general_settings.main_folder, file_ending="samples", supress_printing=True)
    unprocessed_samples = []
    for image in image_folders:
        if image not in suite2p_samples:
            unprocessed_samples.append(image)
    
    process_files_with_suite2p(unprocessed_samples, ops)
    import json
    with open(os.path.join(main_folder, 'analysis_config.json'), 'w') as f:
        json.dump(config_dict, f, indent = 4)
    print(f"Analysis parameters saved in {main_folder} as analysis_config.json")


if __name__ == "__main__":
    main()


"""To Run:
activate suite2p
import run_suite2p 
if __name__ == "__main__":
    run_suite2p.main()

or simply in ipynb file: run_suite2p_main()
    """