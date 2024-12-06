import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
from run_cascade import functions_data_transformation as transform
from batch_process import gui_configurations as configurations



from run_cascade import functions_data_transformation as transform
import numpy as np
import matplotlib.pyplot as plt
import os
import pandas as pd
import networkx as nx
from networkx.algorithms.community import greedy_modularity_communities
import multiprocessing

def load_for_networkx(data_folder):  ## creates a dictionary for the suite2p paths in the given data folder (e.g.: folder for well_x)
    """here we define our dictionary for networkx analysis from the SUITE2P_STRUCTURE...see above"""
    stat = transform.load_npy_array(os.path.join(data_folder, *transform.SUITE2P_STRUCTURE["stat"]))
    cascade_predictions = transform.load_npy_array(os.path.join(data_folder, *transform.SUITE2P_STRUCTURE["cascade_predictions"]))
    iscell = transform.load_npy_array(os.path.join(data_folder, *transform.SUITE2P_STRUCTURE['iscell']))[:,0].astype(bool)
    neuron_data = {}
    for idx, neuron_stat in enumerate(stat):
        x_median = np.median(neuron_stat['xpix'])
        y_median = np.median(neuron_stat['ypix'])
        predicted_spikes = cascade_predictions[idx,:]

        neuron_data[f"neuron_{idx}"] = {
            "x": x_median,
            "y": y_median,
            "predicted_spikes": predicted_spikes,
            "IsUsed": iscell[idx]
        }
    filtered_neuron_data = {}

    for key, value in neuron_data.items():
        if value["IsUsed"]:
            filtered_neuron_data[key] = value
    
    return  filtered_neuron_data

def create_template_matrix(neuron_data):
    num_neurons = len(neuron_data)
    temp_matrix = np.random.rand(num_neurons, num_neurons)
    temp_matrix[temp_matrix<0.9] = 0
    np.fill_diagonal(temp_matrix, 0)
    G = nx.from_numpy_array(temp_matrix)
    mapping = {i: neuron_id for i, neuron_id in enumerate(neuron_data.keys())} #rename index from neuron_0... for networkx
    G = nx.relabel_nodes(G, mapping)
    return G
def plot_neuron_connections(data_folder):
    neuron_data = load_for_networkx(data_folder)
    node_graph = create_template_matrix(neuron_data)
    for neuron_id, data in neuron_data.items():
        node_graph.add_node(neuron_id, pos=(data['x'], data['y'])) 
    pos = nx.get_node_attributes(node_graph, 'pos')
    neuron_clubs = list(greedy_modularity_communities(node_graph))

    community_map = {
        node:community_idx
        for community_idx, community in enumerate(neuron_clubs)
        for node in community
    }
    community_colors = [community_map[node] for node in node_graph.nodes]
    unique_clubs = len(set(community_colors))
    nx.draw(
        node_graph,
        pos=pos,
        with_labels=False,
        node_size=100,
        node_color=community_colors,
        cmap=plt.cm.tab10,  # Use a colormap with distinct colors
    )
    plt.title(f"Community Detection with {unique_clubs} Communities (Corrected Positions)")
    plt.show()
    
if __name__ == '__main__':
    for sample in transform.load_suite2p_paths(configurations.main_folder):
        plot_neuron_connections(sample)