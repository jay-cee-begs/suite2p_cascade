import numpy as np
import matplotlib.pyplot as plt
import os
# importing rastermap
# (this will be slow the first time since it is compiling the numba functions)
from rastermap import Rastermap, utils
from sklearn.decomposition import TruncatedSVD

from scipy.stats import zscore

from run_cascade import functions_data_transformation as fdt, functions_general
from plotting import functions_plots
from batch_gui.config_loader import load_json_config_file

_DEFAULT_CONFIG = load_json_config_file()
config = _DEFAULT_CONFIG

def visualize_culture_activity(suite2p_dict, save_path):
    iscell_mask = suite2p_dict['iscell'][:,0] == 1
    cascade_activity = suite2p_dict['cascade_predictions']
    active_neuron_activity = cascade_activity[iscell_mask]

    spks = np.nan_to_num(active_neuron_activity)
    ops = suite2p_dict['ops']
    total_activity = []
    for frame in active_neuron_activity.T:
        total_activity.append(np.sum(frame))
    total_activity = np.array(total_activity)
    # deltaF = active_neuron_activity['deltaF']

    # zscore activity (each neuron activity trace is then mean 0 and standard-deviation 1)
    spks = zscore(spks, axis=1)
    
    try:
        model = Rastermap(n_clusters=None, # None turns off clustering and sorts single neurons 
                    n_PCs=32, # use fewer PCs than neurons
                    locality=0.1, # some locality in sorting (this is a value from 0-1)
                    time_lag_window=15, # use future timepoints to compute correlation
                    grid_upsample=0, # 0 turns off upsampling since we're using single neurons
                    ).fit(spks)
        y = model.embedding # neurons x 1
        isort = model.isort
    except ValueError as e:
        print("Too many neurons, setting nclusters to 100")
        model = Rastermap(n_clusters=100, # None turns off clustering and sorts single neurons 
                    n_PCs=128, # use fewer PCs than neurons
                    locality=0.1, # some locality in sorting (this is a value from 0-1)
                    time_lag_window=15, # use future timepoints to compute correlation
                    grid_upsample=10, # 10 is default value and good for 'large recordings' turn on for visualization                    ).fit(spks)
                    ).fit(spks)
        y = model.embedding # neurons x 1
        isort = model.isort    
        
    xmin = 0
    xmax = len(suite2p_dict['F'].T)

    frame_rate = int(config.general_settings.frame_rate)

    # make figure with grid for easy plotting
    fig = plt.figure(figsize=(16,8), dpi=200)
    grid = plt.GridSpec(10, 40, figure=fig, wspace = 0.1, hspace = 0.4)
    

    # plot total estimated spikes
    ax1 = plt.subplot(grid[1, :20])
    ax1.plot(total_activity[xmin:xmax], color=0.5*np.ones(3))
    ax1.xaxis.set_visible(False)
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.spines['bottom'].set_visible(False)
    ax1.set_title("Total Estimated Spikes per Frame")

    # plot sorted neural activity
    ax2 = plt.subplot(grid[2:, :20])
    raster = ax2.imshow(spks[isort, xmin:xmax], cmap="gray_r", vmin=0, vmax=2, aspect="auto")
    #LIMIT plot time
    # xmax = 119 * frame_rate  
    # ax1.set_xlim([0, xmax])
    # ax2.set_xlim([0, xmax])
    num_ticks = 8
    tick_positions = np.linspace(xmin, xmax, num_ticks, dtype=int)
    tick_labels = (tick_positions / frame_rate).astype(int)
    ax2.set_xticks(tick_positions)
    ax2.set_xticklabels(tick_labels)
    ax2.set_xlabel("Time (seconds)")
    ax2.set_ylabel("NeuronID")

    # Add colorbar for z-score scale
    # cbar = plt.colorbar(raster, ax=ax2, orientation='vertical', pad=0.02)
    # cbar.set_label('Z-score', rotation=270, labelpad=15)
    # cbar.set_ticks([0, 1, 2])  # Adjust ticks as necessary
    # cbar.ax.set_yticklabels(['0', '1', '2'])  # Adjust labels as necessary


    ax1.set_xlim(ax2.get_xlim())  # Sync x-limits
    plt.subplots_adjust(hspace=0.1)

    ax3 = plt.subplot(grid[2:, 20:])
    ops = suite2p_dict["ops"]
    Img = functions_plots.getImg(ops)
    scatters, nid2idx, nid2idx_rejected, pixel2neuron = functions_plots.getStats(suite2p_dict, Img.shape, fdt.df_from_suite2p_dict(suite2p_dict), use_iscell = config.analysis_params.use_suite2p_ROI_classifier)
    functions_plots.dispPlot(Img, scatters, nid2idx, nid2idx_rejected, pixel2neuron, suite2p_dict["F"], suite2p_dict["Fneu"], axs=ax3)
    plt.savefig(os.path.join(save_path, "dF_F_raster_summary.png"))
    plt.savefig(os.path.join(save_path, "dF_F_raster_summary.svg"))
    plt.close()


