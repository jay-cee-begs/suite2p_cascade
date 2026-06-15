import os
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
import matplotlib.cm as cm
import random
# from scipy.signal import find_peaks
import pandas as pd
from scipy.ndimage import binary_dilation, binary_fill_holes
import scipy.stats as stats
from PIL import Image
import seaborn as sns #needed for aggregated feature plots
# import pynapple as nap #TODO if you need Pynapple plots, you cannot use alongside cascade as it will break the code
from batch_gui.config_loader import load_json_config_file, load_json_dict

_DEFAULT_CONFIG = load_json_config_file()
config = _DEFAULT_CONFIG

def random_individual_cell_histograms(deltaF_file, roi_percent = 5):
    """
    Plot a histogram of frames from a fluorescence trace for a percentage of the 
    total ROIs at random
    
    Args:
    ----------
        deltaF_file : str
          Path to deltaF.npy file.
        roi_percent: int, default = 5
            Percentage of total ROIs to plot the fluorescence of as histograms
    Returns:
    ----------
        plt.hist(deltaF[i]) where i is a random ROI chosen from the population
    """
    
    array = np.load(rf"{deltaF_file}")
    sample = random.sample(range(0, len(array)), roi_percent)
    for i in sample: ## alterantive i in range(len(array)) to plot all
      plt.figure(figsize=(5,5))
      plt.hist(array[i], density=True, bins=200)
      plt.title(f'Histogram df/F fluorescence cell {i}')
      plt.show()

def deltaF_histogram_across_cells(deltaF_file):
    """
    Plot a histogram of the fluorescence of all frames across all Cells / ROIs
    from a calcium imaging recording...Likely not useful for anything except population metrics
    
    Args:
    ----------
        deltaF_file : str
          Path to deltaF.npy file.
       
    Returns:
    plt.hist(np.load(deltaF_file, allow_pickle = True))
    ----------
    """    
    array = np.load(rf"{deltaF_file}")
    list = array.flatten()
    list_cleaned = [x for x in list if not np.isnan(x)]
    plt.figure(figsize=(5,5))
    plt.hist(list_cleaned, density=True, bins=200)
    plt.title(f'Histogram df/F {deltaF_file[len(config.general_settings.main_folder)+1:]}')
    plt.show()

def histogram_total_estimated_spikes(prediction_deltaF_file, output_directory = None):
    """
    Plot a histogram of the distribution of total Cascade-estimated spikes across all detected (and accepted) ROIs.
    Plot should be highly right skewed

    Args:
    ----------
        predictions_deltaF_file : str / Path
          Path-like object pointing to Cascade deconvolution prediction file (.npy)
        
        output_directory: str / Path
            Directory where to save the generated plot; default is in the subfolder containing the image and Suite2p output

    Returns:
    ----------
        None
    """
    array = np.load(rf"{prediction_deltaF_file}")
    iscell_file = prediction_deltaF_file.replace("predictions_deltaF.npy", 'iscell.npy')
    iscell = np.load(rf"{iscell_file}", allow_pickle = True)
    iscell_mask = iscell[:,0] == 1
    filtered_array = array[iscell_mask]
    print(f"\n{prediction_deltaF_file}\nNumber of neurons in dataset: {len(filtered_array)}")
    estimated_spikes = []
    for i in range(len(filtered_array)):
        estimated_spikes.append(np.nansum(filtered_array[i]))
    print(f"For {prediction_deltaF_file[len(config.general_settings.main_folder)+1:-38]} {int(sum(estimated_spikes))} spikes were predicted in total")
    plt.figure(figsize=(5,5))
    plt.hist(estimated_spikes, bins=50, color = 'm')
    plt.xlabel("Number of predicted estimated spikes")
    plt.ylabel("Number of Neurons")
    plt.title(f'Total number of predicted spikes') # \n {prediction_deltaF_file[len(config.general_settings.main_folder)+1:-38]}
    plt.text(0.65, 0.9, f"Total Spikes \nPredicted: {int(sum(estimated_spikes))}", transform=plt.gca().transAxes)
    
    if output_directory == None:
        plt.show()
   
    else:
        figure_output_path = os.path.join(output_directory, 'spks_histogram.svg')
        png_path = os.path.join(config.output_directory, 'spks_histogram.png')
        plt.savefig(png_path, bbox_inches = 'tight')

        svg_path = os.path.join(output_directory, 'spks_histogram.svg')
        plt.savefig(figure_output_path, bbox_inches = 'tight')
        plt.savefig(svg_path, bbox_inches = 'tight')

        print(f'Well Histograms for estimated spikes saved under {figure_output_path}')
        plt.close()



