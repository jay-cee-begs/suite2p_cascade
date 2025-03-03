import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import leidenalg as la
import seaborn as sns
import igraph as ig
import networkx as nx
from run_cascade import functions_data_transformation as transform
from plotting import functions_plots
from batch_process.config_loader import load_json_config_file, load_json_dict

config = load_json_config_file()
from networkx.algorithms.community import greedy_modularity_communities, louvain_communities

def load_for_networkx(data_folder):  ## creates a dictionary for the suite2p paths in the given data folder (e.g.: folder for well_x)
    """
    Creates a dictionary for networkx analysis from the SUITE2P_STRUCTURE in the data folder.
    """    
    stat = transform.load_npy_array(os.path.join(data_folder, *transform.SUITE2P_STRUCTURE["stat"]))
    cascade_predictions = transform.load_npy_array(os.path.join(data_folder, *transform.SUITE2P_STRUCTURE["cascade_predictions"]))
    deltaF = transform.load_npy_array(os.path.join(data_folder, *transform.SUITE2P_STRUCTURE['deltaF']))
    iscell = transform.load_npy_array(os.path.join(data_folder, *transform.SUITE2P_STRUCTURE['iscell']))[:,0].astype(bool)
    filtered_spike_predictions = np.nan_to_num(cascade_predictions[iscell])
    filtered_dF = deltaF[iscell]

    neuron_data = {}

    for idx, neuron_stat in enumerate(stat):
        #assign location for each ROI; attach cascade predictions to each for spike analysis at end
        x_median = np.median(neuron_stat['xpix'])
        y_median = np.median(neuron_stat['ypix'])
        predicted_spikes = np.nan_to_num(cascade_predictions[idx,:])
        deltaF = deltaF

        neuron_data[f"neuron_{idx}"] = {
            "x": x_median,
            "y": y_median,
            "predicted_spikes": predicted_spikes,
            "deltaF": np.array(deltaF),
            "IsUsed": iscell[idx],
        }
        #create a new dict for filtering by Iscell values (from previous experiments)
    filtered_neuron_data = {}

    for key, value in neuron_data.items():
        if value["IsUsed"]:
            filtered_neuron_data[key] = value
    
    return  filtered_neuron_data, filtered_spike_predictions, filtered_dF

def create_template_matrix(neuron_data):
    num_neurons = len(neuron_data)
    temp_matrix = np.random.rand(num_neurons, num_neurons)
    temp_matrix[temp_matrix<0.9] = 0
    np.fill_diagonal(temp_matrix, 0)
    G = nx.from_numpy_array(temp_matrix)
    mapping = {i: neuron_id for i, neuron_id in enumerate(neuron_data.keys())} #rename index from neuron_0... for networkx
    G = nx.relabel_nodes(G, mapping)
    return G

