
import os, warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from batch_process.config_loader import load_json_config_file, load_json_dict
from BaselineRemoval import BaselineRemoval
_DEFAULT_CONFIG = load_json_config_file()
config = _DEFAULT_CONFIG

def return_baseline_F(F, Fneu):
    """Returns the calculated baseline fluorescence for each cell and appends to the final dictionary"""
    savepath = rf"{F}".replace("\\F.npy","") ## make savepath original folder, indicates where deltaF.npy is saved


    baseline_F = []
    for f, fneu in zip(F, Fneu):
        corrected_trace = f - (0.7*fneu) ## neuropil correction
        trace_median = np.median(corrected_trace)
        trace_mad = np.median(np.abs(corrected_trace - trace_median))
        norm_sigma = 1.4826*trace_mad
        baseline_mask = np.abs(corrected_trace - trace_median) < 2 * norm_sigma

        F0 = np.median(corrected_trace[baseline_mask])
        baseline_F.append(F0)
    return baseline_F

def filter_cascade_predictions(predictions_file):
    """Filter cells in cascade to remove cells with total activity less than threshold
    by setting immediately to 0 predicted spikes"""
    cascade_prediction = np.nan_to_num(predictions_file)
    mask = np.sum(cascade_prediction, axis=1) <  float(config.cascade_settings.predicted_spike_threshold)
    cascade_prediction[mask] = 0
    return cascade_prediction


def basic_stats_per_cell(predictions_file):
    '''returns cell_means, cell_means, cell_cvs for all cells in file, 
    mean/SD/cv based on predicited spikes for this cell
    also returns time_stamp_mean, time_stamp_sds, and time_stamp_cvs for each
    frame besides the first and last 32 frames'''
    # cell_means = []
    cell_sds = []
    cell_cvs = []
    cell_instant_spike_rate = []
    time_stamp_mean = []
    time_stamp_sds = []
    time_stamp_cvs =  []

    frames = predictions_file.shape[1] #Number of columns
    cells = predictions_file.shape[0] #Number of rows
    sum = []
    for cell in predictions_file:
        mean=np.nanmean(cell)
        sum.append(np.nansum(cell))
        if mean > 0:

            cell_instant_spike_rate.append(mean/config.general_settings.FRAME_INTERVAL)
        # cell_means.append(mean)
            sd=np.nanstd(cell)
            cell_sds.append(sd)
            # if mean != 0:
            cv_cell = sd/mean
            # else:
            #     cv_cell = np.nan ## cells that don't fire (--> mean spike probability 0) --> makes cv nan
            cell_cvs.append(cv_cell)
        else:
            cell_sds.append(np.nan)
            cell_cvs.append(np.nan)
    
    for col_idx in range(frames):
        col_data = predictions_file[:, col_idx]
        col_sum = np.nansum(col_data)
        col_mean = col_sum / cells #manually calculating the mean because of errors in np.nanmean()
        col_sd = np.nanstd(col_data)
        time_stamp_mean.append(col_mean)
        time_stamp_sds.append(col_sd)

        if col_mean != 0:
            cv_time = col_sd / col_mean
        else:
            cv_time = np.nan
        time_stamp_cvs.append(cv_time)
    # Compute averages over frames for each row (cell)
    # avg_cell_means = np.nanmean(cell_means)
    avg_instantaneous_spike_rate = np.nanmean(cell_instant_spike_rate)
    avg_cell_sds = np.nanmean(cell_sds)
    avg_cell_cvs = np.nanmean(cell_cvs)
    # Compute averages over cells for each column (time stamp)
    avg_time_stamp_mean = np.nanmean(time_stamp_mean)
    avg_time_stamp_sds = np.nanmean(time_stamp_sds)
    avg_time_stamp_cvs = np.nanmean(time_stamp_cvs)
    
    return avg_instantaneous_spike_rate, avg_cell_sds, avg_cell_cvs, avg_time_stamp_mean, avg_time_stamp_sds, avg_time_stamp_cvs

def basic_estimated_stats_per_cell(predictions_file):
    '''returns means, SDs, cvs for all cells in file, mean/SD/cv based on predicited spikes for this cell'''
    means = []
    sds = []
    cvs = []
    for cell in predictions_file:
        mean=np.nanmean(cell)
        means.append(mean)
        sd=np.nanstd(cell)
        sds.append(sd)
        if mean != 0:
            cv_cell = sd/mean
        else:
            cv_cell = np.nan ## cells that don't fire (--> mean spike probability 0) --> makes cv nan
        cvs.append(cv_cell)
    return means, sds, cvs
 
def summed_spike_probs_per_cell(prediction_deltaF_file):

    summed_spike_probs_cell = []
    for cell in prediction_deltaF_file:
        summed_spike_probs_cell.append(np.nansum(cell))
    return summed_spike_probs_cell