def plot_somatic_traces(suite2p_dict, list = None, plot_cascade = False, trace_offset = 5, iscell_true = True, save_fig = False):
    # Get boolean mask of valid cells
    if iscell_true:
        iscell_mask = suite2p_dict['iscell'][:, 0] == 1
    else:
        iscell_mask = suite2p_dict['iscell'][:,0] ==0
    # Apply mask to deltaF
    masked_dF = suite2p_dict['deltaF'][iscell_mask]
    masked_cascade = suite2p_dict['cascade_predictions'][iscell_mask]
    if list is None:
        lst = np.random.choice(masked_dF.shape[0], size=10, replace=False)
    else:
        lst = list
    # lst = [42, 133, 58, 9, 66, 43, 78, 128, 23 ,63,  27,  28, 96, 127,  34]
    
    print(lst)

    plt.figure(figsize = (10,7))
    ax = plt.gca()
    # --- Colorblind-friendly palette ---
    colors = ['#E69F00', '#56B4E9', '#009E73', '#F0E442', 
            '#0072B2', '#D55E00', '#CC79A7', '#999999', '#000000', '#999933']
    
    frame_rate = 10
    time = np.arange(suite2p_dict["deltaF"].shape[1]) / frame_rate
    if not plot_cascade:
        plt_traces = masked_dF[lst]
        for i, trace in enumerate(plt_traces):
            offset_trace = trace + i * trace_offset
            ax.plot(time, offset_trace, color=colors[i % len(colors)], alpha=0.8)
        
    else:
        plt_traces = masked_cascade[lst]
        for i, trace in enumerate(plt_traces):
            offset_trace = trace + i * 1
            ax.plot(time, offset_trace, color=colors[i % len(colors)], alpha=0.8)

    scalebar_time = 10  # seconds
    scalebar_df = 1     # dF/F units
    x0 = time[-1] + 2
    y0 = -2

    # Horizontal and vertical bars
    ax.plot([x0, x0 + scalebar_time], [y0, y0], 'k', lw=2)
    ax.plot([x0 + scalebar_time, x0 + scalebar_time], [y0, y0 + scalebar_df], 'k', lw=2)

    # Scale bar labels
    ax.text(x0 + scalebar_time / 2, y0 - 0.3, fr"{scalebar_time}$\ s$", ha='center', va='top')
    if not plot_cascade:
        ax.text(x0 + scalebar_time + 1, y0 + scalebar_df / 3,  fr"{scalebar_df} $\Delta F / F_0$", va='center', ha='left')
    else:
        ax.text(x0 + scalebar_time + 1, y0 + scalebar_df / 3,  f"{scalebar_df} CASCADE-predicted\nSpikes", va='center', ha='left')

    # --- Minimalist figure: no axes ---
    ax.axis('off')

    # --- Optional: save to file ---
    if save_fig:
        from pathlib import Path
        import os
        save_path = suite2p_dict['data_folder']
        plot_name = suite2p_dict['data_folder'].split('\\')[0]

        if iscell_true:
            plt.savefig(os.path.join(save_path, f'{plot_name}_neuron_dF_traces.svg'))
        else:
            plt.savefig(os.path.join(save_path, f'{plot_name}_glia_dF_traces.svg'))
        # plt.savefig(os.path.join(save_path,'example_dF_traces.png'))

    plt.tight_layout()
    plt.show()

