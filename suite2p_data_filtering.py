import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os


parent_dir = r'C:\LB_hiPSC\cropped-iN_iA\take2\241022_hIPSC_DIV42ish_1.5H_4x_ACSF_plate02_well001b001'

SUITE2P_STRUCTURE = {
    "F": ["suite2p", "plane0", "F.npy"],
    "Fneu": ["suite2p", "plane0", "Fneu.npy"],
    "spks": ["suite2p", "plane0", "spks.npy"],
    "stat": ["suite2p", "plane0", "stat.npy"],
    "iscell": ["suite2p", "plane0", "iscell.npy"],
    "deltaF": ["suite2p", "plane0", "deltaF.npy"],
    "ops":["suite2p", "plane0", "ops.npy"],
    "cascade_predictions": ["suite2p", "plane0", "predictions_deltaF.npy"]
}

def filter_cascade_predictions(directory):
    iscell = np.load(os.path.join(directory, *SUITE2P_STRUCTURE['iscell']), allow_pickle=True)
    deltaF = np.load(os.path.join(directory, *SUITE2P_STRUCTURE['cascade_predictions']), allow_pickle=True)


    iscell_boolean = iscell[:,0].astype(bool)
    filtered_neurons = [cell for cell, is_cell in zip(deltaF, iscell_boolean) if is_cell]
    output_path = os.path.join(os.path.abspath(directory), 'filtered_cascade_predictions.npy')
    np.save(output_path, filtered_neurons)
    # return np.save(output_path, filtered_neurons)

def get_all_image_folders_in_path(path):
    """
    Find all folders within a given path that contain exactly one .nd2 file in their deepest subfolder.
    
    Nested Function:
    - check_for_single_image_file_in_folder: Checks if a given directory contains exactly one .nd2 file.
    """

    def check_for_single_image_file_in_folder(current_path, file_ending = 'nd2'):
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

if __name__=="__main__":
    current_paths = get_all_image_folders_in_path(parent_dir)
    for path in current_paths:
        filter_cascade_predictions(path)