def visualize_glia_activity(suite2p_dict, save_path):
    iscell_mask = suite2p_dict['iscell'][:,0] == 0
    active_neuron_activity = {}
    for key in suite2p_dict.keys():
        try:
            active_neuron_activity[key] = suite2p_dict[key][iscell_mask]
        except TypeError as e:
            print("Skipping string-like keys")

    active_neuron_activity['cascade_predictions'] = np.nan_to_num(active_neuron_activity['cascade_predictions'])
    ops = suite2p_dict['ops']
    total_activity = []
    for frame in active_neuron_activity['cascade_predictions'].T:
        total_activity.append(np.sum(frame))
    total_activity = np.array(total_activity)
    spks = active_neuron_activity['cascade_predictions']
    spks = active_neuron_activity['deltaF']
    n_neurons, n_time = spks.shape
    print(f"{n_neurons} neurons by {n_time} timepoints")
    # zscore activity (each neuron activity trace is then mean 0 and standard-deviation 1)
    spks = zscore(spks, axis=1)
    
    try:
        model = Rastermap(n_clusters=None, # None turns off clustering and sorts single neurons 
                    n_PCs=32, # use fewer PCs than neurons
                    locality=0.1, # some locality in sorting (this is a value from 0-1)
                    time_lag_window=15, # use future timepoints to compute correlation
                    grid_upsample=0, # 0 turns off upsampling since we're using single neurons
                    ).fit(spks)
        y = model.embedding # neurons x 1
        isort = model.isort
    except ValueError as e:
        print("Too many neurons, setting nclusters to 100")
        model = Rastermap(n_clusters=100, # None turns off clustering and sorts single neurons 
                    n_PCs=128, # use fewer PCs than neurons
                    locality=0.1, # some locality in sorting (this is a value from 0-1)
                    time_lag_window=15, # use future timepoints to compute correlation
                    grid_upsample=10, # 10 is default value and good for 'large recordings' turn on for visualization                    ).fit(spks)
                    ).fit(spks)
        y = model.embedding # neurons x 1
        isort = model.isort
    
    xmin = 0
    xmax = len(suite2p_dict['F'].T)
    frame_rate = int(config.general_settings.frame_rate)

    # make figure with grid for easy plotting
    fig = plt.figure(figsize=(16,8), dpi=200)
    grid = plt.GridSpec(10, 40, figure=fig, wspace = 0.1, hspace = 0.4)
    

    # plot total estimated spikes
    ax1 = plt.subplot(grid[1, :20])
    ax1.plot(total_activity[xmin:xmax], color=0.5*np.ones(3))
    ax1.xaxis.set_visible(False)
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.spines['bottom'].set_visible(False)
    ax1.set_title("Total Estimated Spikes per Frame")

    # plot sorted neural activity
    ax2 = plt.subplot(grid[2:, :20])
    raster = ax2.imshow(spks[isort, xmin:xmax], cmap="gray_r", vmin=0, vmax=2, aspect="auto")
    #LIMIT glia plot time
    # xmax = 119 * frame_rate  
    # ax1.set_xlim([0, xmax])
    # ax2.set_xlim([0, xmax])
    num_ticks = 8
    tick_positions = np.linspace(xmin, xmax, num_ticks, dtype=int)
    tick_labels = (tick_positions / frame_rate).astype(int)
    ax2.set_xticks(tick_positions)
    ax2.set_xticklabels(tick_labels)
    ax2.set_xlabel("Time (seconds)")
    ax2.set_ylabel("GliaID")

    # Add colorbar for z-score scale
    # cbar = plt.colorbar(raster, ax=ax2, orientation='vertical', pad=0.02)
    # cbar.set_label('Z-score', rotation=270, labelpad=15)
    # cbar.set_ticks([0, 1, 2])  # Adjust ticks as necessary
    # cbar.ax.set_yticklabels(['0', '1', '2'])  # Adjust labels as necessary


    ax1.set_xlim(ax2.get_xlim())  # Sync x-limits
    plt.subplots_adjust(hspace=0.1)

    ax3 = plt.subplot(grid[2:, 20:])
    ops = suite2p_dict["ops"]
    Img = functions_plots.getImg(ops)
    scatters, nid2idx, nid2idx_rejected, pixel2neuron = functions_plots.getStats(suite2p_dict, Img.shape, fdt.df_from_suite2p_dict(suite2p_dict), use_iscell = config.analysis_params.use_suite2p_ROI_classifier)
    functions_plots.dispGlia(Img, scatters, nid2idx, nid2idx_rejected, pixel2neuron, suite2p_dict["F"], suite2p_dict["Fneu"], axs=ax3)
    plt.savefig(os.path.join(save_path, "glia_dF_F_raster_summary.png"))
    plt.savefig(os.path.join(save_path, "glia_dF_F_raster_summary.svg"))

    plt.close()