def single_cell_trace_plotting(input_f): 
    """
    Plot the fluorescence trace of a given cell. 
    NOTE: the function can only handle single fluorescence traces, to process
            multiple traces, a for loop is required

    Args:
    ----------
        input_f : 1D NumPy array
          Fluorescence data from a single ROI

    Returns:
    ----------
        plt.plot(input_f)
        peak_detection_threshold = 'grey'
        baseline estimate = 'red'  
    """
    from scipy.signal import find_peaks
    threshold = np.nanmedian(input_f)+np.nanstd(input_f)
    peaks, _ = find_peaks(input_f, distance = 5, height = threshold)
    plt.figure(figsize=(5,5))
    plt.plot(input_f)
    plt.plot(peaks, input_f[peaks], "x")
    plt.plot(np.full_like(input_f, threshold), "--",color = "grey") ## height in find_peaks
    plt.plot(np.full_like(input_f, np.nanmedian(input_f)), "--", color = 'r')
    plt.xlabel("frames")
    plt.show()
    
def get_max_spike_across_frames(predictions_deltaF_file_list):
    """
    Compute the maximum predicted Cascade spikes across files. 
    The function is primarily used to set axis limits for generating comparable plots.

    Args:
    ----------
        predictions_deltaF_file_list : list
          List of predictions_deltaF.npy files to be used 

    Returns:
    ----------
        max(total_list) : maximum predicted spikes across all files
    
    """
    total_list=[]
    for file in predictions_deltaF_file_list:
        prediction_array = np.load(rf"{file}", allow_pickle=True)
        sum_rows = np.nansum(prediction_array, axis=0)
        total_list.extend(sum_rows)
    return(max(total_list))

def plot_total_spikes_per_frame(prediction_deltaF_file, max_spikes_all_samples, output_directory = None):
    '''
    Calculate and plot the total spikes recorded from all ROIs at each frame

    Args:
    ----------
        predictions_deltaF_file_list : list
          List of predictions_deltaF.npy files to be used 
        max_spikes_all_samples : int
            The maximum number of spikes in a single frame across all samples
        output_directory : str, Path-like object, optional
            Where should the plot be saved if not None

    Returns:
    ----------
       Saves plot to output_directory if not None; otherwise plt.show()
    '''
    prediction_array = np.load(rf"{prediction_deltaF_file}", allow_pickle=True)
    iscell_file = prediction_deltaF_file.replace('predictions_deltaF.npy', 'iscell.npy')
    iscell = np.load(rf"{iscell_file}", allow_pickle = True)
    iscell_mask = iscell[:,0] == 1
    filtered_predictions = prediction_array[iscell_mask]
    sum_rows = np.nansum(filtered_predictions, axis=0)
    avg_rows = np.nanmean(filtered_predictions, axis = 0)
    plt.figure(figsize=(10,5))
    plt.plot(sum_rows, color = "green")
    plt.plot(np.full_like(sum_rows, np.mean(avg_rows)), "--", color = "k")
    plt.title(f'Estimated Network Spike Predictions')
    # plt.text(0.315, -0.115, f"{prediction_deltaF_file[len(config.general_settings.main_folder)+1:-38]}", horizontalalignment='center', verticalalignment = "center", transform=plt.gca().transAxes)
    plt.ylim(0,max_spikes_all_samples+10) ## make dynamic
    plt.ylabel("Number of Predicted Spikes")
    plt.xlabel(f'Frame Number (10 frame = 1s)')
    if output_directory is not None:
        save_path = os.path.join(output_directory, 'total_spikes_per_frame.svg')
        png_path =  os.path.join(output_directory, 'total_spikes_per_frame.png')
        save_path2 = os.path.join(output_directory, 'total_spikes_per_frame.png')
        plt.savefig(save_path)
        plt.savefig(png_path)
        plt.savefig(save_path2)
        print(f'Total Spikes per frame saved under {save_path}')
        plt.close()
    else:
        plt.show()

