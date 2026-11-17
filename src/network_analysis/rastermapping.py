import numpy as np
import matplotlib.pyplot as plt
import os
from scipy.stats import zscore

from run_cascade import functions_data_transformation as fdt, functions_general
from plotting import functions_plots
from batch_gui.config_loader import load_json_config_file

_DEFAULT_CONFIG = load_json_config_file()
config = _DEFAULT_CONFIG

def simple_raster_plot(suite2p_dict, color_map, save_path = None,frame_rate = None, z_score_activity = False, max_neuron_count = None, show_plot = True):
    """
    Create a simple rasterplot of a given suite2p processed file
    Args:
    ----------
        suite2p_dict : dict
            Dictionary containing all Suite2p output files
        color_map : str, matplotlib.colormap
            Color scheme for rasterplot
        save_path : str, default = None
            Folder path telling where to save the rasterplot. It is implemented to defaul to the same folder as the suite2p_dict
        frame_rate : int
            Speed of calcium imaging in frames per second (fps)
        z_score_activity : bool, default = False
            Should activity be normalized by Z-score; default is to show raw activity.
            If activity is low, Z-score should be enabled
        max_neuron_count : int
            Y-limit for the maximum number of neurons to show; if less neurons exist than max, part of the rasterplot will be blank.
        show_plot : bool, default = False
            whether to run plt.show() for the rasterplot
        

    Returns:
    ----------
        if show_plot : run plt.show()
        if save_path : run plt.save(save_path + file_name)
    """
    # Load Cascade activity
    cascade_activity = suite2p_dict["cascade_predictions"]

    # Identify Suite2p-classified cells
    iscell_mask = suite2p_dict["iscell"][:, 0] == 1
    iscell_ids = np.flatnonzero(iscell_mask)
    neuron_ids = iscell_ids.copy()
    # Get neuron IDs from the saved correlation-based classifier
    classifier_path = os.path.join(
        suite2p_dict["data_folder"],
        *fdt.SUITE2P_STRUCTURE["dye_classifier"],
    )
    try:
        dye_classifier = fdt.load_npy_dict(classifier_path)

        neuron_ids = np.asarray(
            dye_classifier["idx_neuro_corr"],
            dtype=int,
        )
        neuron_ids = neuron_ids[iscell_mask[neuron_ids]]
        print("Using dye-classifer ROI classifications")
    except FileNotFoundError:
    # Keep only neurons that are also Suite2p-classified cells
        print("Using iscell ROI classifications")
    # Select neuron activity only
    spks = np.nan_to_num(
        cascade_activity[neuron_ids],
        nan=0.0,
        posinf=0.0,
        neginf=0.0,
    )

    # Total estimated activity now represents neurons only
    total_activity = np.sum(spks, axis=0)

    print(f"Suite2p-classified cells: {len(iscell_ids)}")
    print(f"Neurons plotted: {len(neuron_ids)}")

    if z_score_activity:
        z_spks = zscore(spks, axis=1)
    ops = suite2p_dict['ops']

    #calculate total estimated spikes for ax1
    total_activity = []
    for frame in spks.T:
        total_activity.append(np.sum(frame))
    total_activity = np.array(total_activity)
    
    plt.rcParams['svg.fonttype'] = 'none'
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = 'Arial'
    plt.rcParams['svg.fonttype'] = 'none'
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = 'Arial'
    xmin = 0
    xmax = spks.shape[1]
    if frame_rate is None:
        frame_rate = int(config.general_settings.frame_rate)

    # make figure with grid for easy plotting
    fig = plt.figure(figsize=(16,8), dpi=200)
    grid = plt.GridSpec(10, 40, figure=fig, wspace = 0.1, hspace = 0.4)
    random_spks = np.random.permutation(len(spks))
    
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
    raster = ax2.imshow(spks[random_spks, xmin:xmax], 
                        cmap=color_map, 
                        vmin=0, vmax=1, 
                        aspect="auto")
                        #, interpolation="nearest")
    #LIMIT plot time
    # xmax = 119 * frame_rate  
    # ax1.set_xlim([0, xmax])
    # ax2.set_xlim([0, xmax])
    # ax2.set_ylim([0,165])
    num_ticks = 8
    n_frames = spks.shape[1]
    tick_positions = np.linspace(0, xmax-1, num_ticks, dtype=int)
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
    scatters, nid2idx, nid2idx_rejected, pixel2neuron, nid2idx_neuron, nid2idx_glia = functions_plots.getStats(suite2p_dict, Img.shape, fdt.df_from_suite2p_dict(suite2p_dict, config), config, use_iscell = config.analysis_params.use_suite2p_ROI_classifier)
    #params suite2p_dict, frame_shape, output_df, config, use_iscell = False
    file = suite2p_dict['file_name'].split('\\')[0]
    functions_plots.dispPlot(Img, scatters, nid2idx, nid2idx_rejected, pixel2neuron, nid2idx_neuron, nid2idx_glia,suite2p_dict["F"], suite2p_dict["Fneu"], axs=ax3)
    group = suite2p_dict['Group']
    file = suite2p_dict['data_folder'].split('\\')[-1]
    if save_path is not None:
        
        plt.savefig(os.path.join(save_path, f"{group}_{file}_raster_summary.png"))
        plt.savefig(os.path.join(save_path, f"{group}_{file}_raster_summary.svg"))
    # plt.show()

    if show_plot:
        plt.show()
    plt.close()


