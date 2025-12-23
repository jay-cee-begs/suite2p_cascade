import os
import numpy as np
import tqdm
from pathlib import Path
from PIL import Image
from nd2reader import ND2Reader #only if converting to tiff
import shutil
import sys
# sys.path.insert(0, 'D:/users/JC/suite2p-0.14.0')
from suite2p import run_s2p

from batch_process. config_loader import load_json_config_file, load_json_dict
from run_cascade import functions_data_transformation

_DEFAULT_CONFIG = load_json_config_file()
config = _DEFAULT_CONFIG


def getFilesWithExt(top_dir, files_ext):
    matches = []
    for root, dirnames, filenames in os.walk(str(top_dir)):
        for _dir in dirnames:
            matches += getFilesWithExt(_dir, files_ext)
        for filename in filenames:
            full_path = os.path.join(root, filename)
            if full_path.endswith(files_ext):
                matches.append(Path(os.path.join(root, filename)))
    return matches

def convertND2toTiff(fp_pathlib):
    
    print("Attempting to convert:", str(fp_pathlib))
    save_fp = tiffPathFromND2(fp_pathlib)
    save_dir = save_fp.parent
    print(f"Saving to: {save_fp} in dir: {save_dir}")
    save_dir.mkdir(parents=False, exist_ok = True)
    with ND2Reader(str(fp_pathlib)) as images:
        images_li=[]
        images.iter_axes='t'
        for idx in range(len(images)):
            images_li.append(Image.fromarray(np.array(images[idx])))
        images_li[0].save(save_fp, save_all=True, append_images=images_li[1:])
        print("Done converting")
        
def tiffPathFromND2(_file):
    return Path(f"{_file.parent}/{_file.stem}/{_file.stem}.tif")

def iterConvert(config):
    BASE_DIR = config.general_settings.main_folder

    tiff_files = getFilesWithExt(BASE_DIR, ".tif")
    files_to_convert = [_file for _file in getFilesWithExt(BASE_DIR, ".nd2")
                       if tiffPathFromND2(_file) not in tiff_files]
    print("Files to convert:", files_to_convert)
    print("Total number of files to convert:", len(files_to_convert))
    for fp in tqdm.tqdm(files_to_convert):
        print(f"Processing {fp.name}.tif")
        convertND2toTiff(fp)