def plot_average_spike_probability_per_frame(predictions_deltaF_file, output_directory = None):
    '''
    Calculate and plot the average spikes recorded divided by total ROIs (real cells).
    Normalizes the output of `plot_total_spikes_per_frame`

    Args:
    ----------
        predictions_deltaF_file_list : list
          List of predictions_deltaF.npy files to be used 
        max_spikes_all_samples : int
            The maximum number of spikes in a single frame across all samples
        output_directory : str, Path-like object, optional
            Where should the plot be saved if not None

    Returns:
    ----------
       Saves plot to output_directory if not None; otherwise plt.show()
    '''
   
    prediction_array = np.load(rf"{predictions_deltaF_file}", allow_pickle=True)
    iscell_file = predictions_deltaF_file.replace('predictions_deltaF.npy', 'iscell.npy')
    iscell = np.load(rf"{iscell_file}", allow_pickle = True)
    
    iscell_mask = iscell[:,0] == 1
    filtered_predictions = prediction_array[iscell_mask]
    
    sum_rows = np.nansum(filtered_predictions, axis=0)
    average = sum_rows/(len(filtered_predictions))

    plt.figure(figsize=(10,5))
    plt.plot(average, color = "green", label="average spike probability")

    plt.title(f'Average spike probability across cells per frame')
    plt.text(0.315, -0.115, f"{predictions_deltaF_file[len(config.general_settings.main_folder)+1:-38]}", horizontalalignment='center', verticalalignment = "center", transform=plt.gca().transAxes)
    plt.ylim(0,1)
    if output_directory:
        save_path = os.path.join(output_directory, 'avg_spike_probability_per_frame.svg')
        png_path =  os.path.join(output_directory, 'avg_spike_probability_per_frame.png')
        plt.savefig(save_path)
        plt.savefig(png_path)
        print(f'Average spike probability per frame saved under {save_path}')
        plt.close()
    else:
        plt.show()

## ROI image
def getImg(ops):
    """
    Generate a normalized image from suite2p ops for ROI visualization.

    Args:
    ----------
        ops : dict
            Suite2p ops dictionary containing imaging outputs.
        config : SimpleNameSpace dict
            Configuration JSON file with analysis parameters.

    Returns:
    ----------
        mimg: np.ndarray
            Normalized 8-bit image for visualization saved as an array.
    """
    Img = ops["meanImg"] # Also "max_proj", "meanImg", "meanImgE"
    mimg = Img # Use suite-2p source-code naming
    mimg1 = np.percentile(mimg,1)
    mimg99 = np.percentile(mimg,99)
    mimg = (mimg - mimg1) / (mimg99 - mimg1)
    mimg = np.maximum(0,np.minimum(1,mimg))
    mimg *= 255
    mimg = mimg.astype(np.uint8)
    return mimg

    #redefine locally suite2p.gui.utils import boundary
def boundary(ypix,xpix):
    """
    Compute the boundary pixels of a given ROI mask.
    Function is taken directly from suite2p src code.

    Args:
    ----------
        ypix : np.ndarray 
            Y-coordinates of ROI pixels.
        xpix : np.ndarray
            X-coordinates of ROI pixels.

    Returns:
    ----------
        tuple[np.ndarray, np.ndarray]:
            Arrays of y and x coordinates representing the boundary pixels.
    """
    ypix = np.expand_dims(ypix.flatten(),axis=1)
    xpix = np.expand_dims(xpix.flatten(),axis=1)
    npix = ypix.shape[0]
    if npix>0:
        msk = np.zeros((np.ptp(ypix)+6, np.ptp(xpix)+6), bool) 
        msk[ypix-ypix.min()+3, xpix-xpix.min()+3] = True
        msk = binary_dilation(msk)
        msk = binary_fill_holes(msk)
        k = np.ones((3,3),dtype=int) # for 4-connected
        k = np.zeros((3,3),dtype=int); k[1] = 1; k[:,1] = 1 # for 8-connected
        out = binary_dilation(msk==0, k) & msk

        yext, xext = np.nonzero(out)
        yext, xext = yext+ypix.min()-3, xext+xpix.min()-3
    else:
        yext = np.zeros((0,))
        xext = np.zeros((0,))
    return yext, xext

