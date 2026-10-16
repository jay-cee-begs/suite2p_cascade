import numpy as np
import pandas as pd
from BaselineRemoval import BaselineRemoval

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

def calculate_peaks(deltaF):
    from scipy.signal import find_peaks
    sigma, baseline_samples = estimate_single_trace_baseline_noise_mad(deltaF)
    peaks, properties = find_peaks(deltaF, height = np.median(baseline_samples) + 4.5*sigma, distance = 5, 
                          prominence= 2*sigma,
                          width = (2,50))
    peak_count = len(peaks)

    return peaks, peak_count, properties['width']



def calculate_normalized_deltaF(F, Fneu, baseline_correction = None, lambda_window = None, event_threshold = 2, by_type = "Cell"):
    """
    Convert raw fluorescence (F.npy) into a normalized change in fluorescence with 0 being baseline and 1 being the max fluorscence. 
    Normalization can be done for the min/max of an individual ROI (ROI / "Cell" based) or for a population max/min ("Population").
    This can be done with and without baseline correction
    using rolling median baseline correction.

    Args:
    -----------
        F_file : str
            Path to NumPy array containing raw flourescence (F.npy) trace from suite2p.
        config : SimpleNameSpace dictionary
            loaded automatically from config_loader.load_json_config_file(file = None)
        baseline_correction : str, optional
            String input accepting either "airPLS" or "rolling_median" as options for correction
        lambda_window : int, optional
            Number of frames to subsample for rolling median calculation
        event_threshold : float, optional
            Number of standard deviations above MAD to se peak filtering; default is 2
        by_type : str
            How to perform normalization within ROIs so all ROIs are between 0-1 ("Cell") or "Population" for 0-1 based on population values
            Normalizing by population is not recommended since it will likely include false ROIs unless these are filtered / removed by the user

    Returns:
    -----------
        deltaF : 1D numpy array
            dF/F0 normalized fluorescence
            MAD baseline estimated
            rolling median automated baseline correction
            deltaF is saved into the suite2p output folder generated from suite2p ROI detection.
    """    
    deltaF= []

    # if by_type != config.analysis_params.normalization_method:
    #     by_type = config.analysis_params.normalization_method


    

    for f, fneu in zip(F, Fneu):
        corrected_trace = f - (0.7*fneu) ## neuropil correction
        
        if baseline_correction is None:
            deltaF.append((corrected_trace-corrected_trace.min())/ (corrected_trace.max() - corrected_trace.min()))
        else:
            if baseline_correction in ['rolling_median', 'airPLS']:
                if baseline_correction is 'airPLS':
                    from BaselineRemoval import BaselineRemoval
                    base_corr = BaselineRemoval(corrected_trace)
                    if lambda_window is None:
                        deltaF = base_corr.ZhangFit(lambda_ = 100)
                    else:
                        deltaF = base_corr.ZhangFit(lambda_ = lambda_window)
                if baseline_correction is 'rolling_median':
                    from run_cascade import functions_data_transformation as fdt, functions_general as fun_g
                    if lambda_window is not None:
                        deltaF = fun_g.remove_bleaching(corrected_trace, baseline_correction="rolling_med", window = lambda_window)
                    else:
                        deltaF = fun_g.remove_bleaching(corrected_trace, baseline_correction='rolling_min',window = 250)
    deltaF = np.array(deltaF)
    deltaF = np.squeeze(deltaF)

    return deltaF


def glob_roi_corr(trace, global_signal, max_lag = 10):

    trace = (trace - np.mean(trace) ) / (np.std(trace) + 1e-12)
    global_z = (global_signal - np.mean(global_signal) ) / (np.std(global_signal) + 1e-12)

    n = len(trace)
    zero_lag_corr = np.corrcoef(trace, global_z)[0,1]

    if max_lag == 0:
        return zero_lag_corr, zero_lag_corr, 0
    
    lags = range(-max_lag, max_lag + 1)

    corrs = []

    for lag in lags:
        if lag > 0:
            a,b = trace[lag:], global_z[:n-lag]
        elif lag < 0:
            a,b = trace[:n + lag], global_z[-lag:]
        else:
            a,b = trace, global_z

        corrs.append(np.corrcoef(a,b)[0,1])

    corrs = np.asarray(corrs, dtype=float)

    valid = np.isfinite(corrs)

    if not np.any(valid):
        # No valid correlation at any lag.
        return zero_lag_corr, np.nan, 0

    # Find the highest valid correlation.
    valid_indices = np.flatnonzero(valid)
    best_idx = valid_indices[np.argmax(corrs[valid])]

    return zero_lag_corr, corrs[best_idx], list(lags)[best_idx]