def build_spike_communities(data_folder, neuron_data, deltaF, threshold = 0.5):
    node_graph = create_template_matrix(neuron_data)
    neuron_ids = list(neuron_data.keys())
    sample_name = os.path.basename(data_folder)
    for neuron_id, data in neuron_data.items():
        node_graph.add_node(neuron_id, pos=(data['x'],data['y']))
    
    pos = {node: (neuron_data[node]["x"], neuron_data[node]["y"]) for node in node_graph.nodes}

    nx.set_node_attributes(node_graph, pos, "pos")
    
    correlation_matrix = np.corrcoef(deltaF)
    np.fill_diagonal(correlation_matrix, 0)
    #Plot Histogram of neuron-to-neuron deltaF correlations
    plt.hist(correlation_matrix.flatten(), bins = 50, color = 'skyblue')
    plt.xlabel("Correlation")
    plt.ylabel("Frequency")
    plt.show()

    for i, neuron_1 in enumerate(neuron_ids):
        for j, neuron_2 in enumerate(neuron_ids):
            if i<j:
                correlation = correlation_matrix[i,j]
                if abs(correlation) > threshold:
                       node_graph.add_edge(neuron_1, neuron_2, weight = correlation)
    
    # Step 3: Convert to a format compatible with Leiden
    ig_graph = ig.Graph.TupleList(node_graph.edges(data=True), directed=False, weights="weight")
    # Step 4: Apply Leiden method
    partition = la.find_partition(ig_graph, la.ModularityVertexPartition)#la.RBConfigurationVertexPartition, resolution_parameter=1.0)
    # Convert partition to a list of communities
    neuron_communities = [list(ig_graph.vs[community]['name']) for community in partition]

    # return graph, communities, correlation_matrix            
    community_map = {
        node: community_idx
        for community_idx, community in enumerate(neuron_communities)
        for node in community
    }
    communities = list(range(len(neuron_communities)))
    community_spikes = {
        community: np.zeros_like(next(iter(neuron_data.values()))['predicted_spikes'])
        for community in communities
    }
    for node, community_idx in community_map.items():
        community_spikes[community_idx] += np.nan_to_num(neuron_data[node]['predicted_spikes'])
    
        # Node statistics
    node_degree_dict = dict(node_graph.degree)
    clustering_coeff_dict = nx.clustering(node_graph)
    betweenness_centrality_dict = nx.betweenness_centrality(node_graph)
    try:
        eigenvector_centrality_dict = nx.eigenvector_centrality(node_graph)
    except nx.PowerIterationFailedConvergence:
        eigenvector_centrality_dict = {node: None for node in node_graph.nodes}
    
    # # Edge Statistics
    # edge_data = []
    # for (u, v, data) in node_graph.edges(data=True):
    #     edge_data.append({
    #         'source': u,
    #         "target": v,
    #         'weight': data.get("weight", 1),
    #     })
    
    community_sizes = {community_idx: len(community) for community_idx, community in enumerate(neuron_communities)}
    raw_data = []
    for node, neuron in zip(node_graph.nodes, neuron_data):
        raw_data.append({
            "neuron_id": node,
            "x": neuron_data[node]["x"],
            "y": neuron_data[node]["y"],
            "community": community_map[node],
            "community_size": community_sizes[community_map[node]],
            "degree": node_degree_dict[node],
            "clustering_coefficient": clustering_coeff_dict[node],
            "betweenness_centrality": betweenness_centrality_dict[node],
            "eigenvector_centrality": eigenvector_centrality_dict[node],
            "total_predicted_spikes": np.nansum(neuron_data[neuron]['predicted_spikes']),
            "avg_predicted_spikes": np.nanmean(neuron_data[neuron]['predicted_spikes'])
        })
    df_nodes = pd.DataFrame(raw_data)
    # df_nodes["community_spikes"]
    df_nodes.to_csv(os.path.join(data_folder, f"{sample_name}_graph_node_data.csv"), index=False)
    
    return node_graph, neuron_communities, neuron_data, community_spikes

def extract_and_plot_neuron_connections(node_graph, neuron_data, neuron_communities, community_spikes, data_folder, ops):
    # Prepare image
    sample_name = os.path.basename(data_folder)
    mimg = functions_plots.getImg(ops)
    fig = plt.figure(figsize=(20, 20), dpi=200)
    grid = plt.GridSpec(10, 40, figure=fig, wspace = 0.1, hspace = 0.4)
    

    # plot NetworkX Graph
    ax1 = fig.add_subplot(grid[0:8, 0:40])
    #Display Suite2p image base
    ax1.imshow(mimg, cmap='gray', interpolation='nearest')
    ax1.set_title(f"Sample: {sample_name} - Overlayed Communities", fontsize=24)
    ax1 = plt.gca()
 
    neuron_communities_dict = {
        node: community_idx
        for community_idx, community in enumerate(neuron_communities)
        for node in community
}
    # Overlay graph on the image
    community_colors = [neuron_communities_dict[node] for node in node_graph.nodes]
    unique_clubs = len(set(community_colors))
    pos = nx.get_node_attributes(node_graph, 'pos')

    nx.draw(
        node_graph,
        pos=pos,
        node_size=25,
        node_color=community_colors,
        edge_color = (1,1,1,0), #make edges transparent
        cmap=plt.cm.tab10,  # Use a colormap with distinct colors
        ax = ax1
    )
    ax1.set_title(f"Community Detection with {unique_clubs} Communities (Corrected Positions)", fontsize = 24)
    ax1.set_xlabel(f"Sample: {sample_name}", fontsize = 18)

    #TODO implement way to show bar plot of networkX total estimated spikes
    # plt.savefig(os.path.join(data_folder, f"{sample_name}_networkx_connections.png"))
    # plt.close()
    # plt.figure(figsize=(10,6))
    # communities = list(community_spikes.keys())
    # total_spikes = list(community_spikes.values())
    # bar_colors = [plt.cm.tab10(i / len(communities)) for i in communities]
    # plt.bar(communities, total_spikes, color=bar_colors)
    # plt.xlabel('Community', fontsize=14)
    # plt.ylabel('Total Predicted Spikes', fontsize=14)
    # plt.title(f"Total Predicted Spikes per Community - {sample_name}", fontsize=16)
    # plt.xticks(communities)
    # plt.tight_layout()
    # # plt.savefig(os.path.join(data_folder, f"{sample_name}_total_spikes_per_community.png"))
    # plt.close()

    # plt.figure(figsize=(12, 8))
    #TODO need to find a way to put ylabel in the center of the figure
    max_spike = max([spikes.max() for spikes in community_spikes.values()])
    num_communities = len(community_spikes)

    ax2 = fig.add_subplot(grid[8:, 0:40])
    for idx, (community, spikes) in enumerate(community_spikes.items()):
        # ax2 = plt.subplot(num_communities, 1, idx+1)
        ax2.plot(spikes, label = f'{community}')
        ax2.legend(loc = 'upper right', fontsize = 10)

        # if idx == 1:
        #    ax.set_ylabel("Spikes", fontsize = 12)
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        ax2.spines['bottom'].set_visible(False if idx < num_communities -1 else True)

        if idx < num_communities - 1:
            ax2.tick_params(axis='x', which = 'both', bottom = False, labelbottom = False)

        if idx == num_communities - 1:
            ax2.set_xlabel("Frame", fontsize = 14)   
    # plt.xlabel('Frame', fontsize=14)
        ax2.set_ylim(-0.1,max_spike)
        ax2.set_xlabel("Frame", fontsize = 14)
        ax2.set_ylabel("Spikes", fontsize = 14)
        ax2.set_title("Total Estimated Spikes per Frame")
    plt.show()
    # plt.title(f"Total Predicted Spikes per Community (Line Plot) - {sample_name}", fontsize=16)
    # plt.legend()
    # plt.grid(True)
    # plt.tight_layout()
    # plt.show()