#gets neuronal indices
def getStats(suite2p_dict, frame_shape, output_df, config, use_iscell = False):
    """
    Classify ROIs and compute spatial/statistical properties.

    ROIs are categorized into synaptic, dendritic, or rejected based on
    thresholds for peak count, skewness, and compactness.

    Args:
    ----------
        suite2p_dict : dict
            Dictionary containing suite2p outputs (stat, F, Fneu, iscell).
        frame_shape : tuple[int, int]
            Shape of the imaging frame (height, width).
        output_df : pandas.DataFrame
            DataFrame containing peak detection results.
        config  : SimpleNameSpace dict
            Configuration dictionary / JSON with analysis thresholds.
        use_iscell : bool, optional
            If True, classification is based only on iscell flag.

    Returns:
    ----------
        tuple :
            scatters (dict): ROI boundary coordinates.
            nid2idx (dict): Mapping of ROI IDs to indices.
            nid2idx_rejected (dict): Rejected ROI indices.
            pixel2neuron (np.ndarray): Pixel-to-ROI mapping.
            synapse_ID (list): List of accepted synapse IDs.
            nid2idx_dendrite (dict): Dendritic ROI indices.
            nid2idx_synapse (dict): Synaptic ROI indices.
    """
    stat = suite2p_dict['stat']
    iscell = suite2p_dict['iscell']
    F = suite2p_dict["F"]
    Fneu = suite2p_dict["Fneu"]
    MIN_CASCADE_ACTIVITY = config.analysis_params.cascade_activity_threshold
    min_radius = 3
    pixel_weight_threshold = 0.5
    min_skew = 1
    pixel2neuron = np.full(frame_shape, fill_value=np.nan, dtype=float)
    scatters = dict(x=[], y=[], color=[], text=[])
    nid2idx = {}
    nid2idx_rejected = {}
    print(f"Number of detected ROIs: {stat.shape[0]}")
    
    if not use_iscell:

        for n in range(stat.shape[0]):
            estimated_spikes = output_df.iloc[n]["EstimatedSpikes"]
            radius = stat.iloc[n]['radius']
            skew = stat.iloc[n]['skew']

            sample_F = F[n]
            sample_Fneu = Fneu[n]

            med_pixel_weight = np.median(stat.iloc[n]['lam'])
            if med_pixel_weight > pixel_weight_threshold and radius > min_radius and sample_F.min() > sample_Fneu.min():
                nid2idx[n] = len(scatters["x"]) # Assign new idx
            else:
                nid2idx_rejected[n] = len(scatters["x"])
            ypix = stat.iloc[n]['ypix'].flatten() - 1 #[~stat.iloc[n]['overlap']] - 1
            xpix = stat.iloc[n]['xpix'].flatten() - 1 #[~stat.iloc[n]['overlap']] - 1

            valid_idx = (xpix>=0) & (xpix < frame_shape[1]) & (ypix >=0) & (ypix < frame_shape[0])
            ypix = ypix[valid_idx]
            xpix = xpix[valid_idx]
            yext, xext = boundary(ypix, xpix)
            scatters['x'] += [xext]
            scatters['y'] += [yext]
            pixel2neuron[ypix, xpix] = n
    else:
        for n in range(stat.shape[0]):

            if iscell[n,0] == 1 or iscell[n,0] == 1.0 or iscell[n,0] == True:
                nid2idx[n] = len(scatters["x"]) # Assign new idx
            else:
                nid2idx_rejected[n] = len(scatters["x"])

            ypix = stat.iloc[n]['ypix'].flatten() - 1 #[~stat.iloc[n]['overlap']] - 1
            xpix = stat.iloc[n]['xpix'].flatten() - 1 #[~stat.iloc[n]['overlap']] - 1

            valid_idx = (xpix>=0) & (xpix < frame_shape[1]) & (ypix >=0) & (ypix < frame_shape[0])
            ypix = ypix[valid_idx]
            xpix = xpix[valid_idx]
            yext, xext = boundary(ypix, xpix)
            scatters['x'] += [xext]
            scatters['y'] += [yext]
            pixel2neuron[ypix, xpix] = n

    return scatters, nid2idx, nid2idx_rejected, pixel2neuron


