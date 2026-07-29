from run_cascade import functions_data_transformation as fdt,  functions_general as fun_g
from batch_gui.config_loader import load_json_config_file, load_json_dict
from network_analysis import rastermapping
import matplotlib.pyplot as plt
import numpy as np 
import pandas as pd
from scipy.signal import find_peaks
from BaselineRemoval import BaselineRemoval
import matplotlib.pyplot as plt
import os
from scipy.signal import find_peaks
from scipy.ndimage import label





def load_and_plot_network(suite2p_dict, activity_threshold=0.05, recruitment_fraction=0.1,
                            bin_window=5, peak_distance=10, save_path=None, show_plots=True,
                            show_recruitment_diagnostic=True):
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
        return af_smooth, deltaF_activity, network_activity, n_active_cells

    # Restrict to suite2p-classified cells so numerator/denominator of the
    # recruitment criterion stay consistent with each other.
    iscell_mask = suite2p_dict['iscell'][:, 0] == 1
    masked_normalized_traces = suite2p_dict['network_deltaF'][iscell_mask]
    masked_deltaF_traces = suite2p_dict['deltaF'][iscell_mask]
    total_cells = iscell_mask.sum()

    af_smooth, deltaF_activity, network_activity, n_active_cells = process_normalized_fluorescence(masked_deltaF_traces, masked_normalized_traces)

    if show_recruitment_diagnostic:
        recruited_fraction_per_frame = n_active_cells / total_cells
        plt.figure(figsize=(6, 4))
        plt.hist(recruited_fraction_per_frame, bins=50, color='steelblue', alpha=0.8)
        plt.axvline(recruitment_fraction, color='red', ls='--',
                    label=f'current cutoff = {recruitment_fraction}')
        plt.xlabel("Fraction of classified cells co-active (per frame)")
        plt.ylabel("Number of frames")
        plt.title("Distribution of per-frame neuron recruitment")
        plt.legend()
        plt.tight_layout()
        if show_plots:
            plt.show()
        else:
            plt.close()

    peaks, _ = find_peaks(af_smooth, height=activity_threshold, distance=peak_distance)

    # --- Two individual criteria ---
    burst_mask = af_smooth > activity_threshold
    recruitment_threshold = total_cells * recruitment_fraction
    recruitment_mask = n_active_cells > recruitment_threshold

    # --- Combined event mask: both criteria must hold ---
    event_mask = burst_mask & recruitment_mask

    # --- Label discrete events and summarize each one ---
    labeled_events, n_events = label(event_mask)
    event_stats = []
    for event_id in range(1, n_events + 1):
        frames = np.where(labeled_events == event_id)[0]
        event_stats.append({
            'event_id': event_id,
            'start_frame': int(frames[0]),
            'end_frame': int(frames[-1]),
            'duration_frames': int(len(frames)),
            'peak_amplitude': float(deltaF_activity[frames].max()),
            'max_neurons_recruited': int(n_active_cells[frames].max()),
        })

    def create_plots(input_trace, plot_title, ylabel="Fraction active", ylim=None, axhline_val=None):
        plt.figure(figsize=(10, 4))
        plt.plot(input_trace, label='Activity trace', color='black', alpha=0.4, lw=2)
        plt.plot(peaks, input_trace[peaks], 'x', label='Peaks')
        if axhline_val is not None:
            plt.axhline(axhline_val, color='k', ls='--', alpha=0.5)
        
        plt.fill_between(
            np.arange(len(event_mask)),
            input_trace.min(),
            input_trace.max(),
            where=event_mask,
            color='red',
            alpha=0.2,
            label='Network events'
        )
        if ylim is not None:
            plt.ylim(ylim)
        plt.xlabel("Frame")
        plt.ylabel(ylabel)
        plt.title(plot_title)
        plt.legend()
        plt.tight_layout()

        if save_path is not None:
            group = suite2p_dict["Group"]
            fname_base = f"{group}_{plot_title.replace(' ', '_').lower()}"
            plt.savefig(os.path.join(save_path, f"{fname_base}.png"))
            plt.savefig(os.path.join(save_path, f"{fname_base}.svg"))

        if show_plots:
            plt.show()
        else:
            plt.close()

    create_plots(deltaF_activity, "Raw Amplitude", ylabel="Mean deltaF/F0", ylim=None, axhline_val=activity_threshold)
    create_plots(af_smooth, "Smoothed Amplitude", ylabel="Mean deltaF/F0", ylim=None, axhline_val=activity_threshold)
    create_plots(n_active_cells.astype(float), "Neurons Recruited", ylabel="Active neuron count", ylim=(0, total_cells), axhline_val=recruitment_threshold)

    image_file = os.path.basename(suite2p_dict['data_folder'])
    results = {
        'Group': suite2p_dict['Group'],
        "Replicate_No.": suite2p_dict['sample'],
        'File_Name': image_file,
        'af_smooth': af_smooth,
        'deltaF_activity':deltaF_activity,
        'network_activity': network_activity,
        'n_active_cells': n_active_cells,
        'peaks': peaks,
        'burst_mask': burst_mask,
        'recruitment_mask': recruitment_mask,
        'event_mask': event_mask,
        'event_stats': event_stats,
    }
    return results

