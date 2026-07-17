from run_cascade import functions_data_transformation as fdt,  functions_general as fun_g
from batch_gui.config_loader import load_json_config_file, load_json_dict
from network_analysis import rastermapping
import matplotlib.pyplot as plt
from scipy.stats import zscore, norm
import numpy as np 
import pandas as pd
from scipy.signal import find_peaks
from BaselineRemoval import BaselineRemoval
import os



def load_and_plot_network(suite2p_dict): 
    
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import zscore, norm
from scipy.signal import find_peaks
import matplotlib.pyplot as plt
import numpy as np
import os
from scipy.signal import find_peaks
from scipy.ndimage import label


import matplotlib.pyplot as plt
import numpy as np
import os
from scipy.signal import find_peaks
from scipy.ndimage import label


    plt.rcParams['svg.fonttype'] = 'none'
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = 'Arial'
    def calculate_zscore(network_deltaF):
        Z = zscore(network_deltaF, axis = 1, ddof = 1)
        #Find 95% of activity for all neurons and filter
        # activity_fraction = (Z > 2).mean(axis = 0)
        activity_fraction = (Z > np.percentile(Z, 85, axis=1)[:, None]).mean(axis=0)
        bin_window = 5
        #smooth activity_fraction by 500 ms
        af_smooth = np.convolve(
            activity_fraction,
            np.ones(bin_window) / bin_window,
            mode = 'same'
        )
        return Z, af_smooth, bin_window, activity_fraction
    Z, af_smooth, bin_window, activity_fraction = calculate_zscore(suite2p_dict['network_deltaF'])
    peaks, _  = find_peaks(activity_fraction, height = 0.1, distance = 5)
    burst_mask = np.zeros(Z.shape[1], dtype = bool)
    burst_width = 10
    for p in peaks:
        burst_mask[max(0, p-burst_width):min(Z.shape[1], p + burst_width)] = True
        global_signal = Z.mean(axis=0)
        global_smooth = np.convolve(
            global_signal,
            np.ones(bin_window) / bin_window,
            mode='same'
        )
    
    norm_global = global_smooth / global_smooth.max()
    plt.rcParams['svg.fonttype'] = 'none'
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = 'Arial'
    plt.figure(figsize=(10,4))
    plt.plot(activity_fraction, label='Activity fraction', color = 'black', alpha = 0.4,lw=2)
    plt.plot(peaks, activity_fraction[peaks], 'x', label='Burst peaks')
    # plt.plot(norm_global, 
    #         alpha=0.4, label='Global mean (norm)')
    plt.axhline(0.1, color='k', ls='--', alpha=0.5)
    plt.fill_between(
        np.arange(len(burst_mask)),
        norm_global.min(),
        norm_global.max(),
        where=burst_mask,
        color='red',
        alpha=0.2,
        label='Network bursts'
    )
    plt.ylim(-0.2, 1)
    plt.xlabel("Frame")
    plt.ylabel("Fraction active")
    plt.title("Network bursts defined by population participation")
    plt.tight_layout()
    # plt.legend()
    group = suite2p_dict["Group"]
    import os
    save_path = r'D:\zeiss\Documents\JC_presents'
    plt.savefig(os.path.join(save_path, f"{group}_simple_network_bursts.png"))
    plt.savefig(os.path.join(save_path, f"{group}_simple_network_bursts.svg"))
    plt.show()
    global_min = np.min(global_signal)
    offset = abs(0 - global_min)
    plt.plot(global_signal + offset)
    plt.plot(peaks,global_signal[peaks] + offset, 'x')
    # plt.plot(peaks, global_signal[peaks], 'x', label='Burst peaks')
    # plt.plot(norm_global, 
    #         alpha=0.4, label='Global mean (norm)')
    plt.fill_between(
        np.arange(len(burst_mask)),
        global_signal.min() + offset,
        global_signal.max() + offset,
        where=burst_mask,
        color='red',
        alpha=0.2,
        label='Network bursts'
    )
    plt.xlabel("Time [s]")
    plt.ylabel("Global Activity")
    plt.ylim(0, 6)
    plt.title("Network bursts defined by population participation")
    plt.tight_layout()
    save_path = r'D:\zeiss\Documents\JC_presents'
    plt.savefig(os.path.join(save_path, f"{group}_global_activity.png"))
    plt.savefig(os.path.join(save_path, f"{group}_global_activity.svg"))
    ###NOTE Z is deltaF since no more z-score
    return Z, af_smooth, peaks, bin_window, global_signal, burst_width, burst_mask

def main(config_file = None):
    try:
        global config  # <- important
        global config_dict
        if config_file is not None:
            config = load_json_config_file(config_file)
            config_dict = load_json_dict(config_file)

        else:
            config = load_json_config_file()
            config_dict = load_json_dict()
    except KeyboardInterrupt as e:
        print("Outputs interrupted by user")
    finally:
        import json
        with open(os.path.join(config.general_settings.main_folder, 'analysis_config.json'), 'w') as f:
            json.dump(config_dict, f, indent = 4)
        print(f"Analysis parameters saved in {config.general_settings.main_folder} as analysis_config.json")
        from datetime import datetime

        now = datetime.now()

        current_time = now.strftime("%H:%M:%S")
        print("Current Time =", current_time)
if __name__ == '__main__':
    main()