def dispPlot(MaxImg, scatters, nid2idx, nid2idx_rejected,
             pixel2neuron, F, Fneu, save_path=None, axs=None):
             """
            Display ROI overlays of accepted ROIs on a background image.

            Args:
            ----------
                MaxImg : np.ndarray
                    Background image (e.g., max projection).
                scatters : dict
                    ROI boundary coordinates.
                nid2idx : dict
                    Mapping of ROI IDs to indices.
                nid2idx_rejected : dict
                    Rejected ROI indices.
                pixel2neuron : np.ndarray
                    Pixel-to-ROI mapping array.
                F : np.ndarray
                    Fluorescence traces.
                Fneu : np.ndarray
                    Neuropil signals.
                save_path : str, optional
                    File path to save the output image.
                axs : matplotlib.axes.Axes, optional
                    Existing axes to plot on.

            Returns:
            ----------
                Returns Imaged Region overlayed with detected / accepted ROIs
                if axis is provided, will put plot into a figure
             """
             if axs is None:
                fig = plt.figure(constrained_layout=True)
                NUM_GRIDS=12
                gs = fig.add_gridspec(NUM_GRIDS, 1)
                ax1 = fig.add_subplot(gs[:NUM_GRIDS-2])
                fig.set_size_inches(12,14)
             else:
                 ax1 = axs
                 ax1.set_xlim(0, MaxImg.shape[0])
                 ax1.set_ylim(MaxImg.shape[1], 0)
             ax1.imshow(MaxImg, cmap='gist_gray')
             ax1.tick_params(axis='both', which='both', bottom=False, top=False, 
                             labelbottom=False, left=False, right=False, labelleft=False)
             print("Neurons count:", len(nid2idx))
             norm = Normalize(vmin=0, vmax=1, clip=True) 
             mapper = cm.ScalarMappable(norm=norm, cmap=cm.gist_rainbow) 

             def plotDict(n2d2idx_dict, override_color = None):
                 for neuron_id, idx in n2d2idx_dict.items():
                     color = override_color if override_color else mapper.to_rgba(scatters['color'][idx])
                            # print(f"{idx}: {scatters['x']} - {scatters['y'][idx]}")
                            
                     sc = ax1.scatter(scatters["x"][idx], scatters['y'][idx], color = color, 
                                      marker='.', s=1)
             plotDict(nid2idx, 'cyan')
             #TODO make this editable by the user
            #  plotDict(nid2idx_rejected, 'm')
             ax1.set_title(f"{len(nid2idx)} neurons used (cyan) out of {len(nid2idx)+len(nid2idx_rejected)} total neurons detected") 
             if save_path:
                 plt.savefig(save_path)
                 plt.close(fig)
             else:
                 return ax1