def unpack_sync_event_stats(suite2p_dict, results):
    unpacked_events = []
    for network_event in results['event_stats']:
            event_with_id = {
                "Group": suite2p_dict['Group'],
                "Replicate_No.": suite2p_dict['sample'],
                "File_Name": os.path.basename(suite2p_dict['data_folder']),
                **network_event,
            }
            unpacked_events.append(event_with_id)
    if not unpacked_events:
        unpacked_events.append({
            "Group": suite2p_dict['Group'],
            "Replicate_No.": suite2p_dict['sample'],
            "File_Name": os.path.basename(suite2p_dict['data_folder']),
            "event_id": None,
            "start_frame": None,
            "end_frame": None,
            "duration_frames": np.nan,
            "peak_amplitude": np.nan,
            "max_neurons_recruited": np.nan,
        
        })
    return pd.DataFrame(unpacked_events)

# def process_sync_events(list_of_unpacked_events):
#     pd_list = []
#     for events in list_of_unpacked_events:
#         pd_list.append(events.groupby(["Group", "File_Name"]).agg({
#         'duration_frames': ['mean','std'],
#         'peak_amplitude': ['mean','std'],
#         'max_neurons_recruited': ['mean','std']
#         }))
#     final_df = pd.concat(pd_list)


# def main(config_file = None):
#     try:
#         global config  # <- important
#         global config_dict
#         if config_file is not None:
#             config = load_json_config_file(config_file)
#             config_dict = load_json_dict(config_file)

#         else:
#             config = load_json_config_file()
#             config_dict = load_json_dict()
#         suite2p_folders = fdt.get_file_name_list(config.general_settings.main_folder, 'samples', supress_printing=True)
#         all_results = []
#         all_events = []
#         for folder in suite2p_folders:
#             suite2p_dict = fdt.load_suite2p_paths(folder, config, use_iscell = config.analysis_params.use_suite2p_ROI_classifier)
#             results = load_and_plot_network(suite2p_dict, show_plots = False)
#             for network_event in results['event_stats']:
#                 event_with_id = {
#                     "Group": suite2p_dict['Group'],
#                     "Replicate_No.": suite2p_dict['sample'],
#                     "File_Name": os.path.basename(suite2p_dict['data_folder']),
#                     **network_event,
#                 }
#                 all_events.append(event_with_id)
#             all_results.append(results)
#         results_df = pd.DataFrame(all_results)
#         event_df = pd.DataFrame(all_events)
#     except KeyboardInterrupt as e:
#         print("Outputs interrupted by user")
#     finally:
#         import json
#         with open(os.path.join(config.general_settings.main_folder, 'analysis_config.json'), 'w') as f:
#             json.dump(config_dict, f, indent = 4)
#         print(f"Analysis parameters saved in {config.general_settings.main_folder} as analysis_config.json")
#         from datetime import datetime

#         now = datetime.now()

#         current_time = now.strftime("%H:%M:%S")
#         print("Current Time =", current_time)
#     return results_df, event_df
# if __name__ == '__main__':
#     main()