def PCA_raster(
    suite2p_dict,
    color_map,
    save_path=None,
    frame_rate=None,
    z_score_activity=False,
    max_neuron_count=None,
    show_plot=True,
):
    """
    Plot Cascade activity for neuron-classified ROIs, ordered by
    Rastermap or, if unavailable, by their first principal component.

    Uses the same arguments as simple_raster_plot().
    """

    import os
    import numpy as np
    import matplotlib.pyplot as plt
    plt.rcParams['svg.fonttype'] = 'none'
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = 'Arial'
    plt.rcParams['svg.fonttype'] = 'none'
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = 'Arial'
    # ---------------------------------------------------------
    # 1. Load activity and select classified neurons
    # ---------------------------------------------------------
    cascade_activity = suite2p_dict["cascade_predictions"]

    iscell_mask = suite2p_dict["iscell"][:, 0] == 1
    iscell_ids = np.flatnonzero(iscell_mask)
    neuron_ids = iscell_ids.copy()

    classifier_path = os.path.join(
        suite2p_dict["data_folder"],
        *fdt.SUITE2P_STRUCTURE["dye_classifier"],
    )
    try:
        dye_classifier = fdt.load_npy_dict(classifier_path)

        neuron_ids = np.asarray(
            dye_classifier["idx_neuro_corr"],
            dtype=int,
        )
        neuron_ids = neuron_ids[iscell_mask[neuron_ids]]
        print("Using dye-classifer ROI classifications")
    except FileNotFoundError:
    # Keep only neurons that are also Suite2p-classified cells
        print("Using iscell ROI classifications")
    # Select neuron activity only
    spks = np.nan_to_num(
        cascade_activity[neuron_ids],
        nan=0.0,
        posinf=0.0,
        neginf=0.0,
    )

    if spks.shape[0] == 0:
        raise ValueError("No neuron-classified ROIs were found.")

    total_activity = np.sum(spks, axis=0)
    xmax = spks.shape[1]

    print(f"Suite2p-classified cells: {len(iscell_ids)}")
    print(f"Neurons selected: {len(neuron_ids)}")

    # ---------------------------------------------------------
    # 2. Optional z-scoring for ordering
    # ---------------------------------------------------------
    # Keep the original activity for plotting; normalize a copy
    # so high-amplitude neurons don't dominate the ordering.
    sort_data = spks.copy()

    if z_score_activity:
        mean = sort_data.mean(axis=1, keepdims=True)
        std = sort_data.std(axis=1, keepdims=True)
        sort_data = (sort_data - mean) / np.maximum(std, 1e-8)

    # ---------------------------------------------------------
    # 3. Compute neuron ordering
    # ---------------------------------------------------------
    try:
        from rastermap import Rastermap

        n_neurons = sort_data.shape[0]
        n_timepoints = sort_data.shape[1]

        model = Rastermap(
            n_PCs=max(1, min(200, n_neurons, n_timepoints)),
            n_clusters=max(1, min(100, n_neurons)),
            locality=0.0,
            time_lag_window=0,
            verbose=False,
        ).fit(sort_data)

        # isort contains row indices into sort_data/spks
        sort_idx = np.asarray(model.isort, dtype=int)
        sort_method = "Rastermap"

    except (ImportError, ValueError, RuntimeError) as exc:
        print(f"Rastermap unavailable or failed ({exc}); using PCA.")

        from sklearn.decomposition import PCA

        # Center each timepoint across neurons before PCA.
        # PCA expects observations x features, here neurons x time.
        pca_data = sort_data - sort_data.mean(axis=0, keepdims=True)

        if pca_data.shape[0] < 2 or not np.any(pca_data):
            sort_idx = np.arange(len(sort_data))
        else:
            n_components = min(
                1,
                pca_data.shape[0],
                pca_data.shape[1],
            )
            scores = PCA(
                n_components=n_components
            ).fit_transform(pca_data)[:, 0]

            sort_idx = np.argsort(scores)

        sort_method = "PCA"

    # Apply the same order to activity and ROI IDs
    spks = spks[sort_idx]
    neuron_ids = neuron_ids[sort_idx]

    # ---------------------------------------------------------
    # 4. Respect optional neuron limit
    # ---------------------------------------------------------
    if max_neuron_count is not None:
        n_plot = max(0, int(max_neuron_count))
        spks = spks[:n_plot]
        neuron_ids = neuron_ids[:n_plot]

    if len(spks) == 0:
        raise ValueError("No neurons remain to plot.")

    # ---------------------------------------------------------
    # 5. Raster plot
    # ---------------------------------------------------------

    # ---------------------------------------------------------
    # 5. Plot total Cascade activity above the raster
    # ---------------------------------------------------------
    fig, (ax_total, ax_raster) = plt.subplots(
        2,
        1,
        figsize=(12, 8),
        sharex=True,
        gridspec_kw={
            "height_ratios": [1, 4],
            "hspace": 0.08,
        },
    )

    # Time axis
    if frame_rate is not None and frame_rate > 0:
        time_axis = np.arange(spks.shape[1]) / frame_rate
        x_label = "Time (s)"
    else:
        time_axis = np.arange(spks.shape[1])
        x_label = "Frame"

    # Top panel: sum of Cascade predictions
    ax_total.plot(
        time_axis,
        total_activity,
        color="black",
        linewidth=1,
    )
    ax_total.set_ylabel("Total activity")
    ax_total.set_title(
        f"Population activity and neuron raster ({sort_method})"
    )
    ax_total.xaxis.set_visible(False)
    ax_total.spines['top'].set_visible(False)
    ax_total.spines['right'].set_visible(False)
    ax_total.spines['bottom'].set_visible(False)
    # Bottom panel: ordered neuron raster
    ax_raster.imshow(
        spks,
        aspect="auto",
        interpolation="nearest",
        cmap=color_map,
        extent=[
            time_axis[0] if len(time_axis) else 0,
            time_axis[-1] if len(time_axis) else 0,
            len(spks),
            0,
        ],
    )

    ax_raster.set_ylabel("Neuron rank")
    ax_raster.set_xlabel(x_label)

    # Keep both panels aligned
    if len(time_axis) > 1:
        ax_raster.set_xlim(time_axis[0], time_axis[-1])

    # ---------------------------------------------------------
    # 6. Save and display
    # ---------------------------------------------------------
    fig.tight_layout()

    if save_path is not None:
        fig.savefig(os.path.join(save_path, f'{os.path.basename(suite2p_dict["data_folder"])}_PCA_raster_summary.svg'), bbox_inches="tight", dpi=300)
        fig.savefig(os.path.join(save_path, f'{os.path.basename(suite2p_dict["data_folder"])}_PCA_raster_summary.png'), bbox_inches="tight", dpi=300)

    if show_plot:
        plt.show()
    else:
        plt.close(fig)

    return {
        "neuron_ids": neuron_ids,
        "activity": spks,
        "total_activity": total_activity,
        "sort_idx": sort_idx,
        "sort_method": sort_method,
        "figure": fig,
        "time_axis": time_axis,
    }



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
                           z_score_activity=True, show_plot=False)

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
    