def dispGlia(MaxImg, scatters, nid2idx, nid2idx_rejected,
             pixel2neuron, F, Fneu, save_path=None, axs=None):
             """
            Display ROI overlays of accepted ROIs on a background image.
            NOTE: This is only viable when using a cell-permeable dye to stain all cells

            Args:
            ----------
                MaxImg : np.ndarray
                    Background image (e.g., max projection).
                scatters : dict
                    ROI boundary coordinates.
                nid2idx : dict
                    Mapping of ROI IDs to indices.
                nid2idx_rejected : dict
                    Rejected ROI indices.
                pixel2neuron : np.ndarray
                    Pixel-to-ROI mapping array.
                F : np.ndarray
                    Fluorescence traces.
                Fneu : np.ndarray
                    Neuropil signals.
                save_path : str, optional
                    File path to save the output image.
                axs : matplotlib.axes.Axes, optional
                    Existing axes to plot on.

            Returns:
            ----------
                Returns Imaged Region overlayed with detected / rejected ROIs
                if axis is provided, will put plot into a figure
                Rejected ROIs correspond to glia only if a cell-permeable indicator dye is used.
             """
             if axs is None:
                fig = plt.figure(constrained_layout=True)
                NUM_GRIDS=12
                gs = fig.add_gridspec(NUM_GRIDS, 1)
                ax1 = fig.add_subplot(gs[:NUM_GRIDS-2])
                fig.set_size_inches(12,14)
             else:
                 ax1 = axs
                 ax1.set_xlim(0, MaxImg.shape[0])
                 ax1.set_ylim(MaxImg.shape[1], 0)
             ax1.imshow(MaxImg, cmap='gist_gray')
             ax1.tick_params(axis='both', which='both', bottom=False, top=False, 
                             labelbottom=False, left=False, right=False, labelleft=False)
             print("Neurons count:", len(nid2idx))
             norm = Normalize(vmin=0, vmax=1, clip=True) 
             mapper = cm.ScalarMappable(norm=norm, cmap=cm.gist_rainbow) 

             def plotDict(n2d2idx_dict, override_color = None):
                 for neuron_id, idx in n2d2idx_dict.items():
                     color = override_color if override_color else mapper.to_rgba(scatters['color'][idx])
                            # print(f"{idx}: {scatters['x']} - {scatters['y'][idx]}")
                            
                     sc = ax1.scatter(scatters["x"][idx], scatters['y'][idx], color = color, 
                                      marker='.', s=1)
             plotDict(nid2idx_rejected, 'yellow')
             #TODO make this editable by the user
            #  plotDict(nid2idx_rejected, 'm')
             ax1.set_title(f"{len(nid2idx_rejected)} Glia detected (yellow)") 
             if save_path:
                 plt.savefig(save_path)
                 plt.close(fig)
             else:
                 return ax1


def create_suite2p_ROI_masks(stat, frame_shape, nid2idx, output_path):
    """
    Generate and save ROI masks for external analysis tools.

    Creates a binary mask image where ROI pixels are labeled and saves
    it as an image file.

    Args:
    ----------
        stat (pandas.DataFrame):
            Suite2p stat DataFrame containing ROI pixel coordinates.
        frame_shape (tuple[int, int]):
            Shape of the imaging frame (height, width).
        nid2idx (dict):
            Mapping of ROI IDs to indices.
        output_path (str):
            File path to save the ROI mask image.

    Returns:
    ----------
        tuple :
            PIL.Image.Image: Saved image object.
            np.ndarray: ROI mask array.
    """   
    #Make an empty array to contain the nid2idx masks
    roi_masks = np.zeros(frame_shape, dtype=int)

    #Iterate through the ROIs in nid2idx and fill in the masks
    for n in nid2idx.keys():
        ypix = stat.iloc[n]['ypix'].flatten() - 1
        xpix = stat.iloc[n]['xpix'].flatten() - 1

        #Ensure the indices are within the bounds of the frame_shape

        valid_idx = (xpix >= 0) & (xpix<frame_shape[1]) & (ypix >=0) & (ypix < frame_shape[0])
        ypix = ypix[valid_idx]
        xpix = xpix[valid_idx]

        #Set ROI pixels to mask

        roi_masks[ypix, xpix] = 255 # n + 1 helps to differentiate masks from background

    im = Image.fromarray(roi_masks)
    im.save(output_path)
    return im, roi_masks
    