def calculate_deltaF(F_file, config, event_threshold = None):
    """
    Convert raw fluorescence (F.npy) into change in fluorescence compared to baseline (dF / F0).

    Args:
    -----------
    F_file : str
        Path to NumPy array containing raw flourescence (F.npy) trace from suite2p.
    
    event_threshold: float
        Threshold (in MAD units) to mask obvious events by multiplying threshold by standard deviation. 
        The Default value is 3; smaller values will limit the number of baseline points used for correction.

    Returns:
    --------
    deltaF : 1D numpy array
        dF/F0 normalized fluorescence
        MAD baseline estimated
        ZhangFit / airPLS automated baseline correction
        deltaF is saved into the suite2p output folder generated from suite2p ROI detection.
    """

    savepath = rf"{F_file}".replace("\\F.npy","") ## make savepath original folder, indicates where deltaF.npy is saved
    F = np.load(rf"{F_file}", allow_pickle=True)
    Fneu = np.load(rf"{F_file[:-4]}"+"neu.npy", allow_pickle=True)
    deltaF= []
    for f, fneu in zip(F, Fneu):
        corrected_trace = f - (0.7*fneu) ## neuropil correction

        #Remove bleaching to generate change in Fluorescence
        

        #Determine baseline F0 value
        trace_median = np.median(corrected_trace)
        trace_mad = np.median(np.abs(corrected_trace - trace_median))
        norm_sigma = 1.4826*trace_mad
        baseline_mask = np.abs(corrected_trace - trace_median) < event_threshold * norm_sigma
        F0 = np.median(corrected_trace[baseline_mask])

        #calculate dF / F0
        normalized_F = (corrected_trace - F0)/F0
        
        deltaF.append(normalized_F)
        
    deltaF = np.array(deltaF)
    deltaF = np.squeeze(deltaF)
    if not os.path.exists(f"{savepath}/deltaF.npy"):
        np.save(f"{savepath}/deltaF.npy", deltaF, allow_pickle=True)
        print(f"delta F traces saved as deltaF.npy under {savepath}\n")
    else:
        print(f"deltaF files already exist for {F_file[len(config.general_settings.main_folder)+1:-21]}")

    return deltaF


def calculate_deltaF_airPLS(F_file, config, event_threshold = None, lambda_window = None):
    """
    Convert raw fluorescence (F.npy) into change in fluorescence compared to baseline (dF / F0).

    Args:
    -----------
    F_file : str
        Path to NumPy array containing raw flourescence (F.npy) trace from suite2p.
    
    event_threshold: float
        Threshold (in MAD units) to mask obvious events by multiplying threshold by standard deviation. 
        The Default value is 3; smaller values will limit the number of baseline points used for correction.

    Returns:
    --------
    deltaF : 1D numpy array
        dF/F0 normalized fluorescence
        MAD baseline estimated
        ZhangFit / airPLS automated baseline correction
        deltaF is saved into the suite2p output folder generated from suite2p ROI detection.
    """

    savepath = rf"{F_file}".replace("\\F.npy","") ## make savepath original folder, indicates where deltaF.npy is saved
    F = np.load(rf"{F_file}", allow_pickle=True)
    Fneu = np.load(rf"{F_file[:-4]}"+"neu.npy", allow_pickle=True)
    deltaF= []
    for f, fneu in zip(F, Fneu):
        corrected_trace = f - (0.7*fneu) ## neuropil correction

        #Remove bleaching to generate change in Fluorescence
        baseline_corrected = BaselineRemoval(corrected_trace)
        airPLS_corrected = baseline_corrected.ZhangFit(lambda_= lambda_window)

        #Determine baseline F0 value
        trace_median = np.median(corrected_trace)
        trace_mad = np.median(np.abs(corrected_trace - trace_median))
        norm_sigma = 1.4826*trace_mad
        baseline_mask = np.abs(corrected_trace - trace_median) < event_threshold * norm_sigma
        F0 = np.median(corrected_trace[baseline_mask])

        #calculate dF / F0
        normalized_F = (airPLS_corrected - F0)/F0
        
        deltaF.append(normalized_F)
        
    deltaF = np.array(deltaF)
    deltaF = np.squeeze(deltaF)
    if not os.path.exists(f"{savepath}/deltaF.npy"):
        np.save(f"{savepath}/deltaF.npy", deltaF, allow_pickle=True)
        print(f"delta F traces saved as deltaF.npy under {savepath}\n")
    else:
        print(f"deltaF files already exist for {F_file[len(config.general_settings.main_folder)+1:-21]}")

    return deltaF

