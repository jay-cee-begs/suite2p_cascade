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
from batch_process.config_loader import load_json_config_file

def visualize_culture_activity(suite2p_dict, save_path):
    iscell_mask = suite2p_dict['iscell'][:,0] == 1
    active_neurons = {}
    for key in suite2p_dict.keys():
        try:
            active_neurons[key] = suite2p_dict[key][iscell_mask]
        except TypeError as e:
            print("Skipping string-like keys")

    active_neurons['cascade_predictions'] = np.nan_to_num(active_neurons['cascade_predictions'])
    ops = suite2p_dict['ops']
    total_activity = []
    for frame in active_neurons['cascade_predictions'].T:
        total_activity.append(np.sum(frame))
    total_activity = np.array(total_activity)
    spks = active_neurons['cascade_predictions']

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
                    grid_upsample=0, # 0 turns off upsampling since we're using single neurons
                    ).fit(spks)
        y = model.embedding # neurons x 1
        isort = model.isort
    
    xmin = 0
    xmax = len(suite2p_dict['F'].T)
    frame_rate = 10

    # make figure with grid for easy plotting
    fig = plt.figure(figsize=(16,8), dpi=200)
    grid = plt.GridSpec(10, 40, figure=fig, wspace = 0.1, hspace = 0.4)

    # plot total estimated spikes
    ax = plt.subplot(grid[1, :20])
    ax.plot(total_activity[xmin:xmax], color=0.5*np.ones(3))
    ax.xaxis.set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.set_title("Total Estimated Spikes per Frame")

    # plot sorted neural activity
    ax = plt.subplot(grid[2:, :20])
    ax.imshow(spks[isort, xmin:xmax], cmap="gray_r", vmin=0, vmax=2, aspect="auto")
    num_ticks = 10
    tick_positions = np.linspace(xmin, xmax, num_ticks, dtype=int)
    tick_labels = (tick_positions / frame_rate).astype(int)
    ax.set_xticks(tick_positions)
    ax.set_xticklabels(tick_labels)
    ax.set_xlabel("Time (seconds)")
    ax.set_ylabel("NeuronID")
    # plt.show()

    ax = plt.subplot(grid[2:, 20:])
    ops = suite2p_dict["ops"]
    Img = functions_plots.getImg(ops)
    scatters, nid2idx, nid2idx_rejected, pixel2neuron = functions_plots.getStats(suite2p_dict, Img.shape, fdt.create_df(suite2p_dict), use_iscell = False)
    functions_plots.dispPlot(Img, scatters, nid2idx, nid2idx_rejected, pixel2neuron, suite2p_dict["F"], suite2p_dict["Fneu"], axs=ax)
    plt.show()

def culture_PCA_clusters(suite2p_dict):
    iscell_mask = suite2p_dict['iscell'][:,0] == 1
    active_neurons = {}
    for key in suite2p_dict.keys():
        try:
            active_neurons[key] = suite2p_dict[key][iscell_mask]
        except TypeError as e:
            print("Skipping string-like keys")

    active_neurons['cascade_predictions'] = np.nan_to_num(active_neurons['cascade_predictions'])
    ops = suite2p_dict['ops']
    total_activity = []
    for frame in active_neurons['cascade_predictions'].T:
        total_activity.append(np.sum(frame))
    total_activity = np.array(total_activity)
    spks = active_neurons['cascade_predictions']
# this function returns the left singular vectors scaled by the singular values
    Vsv = TruncatedSVD(n_components = 16).fit_transform(spks.T)

    # compute the other singular vectors
    U = spks @ (Vsv / (Vsv**2).sum(axis=0)**0.5)
    U /= (U**2).sum(axis=0)**0.5
    fig = plt.figure(figsize=(12,6), dpi=200)
    grid = plt.GridSpec(9, 1, figure=fig, hspace = 0.4)


    pc_colors = plt.get_cmap("viridis")(np.linspace(0,0.9,8))
    for j in range(8):
        ax = plt.subplot(grid[j+1])
        ax.plot(Vsv[0:599, j], color=pc_colors[j])
        ax.set_xlim([0, 599-0])
        ax.axis("off")
        ax.set_title(f"PC {j+1}", color=pc_colors[j])