def process_suite2p_dict(d):
    import numpy as np
    import pandas as pd
    from scipy.signal import find_peaks

    F = d['F']
    Fneu = d['Fneu']
    stat = d['stat']
    deltaF = d['deltaF']
    iscell = d['iscell']
    cascade = d['cascade_predictions']

    n_rois = len(iscell[:,0])
    background = F - Fneu
    bad_ROI_mask = background.min(axis = 1) < 0 
    idx_fneu_over_f = list(np.where(bad_ROI_mask == 1)[0])


    idx_active, idx_neuron, idx_glia = [],[],[]
    peak_info = {}
    norm_F = calculate_normalized_deltaF(F, Fneu, by_type="Cell", event_threshold=2)
    for n in range(n_rois):
        trace = norm_F[n]
        cascade_analysis = np.nansum(cascade[n])
        cascade_max = cascade[n].max()
        sigma, baseline = estimate_single_trace_baseline_noise_mad(trace, 2)
        peaks, properties = find_peaks(trace, height = np.median(baseline) + 4*sigma, distance = 3,
                                       width = (2,50))
        if len(peaks) > 0 and cascade_analysis > 0.1 and cascade_max > 0.05:
            
            idx_active.append(n)
        peak_info[n] = {'peaks': peaks, 'propoerties': properties}

        median_width = np.median(properties['widths'])
        if median_width < 9: 
            idx_neuron.append(n)
        else:
            idx_glia.append(n)
    template_score = []
        # Include ALL Suite2p-classified cells in the cell-type classifier.
    iscell_mask = np.asarray(iscell)[:, 0] == 1
    iscell_ids = np.flatnonzero(iscell_mask)

    classified_traces = deltaF[iscell_ids]
    global_signal = np.mean(classified_traces,axis = 0)

    idx_neuro_corr = []
    idx_glia_corr = []
    neuro_corr = []
    glia_corr = []
    active_corr = {}

    if len(iscell_ids) > 1:
        for i, roi_id in enumerate(iscell_ids):

            cell_trace = deltaF[roi_id]

            # Mean activity of all other Suite2p-classified cells.
            other_cells = np.delete(classified_traces, i, axis=0)

            # Ignore NaNs when calculating the population signal.
            with np.errstate(invalid="ignore"):
                global_signal_excluding_cell = np.nanmean(other_cells, axis=0)

            try:
                zero_lag_corr, best_corr, best_lag = glob_roi_corr(
                    cell_trace,
                    global_signal=global_signal_excluding_cell,
                    max_lag=10,
                )
            except (ValueError, FloatingPointError):
                # The ROI has no usable correlation.
                zero_lag_corr = np.nan
                best_corr = np.nan
                best_lag = 0

            active_corr[int(roi_id)] = {
                "zero_lag_corr": zero_lag_corr,
                "best_corr": best_corr,
                "best_lag": best_lag,
            }

            if np.isfinite(zero_lag_corr) and zero_lag_corr >= 0.4:
                idx_neuro_corr.append(int(roi_id))
                neuro_corr.append(zero_lag_corr)
            else:
                # Fallback for cells that cannot be classified by correlation.
                idx_glia_corr.append(int(roi_id))
                glia_corr.append(zero_lag_corr)

    elif len(iscell_ids) == 1:
        # A single cell cannot be correlated with the other cells.
        # Explicit fallback; consider reviewing this ROI separately.
        idx_glia_corr.append(int(iscell_ids[0]))
        glia_corr.append(np.nan)

    # Confirm that every Suite2p-classified cell has exactly one label.
    assert set(idx_neuro_corr).isdisjoint(set(idx_glia_corr))
    assert set(idx_neuro_corr) | set(idx_glia_corr) == set(iscell_ids)

    results = {
    "Group": d["Group"],
    "File": d["data_folder"],
    "nROIs": n_rois,
    "n_iscell": len(iscell_ids),
    "n_active": len(idx_active),
    "idx_active": idx_active,

    # Existing width-based classification; keep separate.
    "n_neuro": len(idx_neuron),
    "idx_neuro": idx_neuron,
    "n_glia": len(idx_glia),
    "idx_glia": idx_glia,

    # Authoritative neuron/glia classification for plotting.
    "n_neuro_corr": len(idx_neuro_corr),
    "idx_neuro_corr": idx_neuro_corr,
    "neuro_corr": neuro_corr,
    "n_glia_corr": len(idx_glia_corr),
    "idx_glia_corr": idx_glia_corr,
    "glia_corr": glia_corr,
    }
    return results, active_corr, global_signal