def rolling_med(input_series, window_size):
    """
    Calculate rolling minimum value (input_series.rolling()) over different windows of the input trace.

    Args:
    -----------
        input_series: 1D NumPy array
            raw_trace / F.npy / deltaF.npy
        window_size: int
            Size of window to measure with each iteration

    Returns:
    -------- 
        m: int / float
            Smallest local minimum across all windows
    """
    r = input_series.rolling(window_size, min_periods=1)
    m = r.median()
    return m

def remove_bleaching(input_trace, baseline_correction, window = None):
    """
    Basic first-order polynomial function to remove bleaching from single ROI calcium imaging trace

    Args:
    -----------
        input_trace: 1D array
            raw fluorescence trace (F.npy or corrected: F.npy - 0.7*Fneu.npy)
            functions by processing one ROI at a time
        baseline_correction: str
            String name of function to call for removing bleaching from fluorescence trace
            Accepts 'rolling_min' or 'rolling_med' as possible values; all other values will break the function

    Returns:
    --------
        input_trace - fit(range(len(input_trace)))
            input trace adjusted by rolling minimum
            polynomial fit built on length of trace, rolling min values, and order of polynomial (e.g. 2nd)
            poly1d fits a 1 dimensional polynomial to the adjusted trace which is subtraced from the raw trace (input_Trace)

    """
    possible_corrections = ['rolling_med']
    if baseline_correction not in possible_corrections:
        print(f"Please enter a valid correction method: {possible_corrections}")
        return
    
    
    if baseline_correction == "rolling_med":
        if window is not None:
            corr_trace = rolling_med(pd.Series(input_trace), window_size = int(window))
        else:
            corr_trace = rolling_med(pd.Series(input_trace), window_size = int(len(input_trace)/10))
    # fit_coefficients = np.polyfit(range(len(corr_trace)), corr_trace, 2)
    # fit = np.poly1d(fit_coefficients)
    # return input_trace - fit(range(len(input_trace)))
    return input_trace - corr_trace



def rolling_correction_deltaF(F_file, config, event_threshold = None, lambda_window = None):
    """
    Convert raw fluorescence (F.npy) into change in fluorescence compared to baseline (dF / F0)
    using rolling median baseline correction.

    Args:
    -----------
        F_file : str
            Path to NumPy array containing raw flourescence (F.npy) trace from suite2p.
        config: SimpleNameSpace dictionary
            loaded automatically from config_loader.load_json_config_file(file = None)
        Event threshold: float, optional
            Number of standard deviations above MAD to se peak filtering; default is 2
        lambda_window: int, optional
            Number of frames to subsample for rolling median calculation

    Returns:
    --------
        deltaF : 1D numpy array
            dF/F0 normalized fluorescence
            MAD baseline estimated
            rolling median automated baseline correction
            deltaF is saved into the suite2p output folder generated from suite2p ROI detection.
    """
    savepath = rf"{F_file}".replace("\\F.npy","") ## make savepath original folder, indicates where deltaF.npy is saved
    F = np.load(rf"{F_file}", allow_pickle=True)
    Fneu = np.load(rf"{F_file[:-4]}"+"neu.npy", allow_pickle=True)
    deltaF= []
    if event_threshold is None:
        event_threshold = config.analysis_params.MAD_baseline_filter_threshold
    if lambda_window is None:
        lambda_window = config.analysis_params.lambda_window
    for f, fneu in zip(F, Fneu):
        corrected_trace = f - (0.7*fneu) ## neuropil correction

        #Remove bleaching to generate change in Fluorescence
        
        baseline_corrected = remove_bleaching(corrected_trace, 'rolling_med', window = lambda_window) #TODO make interatable with config file

        #Determine baseline F0 value
        trace_median = np.median(corrected_trace)
        trace_mad = np.median(np.abs(corrected_trace - trace_median))
        norm_sigma = 1.4826*trace_mad
        baseline_mask = np.abs(corrected_trace - trace_median) < event_threshold * norm_sigma
        F0 = np.median(corrected_trace[baseline_mask])

        #calculate dF / F0
        normalized_F = (baseline_corrected)/F0
        
        deltaF.append(normalized_F)
        
    deltaF = np.array(deltaF)
    deltaF = np.squeeze(deltaF)
    if not os.path.exists(f"{savepath}/deltaF.npy") and not config.analysis_params.overwrite_suite2p:
        np.save(f"{savepath}/deltaF.npy", deltaF, allow_pickle=True)
        print(f"delta F traces saved as deltaF.npy under {savepath}\n")
    elif os.path.exists(f"{savepath}/deltaF.npy") and config.analysis_params.overwrite_suite2p:
        np.save(f"{savepath}/deltaF.npy", deltaF, allow_pickle=True)
        print(f"delta F traces saved as deltaF.npy under {savepath}\n")
    else:
        print(f"deltaF files already exist for {F_file[len(config.general_settings.main_folder)+1:-21]}")

    return deltaF