_available_tests = {
    "mann-whitney-u": stats.mannwhitneyu,
    "wilcoxon": stats.wilcoxon,
    "paired_t": stats.ttest_rel,
}

def get_significance_text(series1, series2, test="mann-whitney-u", bonferroni_correction=1, show_ns=False, 
                          cutoff_dict={"*":0.05, "**":0.01, "***":0.001, "****":0.00099}, return_string="{text}\n{pvalue:.4f}"):
    statistic, pvalue = _available_tests[test](series1, series2)
    levels, cutoffs = np.vstack(list(cutoff_dict.items())).T
    levels = np.insert(levels, 0, "n.s." if show_ns else "")
    text = levels[(pvalue < cutoffs.astype(float)).sum()]
    return return_string.format(pvalue=pvalue, text=text) #, text=text

def add_significance_bar_to_axis(ax, series1, series2, center_x, line_width):
    significance_text = get_significance_text(series1, series2, show_ns=True)
    
    original_limits = ax.get_ylim()
    
    ax.errorbar(center_x, original_limits[1], xerr=line_width/2, color="k", capsize=12)
    ax.text(center_x, original_limits[1], significance_text, ha="center", va="bottom", fontsize = 32)
    
    extended_limits = (original_limits[0], (original_limits[1] - original_limits[0]) * 1.2 + original_limits[0])
    ax.set_ylim(extended_limits)
    
    return ax

def aggregated_feature_plot(summary_stats, df, feature="SpikesFreq", agg_function="median", comparison_function="mean",
                            palette="Set3", significance_check=False, group_order=None, control_group=None, ylim=0, y_label="", x_label=""):
    """
    Add a 'group_order' parameter that takes a list of groups in the desired order.
    """
    # Flatten the multi-level columns
    summary_stats.columns = ['_'.join(col).strip() for col in summary_stats.columns.values]
    
    # Filter the required feature and reset index
    feature_col = f"{feature}_{agg_function}"
    grouped_df = summary_stats[[feature_col]].reset_index()
    grouped_df.columns = ["Group", "Time_Point", feature]
    
    if control_group is not None:
        control_avg = grouped_df[grouped_df['Group'] == control_group][feature].agg(comparison_function)
        grouped_df[feature] = grouped_df[feature].apply(lambda x: (x / control_avg) * 100)
    
    fig = plt.figure(figsize=(48, 16))
    ax = fig.add_subplot()
    color_palette = sns.color_palette(palette)
    
    sns.violinplot(x="Time_Point", y=feature, data=grouped_df, ax=ax, palette=palette, order=group_order, inner="quartile", width=0.5)

    if group_order:
        tick_positions = {group: pos for pos, group in enumerate(group_order)}
    else:
        tick_positions = {ax.get_xticklabels()[index].get_text(): ax.get_xticks()[index] for index in range(len(ax.get_xticklabels()))}

    if significance_check:
        sub_checks = [significance_check] if not any(isinstance(element, list) for element in significance_check) else significance_check
        for sub_check in sub_checks:
            add_significance_bar_to_axis(ax, 
                                         grouped_df[grouped_df["Group"] == sub_check[0]][feature], 
                                         grouped_df[grouped_df["Group"] == sub_check[1]][feature],
                                         (tick_positions[sub_check[0]] + tick_positions[sub_check[1]]) / 2,
                                         abs(tick_positions[sub_check[0]] - tick_positions[sub_check[1]]))

    ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0, frameon=False)
    ax.set_ylim([ylim, ax.get_ylim()[1]])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_ylabel(y_label, fontsize=64)
    ax.set_xlabel(x_label, fontsize=64)
    ax.set_xticklabels(ax.get_xticklabels(), fontsize=44)
    ax.set_yticklabels(ax.get_yticklabels(), fontsize=44)

    return fig