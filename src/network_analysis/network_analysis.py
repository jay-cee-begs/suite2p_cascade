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
from batch_gui import config_loader

_DEFAULT_CONFIG = load_json_config_file()
config = _DEFAULT_CONFIG

def estimate_single_trace_baseline_noise_mad(F_trace, event_threshold = 2):
    """
    Estimate noise sigma from baseline-only windows using MAD.
    
    Args:
    -----------
        F : 1D numpy array
            Baseline-corrected ΔF/F trace.
        frame_rate : float
            Sampling rate (Hz).
        event_threshold : float
            Preserved from calculate_deltaF function above.
            Threshold (in MAD units) to mask obvious events by multiplying by estimated noise standard deviation. 
            Default: 2 (SD above median)
            Smaller values will limit the number of baseline points used for correction.
        min_baseline_sec : float
            Minimum duration (seconds) of a baseline window.
            Default: 10 s

    Returns:
    --------
        sigma : float
            Estimated noise standard deviation.
        baseline_mask : boolean array
            Mask of samples classified as baseline.
    """

    trace_median = np.median(F_trace)
    mad = np.median(np.abs(F_trace - trace_median))
    sigma = 1.4826 * mad
    event_mask = np.abs(F_trace - trace_median) > event_threshold * sigma

    trace_baseline = ~event_mask

    baseline_samples = F_trace[trace_baseline]
    
    baseline_median = np.median(baseline_samples)
    baseline_mad = np.median(np.abs(baseline_samples - baseline_median))
    sigma = 1.4826 * baseline_mad
    
    return sigma, baseline_samples