def calculate_synchrony(neuron_data, node_graph):

    synchrony_scores = {}

    for u, v in node_graph.edges():
            spikes_u = neuron_data[u]['predicted_spikes']
            spikes_v = neuron_data[v]['predicted_spikes']
            
            # Create a mask to filter out NaN values
            mask = ~np.isnan(spikes_u) & ~np.isnan(spikes_v)

            if np.sum(mask) > 1:  # Ensure there are enough data points
                # Calculate the correlation coefficient
                correlation_matrix = np.corrcoef(spikes_u[mask], spikes_v[mask])
                correlation = correlation_matrix[0, 1]  # Get the correlation between u and v
            else:
                correlation = np.nan  # Not enough data to compute correlation

            synchrony_scores[(u, v)] = correlation  # Store the synchrony score

    return synchrony_scores

def plot_synchrony_heatmap(synchrony_scores):
    # Convert the synchrony scores dictionary to a DataFrame
    neuron_pairs = list(synchrony_scores.keys())
    
    # Extract unique neuron names
    neurons = sorted(set([neuron for pair in neuron_pairs for neuron in pair]))
    neuron_id = []
    for neuron in neurons:
        neuron_id.append(neuron.split('_')[1])
    # Create a DataFrame for the heatmap
    heatmap_data = pd.DataFrame(np.nan, index=neuron_id, columns=neuron_id)
    # heatmap_data.index = [neuron.split('_')[1] for neuron in heatmap_data.index]
    # heatmap_data.columns = [neuron.split('_')[1] for neuron in heatmap_data.columns]
    
    for (neuron1, neuron2), score in synchrony_scores.items():
        heatmap_data.at[neuron1, neuron2] = score
        heatmap_data.at[neuron2, neuron1] = score  # Symmetric matrix

    # Plotting the heatmap
    plt.figure(figsize=(12, 10))
    sns.heatmap(heatmap_data, annot=True, fmt=".2f", cmap='coolwarm', center=0, cbar_kws={"shrink": .8})
    plt.title('Neuron Synchrony Scores Heatmap')
    plt.xlabel('Neurons')
    plt.ylabel('Neurons')
    plt.tight_layout
    plt.show()


def plot_neuron_connections(data_folder):
    print('extracting neuron data for network x')
    neuron_data, spike_data, deltaF = load_for_networkx(data_folder)
    print("creating networkx node graph")
    node_graph, neuron_communities, neuron_data, community_spikes = build_spike_communities(data_folder, neuron_data, deltaF, threshold = 0.3)
    ops = transform.load_npy_array(os.path.join(data_folder, *transform.SUITE2P_STRUCTURE["ops"])).item()
    extract_and_plot_neuron_connections(node_graph, neuron_data, neuron_communities, community_spikes, data_folder, ops)
    synchrony = calculate_synchrony(neuron_data, node_graph)
    plot_synchrony_heatmap(synchrony)
def main():
    for sample in transform.get_file_name_list(config.general_settings.main_folder, file_ending = 'samples', supress_printing=False):
        print(f"Processing {sample}")
        plot_neuron_connections(sample)
        print('Finished processing')

if __name__ == '__main__':
    main()
