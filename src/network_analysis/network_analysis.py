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


    """
    Detect and characterize synchronous network events from normalized (0-1) calcium
    fluorescence traces, using two complementary criteria:

        1) Population-level activity: the fraction of cells simultaneously active
           (smoothed) exceeds `activity_threshold`.
        2) Neuron recruitment: the raw number of co-active cells exceeds
           `recruitment_fraction` of the total classified-cell count.

    A frame is only called part of a synchronous network event if BOTH criteria
    are met (burst_mask & recruitment_mask). Discrete events are then labeled and
    summarized (duration, amplitude, neurons recruited) rather than left as a
    frame-wise boolean mask.

    Args:
    --------
        suite2p_dict : dict
            Must contain 'network_deltaF' (cells x frames, normalized 0-1) and
            'iscell' (suite2p classification array, iscell[:,0] == 1 for real cells).
            Optionally 'Group' for labeling saved plots.
        activity_threshold : float
            Threshold on smoothed population-activity fraction (0-1) to call a
            frame "elevated." Default 0.1.
        recruitment_fraction : float
            Fraction of total classified cells that must be simultaneously active
            to satisfy the recruitment criterion. Default 0.4 (40%).
        bin_window : int
            Width (in frames) of the moving-average smoothing window applied to
            the population activity trace.
        peak_distance : int
            Minimum spacing (in frames) between detected peaks, passed to
            scipy.signal.find_peaks.
        save_path : str or None
            If provided, saves both plots as .png and .svg to this directory.
        show_plots : bool
            Whether to call plt.show() for the two diagnostic plots.
        show_recruitment_diagnostic : bool
            If True, plots a histogram of the per-frame fraction of classified
            cells co-active, with a vertical line at the current
            `recruitment_fraction` cutoff. Useful for sanity-checking whether
            0.4 (or whatever value you're using) is a defensible threshold for
            this recording, rather than an arbitrary guess.

    Returns:
    --------
        results : dict
            af_smooth           : smoothed population-activity trace
            global_activity     : raw (unsmoothed) population-activity trace
            cell_activity       : boolean array (cells x frames) of per-cell activity
            n_active_cells      : per-frame count of co-active cells
            peaks               : frame indices of detected activity peaks
            burst_mask          : bool array, population-activity criterion only
            recruitment_mask    : bool array, neuron-recruitment criterion only
            event_mask          : bool array, BOTH criteria met (the actual network events)
            event_stats         : list of dicts, one per discrete event, with
                                   start/end frame, duration, peak amplitude,
                                   and max neurons recruited during the event
    """

    plt.rcParams['svg.fonttype'] = 'none'
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = 'Arial'

    def process_normalized_fluorescence(deltaF_traces, normalized_traces):
        """
        calcium_traces : (n_cells, n_frames) array, normalized 0-1 per ROI.
        A cell is "active" on a frame if it exceeds its own 95th-percentile value
        -- since traces are already min-max normalized per-ROI, this threshold is
        comparable across cells without needing z-scoring.
        """
        network_activity = normalized_traces > np.percentile(normalized_traces, 95, axis=1)[:, None]
        deltaF_activity = deltaF_traces.mean(axis=0)
        n_active_cells = network_activity.sum(axis=0)

        af_smooth = np.convolve(
            deltaF_activity,
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
        return af_smooth, deltaF_activity, network_activity, n_active_cells

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