def load_and_plot_network(suite2p_dict, config, recruitment_fraction=0.1,
                            bin_window=5, peak_distance=10, save_path=None, show_plots=True,
                            show_recruitment_diagnostic=True, mask_traces = True):
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
            df_smooth           : smoothed population-activity trace
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
        baselines, sds = [],[]
        masked_cell_activity = []
        cell_activity = []
        for trace in deltaF_traces:
            sigma, baseline_samples = estimate_single_trace_baseline_noise_mad(trace, event_threshold=2)
            baselines.append(np.median(baseline_samples))
            sds.append(sigma)
            cell_activity.append(trace > np.median(baseline_samples) + 2*sigma)
        
            masked_cell_activity = np.array(cell_activity)
            network_activity = normalized_traces.mean(axis = 0)
            deltaF_activity = deltaF_traces.mean(axis=0)
            n_active_cells = masked_cell_activity.sum(axis=0)

        df_smooth = np.convolve(
            deltaF_activity,
            np.ones(bin_window) / bin_window,
            mode='same'
        )
        results = {
            'df_smooth': df_smooth,
            'raw_normalized_activity': network_activity,
            'raw_deltaF_activity': deltaF_activity,
            'masked_cell_activity': masked_cell_activity,
            'n_active_cells': n_active_cells
        }
        return results
    #df_smooth is concolved average fluorescence trace across a recording 
    #network_activity is the raw average deltaF /F0 trace
    #masked_cell_activity is when each ROI has fluorescence > baseline_median + 3*SD
    #
    # Restrict to suite2p-classified cells so numerator/denominator of the
    # recruitment criterion stay consistent with each other.
    suite2p_df = fdt.df_from_suite2p_dict(suite2p_dict, config)
    
    if mask_traces:
        activity_mask = list(suite2p_df['ActiveROI'] == True)
    else:
        activity_mask = suite2p_dict['iscell'][:,0] == 1
    masked_normalized_traces = suite2p_dict['network_deltaF'][activity_mask]
    masked_deltaF_traces = suite2p_dict['deltaF'][activity_mask]
    total_cells = masked_deltaF_traces.shape[0]

    processed_results = process_normalized_fluorescence(masked_deltaF_traces, masked_normalized_traces)

    # ---------------------------------------------------------
    # Cell-to-global synchrony
    # ---------------------------------------------------------
    # Calculate a leave-one-cell-out global signal for each cell.
    # This prevents a cell's own activity from artificially
    # increasing its correlation with the global signal.

    n_cells, n_frames = masked_normalized_traces.shape

    cell_global_corr = np.full(n_cells, np.nan)

    for i in range(n_cells):

        # Global activity of all OTHER cells
        other_cells = np.delete(masked_normalized_traces, i, axis=0)
        global_signal_excluding_cell = other_cells.mean(axis=0)

        # Pearson correlation between this cell and the
        # activity of the rest of the population
        cell_trace = masked_normalized_traces[i]

        cell_global_corr[i] = np.corrcoef(
            cell_trace,
            global_signal_excluding_cell
        )[0, 1]

    if show_recruitment_diagnostic:
        recruited_fraction_per_frame = processed_results['n_active_cells'] / total_cells
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
    af_sd, af_baseline = estimate_single_trace_baseline_noise_mad(processed_results['df_smooth'], event_threshold=2)
    activity_threshold = np.median(af_baseline) + 2*af_sd
    peaks, _ = find_peaks(processed_results['df_smooth'], height=activity_threshold, distance=peak_distance)

    # --- Two individual criteria ---
    burst_mask = processed_results['df_smooth'] > activity_threshold
    recruitment_threshold = total_cells * recruitment_fraction
    recruitment_mask = processed_results['n_active_cells'] > recruitment_threshold
    # --- Combined event mask: both criteria must hold ---
    event_mask =  recruitment_mask
    # ---------------------------------------------------------
    # Cell participation per network event
    # ---------------------------------------------------------
    # First identify the discrete network events
    labeled_events, n_events = label(event_mask)

    # Matrix:
    #   rows    = cells
    #   columns = individual network events
    #
    # Value = 1 if the cell participated in that event,
    #         0 if it did not.
    event_participation = np.zeros(
        (total_cells, n_events),
        dtype=bool
    )

    for event_id in range(1, n_events + 1):

        # Frames belonging to this particular event
        event_frames = labeled_events == event_id

        for i in range(total_cells):

            # Was this cell active at ANY point during the event?
            event_participation[i, event_id - 1] = (
                processed_results['masked_cell_activity'][i, event_frames].any()
            )

    # Fraction of network events each cell participated in
    if n_events > 0:
        event_participation_fraction = event_participation.mean(axis=1)
    else:
        event_participation_fraction = np.full(total_cells, np.nan)


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
            'peak_amplitude': float(processed_results['raw_deltaF_activity'][frames].max()),
            'max_neurons_recruited': int(processed_results['n_active_cells'][frames].max()),
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

    create_plots(processed_results['raw_deltaF_activity'], "Raw Amplitude", ylabel="Mean deltaF/F0", ylim=None, axhline_val=activity_threshold)
    create_plots(processed_results['df_smooth'], "Smoothed Amplitude", ylabel="Mean deltaF/F0", ylim=None, axhline_val=activity_threshold)
    create_plots(processed_results['n_active_cells'].astype(float), "Neurons Recruited", ylabel="Active neuron count", ylim=(0, total_cells), axhline_val=recruitment_threshold)

    image_file = os.path.basename(suite2p_dict['data_folder'])
    synchrony_results = {
        'Group': suite2p_dict['Group'],
        "Replicate_No.": suite2p_dict['sample'],
        'File_Name': image_file,
        'total_cells': total_cells,
        'recruitment_threshold': recruitment_threshold,
        'activity_threshold': activity_threshold,
        'df_smooth': processed_results['df_smooth'],
        'deltaF_activity':processed_results['raw_deltaF_activity'],
        'network_activity': processed_results['raw_normalized_activity'],
        'n_active_cells': processed_results['n_active_cells'],
        'peaks': peaks,
        'burst_mask': burst_mask,
        'recruitment_mask': recruitment_mask,
        'event_mask': event_mask,
        'event_stats': event_stats,
        'cell_global_corr': cell_global_corr,
        'event_participation': event_participation,
        'event_participation_fraction': event_participation_fraction

    }
    return synchrony_results

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