def simple_raster_plot(suite2p_dict, color_map, save_path = None,frame_rate = None, z_score_activity = False, max_neuron_count = None, show_plot = False):
    iscell_mask = suite2p_dict['iscell'][:,0] == 1
    cascade_activity = suite2p_dict['cascade_predictions']
    #get only active neurons cascade predictions
    active_neuron_activity = cascade_activity[iscell_mask]

    spks = np.nan_to_num(active_neuron_activity)
    if z_score_activity:
        spks = zscore(spks, axis=1)
    ops = suite2p_dict['ops']

    #calculate total estimated spikes for ax1
    total_activity = []
    for frame in active_neuron_activity.T:
        total_activity.append(np.sum(frame))
    total_activity = np.array(total_activity)
    
    plt.rcParams['svg.fonttype'] = 'none'
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = 'Arial'
    plt.rcParams['svg.fonttype'] = 'none'
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = 'Arial'
    xmin = 0
    xmax = len(suite2p_dict['F'].T)
    if frame_rate is None:
        frame_rate = int(config.general_settings.frame_rate)

    # make figure with grid for easy plotting
    fig = plt.figure(figsize=(16,8), dpi=200)
    grid = plt.GridSpec(10, 40, figure=fig, wspace = 0.1, hspace = 0.4)
    

    # plot total estimated spikes from total_activity
    ax1 = plt.subplot(grid[1, :20])
    ax1.plot(total_activity[xmin:xmax], color=0.5*np.ones(3))
    if max_neuron_count is not None:
        ax1.set_ylim(0,max_neuron_count)
    ax1.xaxis.set_visible(False)
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.spines['bottom'].set_visible(False)
    ax1.set_title("Total Estimated Spikes per Frame")

    # plot individual neural activity
    ax2 = plt.subplot(grid[2:, :20])
    raster = ax2.imshow(spks[xmin:xmax], cmap=color_map, vmin=0, vmax=1, aspect="auto")
                        #, interpolation="nearest")
    #LIMIT plot time
    # xmax = 119 * frame_rate  
    # ax1.set_xlim([0, xmax])
    # ax2.set_xlim([0, xmax])
    # ax2.set_ylim([0,165])
    num_ticks = 8
    tick_positions = np.linspace(xmin, xmax, num_ticks, dtype=int)
    tick_labels = (tick_positions / frame_rate).astype(int)
    ax2.set_xticks(tick_positions)
    ax2.set_xticklabels(tick_labels)
    ax2.set_xlabel("Time (seconds)")
    ax2.set_ylabel("NeuronID")
    # ax2.set_ylim(0,370)

    # Add colorbar for z-score scale
    # cbar = plt.colorbar(raster, ax=ax2, orientation='vertical', pad=0.02)
    # cbar.set_label('Z-score', rotation=270, labelpad=15)
    # cbar.set_ticks([0, 1, 2])  # Adjust ticks as necessary
    # cbar.ax.set_yticklabels(['0', '1', '2'])  # Adjust labels as necessary


    ax1.set_xlim(ax2.get_xlim())  # Sync x-limits
    plt.subplots_adjust(hspace=0.1)

    ax3 = plt.subplot(grid[2:, 20:])
    ops = suite2p_dict["ops"]
    Img = functions_plots.getImg(ops)
    scatters, nid2idx, nid2idx_rejected, pixel2neuron = functions_plots.getStats(suite2p_dict, Img.shape, fdt.df_from_suite2p_dict(suite2p_dict), use_iscell = config.analysis_params.use_suite2p_ROI_classifier)
    file = suite2p_dict['file_name'].split('\\')[0]
    functions_plots.dispPlot(Img, scatters, nid2idx, nid2idx_rejected, pixel2neuron, suite2p_dict["F"], suite2p_dict["Fneu"], axs=ax3)
    group = suite2p_dict['Group']
    file = suite2p_dict['data_folder'].split('\\')[-1]
    if save_path is not None:
        
        plt.savefig(os.path.join(save_path, f"{group}_{file}_raster_summary.png"))
        plt.savefig(os.path.join(save_path, f"{group}_{file}_raster_summary.svg"))
    # plt.show()

    if show_plot:
        plt.show()
    plt.close()


def main(config_file_path = None):
    print("Executing rastermap")
    if config_file_path is None:
        config = load_json_config_file()
    else:
        from pathlib import Path
        config = load_json_config_file(Path(config_file_path))
    from run_cascade.functions_data_transformation import load_suite2p_paths, get_file_name_list
    suite2p_folders = get_file_name_list(config.general_settings.main_folder, "samples", supress_printing=False)
    for folder in suite2p_folders:
        suite2p_dict = load_suite2p_paths(folder, config) 
        
        simple_raster_plot(suite2p_dict, color_map = 'binary', save_path = folder,
                           frame_rate = int(config.general_settings.frame_rate),
                           z_score_activity=False, show_plot=False)

        # visualize_culture_activity(suite2p_dict, folder)
        # visualize_glia_activity(suite2p_dict, folder)

if __name__ == '__main__':
    main()
    from batch_gui.config_loader import load_json_dict
    config_dict = load_json_dict()
    import json
    with open(os.path.join(config.general_settings.main_folder, 'analysis_config.json'), 'w') as f:
        json.dump(config_dict, f, indent = 4)
    print(f"Analysis parameters saved in {config.general_settings.main_folder} as analysis_config.json")
    from datetime import datetime

    now = datetime.now()

    current_time = now.strftime("%H:%M:%S")
    print("Current Time =", current_time)
    