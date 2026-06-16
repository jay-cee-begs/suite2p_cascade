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
                          prominence=np.median(baseline_samples) + 2*sigma,
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


    
    if by_type == "Cell":
        for f, fneu in zip(F, Fneu):
            corrected_trace = f - (0.7*fneu) ## neuropil correction

            deltaF.append((corrected_trace-corrected_trace.min())/ (corrected_trace.max() - corrected_trace.min()))
    else:
        corrected_traces = F - 0.7*Fneu
        pop_max = corrected_traces.max()
        pop_min = corrected_traces.min()

        for f, fneu in zip(F, Fneu):
            corrected_trace = f - (0.7*fneu) ## neuropil correction

            deltaF.append((corrected_trace-pop_min)/ (pop_max - pop_min))

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

    corrs = np.array(corrs)
    best_idx = np.nanargmax(corrs)

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
        trace = deltaF[n]
        cascade_analysis = np.nansum(cascade[n])
        sigma, baseline = estimate_single_trace_baseline_noise_mad(trace, )
        peaks, properties = find_peaks(trace, height = np.median(baseline) + 4*sigma, distance = 3,
                                       width = (2,50))
        if len(peaks) == 0 and cascade_analysis <= 0.1:
            continue
        idx_active.append(n)
        peak_info[n] = {'peaks': peaks, 'propoerties': properties}

        median_width = np.median(properties['widths'])
        if median_width < 9: 
            idx_neuron.append(n)
        else:
            idx_glia.append(n)
    template_score = []
    active_traces = deltaF[idx_active]
    global_signal = np.mean(active_traces,axis = 0)
    corr_glob = BaselineRemoval(global_signal)
    corr_glob = corr_glob.ZhangFit(lambda_ = 100)
    global_signal = corr_glob
    active_corr = {}
    for id in idx_active:
        zero_lag_corr, best_corr, best_lag = glob_roi_corr(deltaF[id], global_signal=global_signal, max_lag= 10)
        template_score.append(zero_lag_corr)
        active_corr[id] = {
            'zero_lag_corr': zero_lag_corr,
            'best_corr': best_corr,
            'best_lag': best_lag
        }

    glob_neuron_idx = []
    glob_neuron_corr = []
    glob_glia_idx = []
    glob_glia_corr = []

    for roi_id, scores in active_corr.items():
        if scores['zero_lag_corr'] < 0.4:
            glob_glia_idx.append(roi_id)
            glob_glia_corr.append(scores['zero_lag_corr'])
        else:
            glob_neuron_idx.append(roi_id)
            glob_neuron_corr.append(scores['zero_lag_corr'])
    results = {
        "Group": d['Group'],
        'File': d['data_folder'],
        'nROIs': n_rois,
        "n_faulty": len(idx_fneu_over_f),
        "n_faulty_idx": idx_fneu_over_f,
        "n_active": len(idx_active),
        "idx_active": idx_active,
        'n_neuro': len(idx_neuron),
        'idx_neuro': idx_neuron,
        'idx_neuro_corr': glob_neuron_idx,
        'neuro_corr': glob_neuron_corr,
        'n_glia': len(idx_glia),
        'idx_glia': idx_glia,
        'idx_glia_corr': glob_glia_idx,
        'glia_corr': glob_glia_corr,

    
    }
    return results, active_corr, global_signal

