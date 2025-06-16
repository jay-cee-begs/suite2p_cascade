import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import statannotations
import scipy.stats as stats
import os
import matplotlib.cm as cm

"""Example Usage:
comparison_dict = {
    "0 mM HCO3-": {
        '0mM HCO3, 0 L-Cys': "0_0",
        '0mM HCO3, 1x L-Cys': "0_c",
        '0mM HCO3, 1x L-Cys, 1x D-APV': '0_1_APV'
    },
    "26 mM HCO3-": {
        '26mM HCO3, 0 L-Cys': "26_0",
        '26mM HCO3, 1x L-Cys': "26_c",
        '26mM HCO3, 1x L-Cys, 1x D-APV': '26_1_APV'
    }
}
treatment_dict = {
    "0 uM L-Cys": {
        "0mM HCO3": '0_0',
        "26mM HCO3": '26_0'
    },
    "260 uM L-Cys":{
        "0mM HCO3": '0_c',
        "26mM HCO3": '26_c'
    },
    "260 uM L-Cys; 50 uM D-APV":{
        "0mM HCO3": '0_1_APV',
        "26mM HCO3": '26_1_APV'
    }
}
params = ['Active_Neuron_Count', 'Total_Estimated_Spikes','SC_Avg_Instantaneous_Firing_Rate(Hz)','Active_Neuron_F0','Inactive_Neuron_F0']
for param in params:
    plot_comparisons(data_path=r"D:\users\JC\pipeline\001-Cysteine_Toxicity\002-HCO3\pH8_replicates", parameter=param, comparison_dict=comparison_dict)
    plot_comparisons(data_path=r'D:\users\JC\pipeline\001-Cysteine_Toxicity\002-HCO3\pH76_replicates', parameter = param, comparison_dict=treatment_dict)
    """

def toxicity_line_plot(data, parameter, group_dict, title_prefix="", color_map=None, ylim=None, save_path=None):
    import matplotlib.pyplot as plt
    import pandas as pd
    import os

    # Set custom time points and labels
    time_order = ['pre', 't60']
    x_labels = ['pre-imaging', '60min post-treatment']
    data['Time_Point'] = pd.Categorical(data['Time_Point'], categories=time_order, ordered=True)

    plt.figure(figsize=(10, 8))

    for label, group_clean in group_dict.items():
        group_data = data[data['Group_Clean'] == group_clean]
        color = color_map[label] if color_map and label in color_map else None

        # Plot individual wells
        pivot = group_data.pivot_table(index='Well_ID', columns='Time_Point', values=parameter)
        for i, time in enumerate(time_order):
            y = group_data[group_data['Time_Point'] == time][parameter]
            x = np.random.normal(i, 0.05, size=len(y))  # jitter around time index
            plt.scatter(x, y, color=color, alpha=0.5, s=20)

        # Plot mean ± SEM
        stats = group_data.groupby('Time_Point')[parameter].agg(['mean', 'sem']).reset_index()
        plt.errorbar(
            stats['Time_Point'],
            stats['mean'],
            yerr=stats['sem'],
            marker='o',
            linewidth=3,
            capsize=5,
            label=label,
            color=color
        )

    ylabel = parameter.replace('_', ' ').replace('(', '').replace(')', '')
    title = f'Normalized {title_prefix} - {ylabel} Compared to baseline'

    plt.title(title)
    plt.xlabel('Time Point')
    plt.ylabel(ylabel)
    if ylim:
        plt.ylim(ylim)
    plt.xticks(ticks=range(len(time_order)), labels=x_labels)
    plt.grid(True)
    plt.legend(title='Group', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize='small')
    plt.tight_layout()

    # ✅ Save before showing
    if save_path:
        filename = title.replace(" ", "_").replace("/", "_") + '.png'
        # plt.savefig(os.path.join(save_path, filename), dpi=300)
    plt.show()


def plot_comparisons(data_path, parameter, comparison_dict, plot_type = None):

    # Load and process data
    data = pd.read_csv(os.path.join(data_path, 'new_experiment_summary.csv'))
    data['Well_ID'] = data['Prediction_File'].apply(lambda x: x.split('\\')[-1].split('.')[0])
    data['Group_Clean'] = data['Group'].apply(lambda x: '_'.join(x.split('_')[1:]))

    # Flatten all labels and group IDs from all comparisons

    all_labels = []
    all_groups = []
    for comparison in comparison_dict.values():
        all_labels.extend(comparison.keys())
        all_groups.extend(comparison.values())

    # Create global colormap
    cmap = cm.get_cmap('tab20', len(all_labels))
    color_map = {label: cmap(i) for i, label in enumerate(all_labels)}

    # 🧠 Compute global y-limits across all groups
    filtered_data = data[data['Group_Clean'].isin(all_groups)]
    group_means = filtered_data.groupby(['Group_Clean', 'Time_Point'])[parameter].mean()
    min_val = group_means.min()
    max_val = group_means.max()
    padding = (max_val - min_val) * 0.4
    ylim = (min_val - padding, max_val + padding)

    # Plot each comparison using the shared ylim
    if plot_type is not None:
        for comparison_name, group_dict in comparison_dict.items():
            if plot_type is 'line':
                toxicity_line_plot(
                    data,
                    parameter,
                    group_dict,
                    title_prefix=comparison_name,
                    color_map=color_map,
                    ylim=ylim,
                    save_path = data_path
                    )
            
df = pd.read_csv(os.path.join(r'D:\users\JC\pipeline\001-Cysteine_Toxicity\002-HCO3\pH76_replicates\new_experiment_summary.csv'))
params = ['Active_Neuron_Count', 'Total_Estimated_Spikes','SC_Avg_Instantaneous_Firing_Rate(Hz)','Active_Neuron_F0','Inactive_Neuron_F0']

def normalize_parameters(df, params):

    normalized_df = df.copy()
    normalized_df['Well_ID'] = normalized_df['Prediction_File'].apply(lambda x: x.split('\\')[-1].split('.')[0])
    normalized_df['Group_Clean'] = normalized_df['Group'].apply(lambda x: '_'.join(x.split('_')[1:]))
    for param in params:
        normalized_col = f'{param}_normalized'
        pivoted = normalized_df.pivot_table(index = ["Group_Clean", "Well_ID"], columns = "Time_Point", values = param)

        pivoted[normalized_col] = (pivoted['t60'] / pivoted['pre']) * 100

        result = pivoted[[normalized_col]].reset_index()

        normalized_df = normalized_df.merge(result, on=["Group_Clean", "Well_ID"], how = "left")

    return normalized_df
normal_df = normalize_parameters(df, params)
normal_df

def plot_normalized_bar(df, param, group_dict, title = "", save_path = None):
    plt.figure(figsize=(10,6))
    bar_width = 0.6
    all_data = []

    for i, (label, group_clean) in enumerate(group_dict.items()):
        group_data = df[(df["Group_Clean"]==group_clean) & (df["Time_Point"] == 't60')]
        values = group_data[param].dropna()
        all_data.append(values)

    positions = np.arange(len(all_data))
    bar_containers = plt.bar(positions, [data.mean() for data in all_data], 
                             yerr = [data.sem() for data in all_data],
                             tick_label=list(group_dict.keys()),
                             capsize = 8,
                             alpha = 0.8,
                             color = 'skyblue')
    
    plt.axhline(100, color='gray', linestyle='--', linewidth=1)

    # Labels & formatting
    ylabel = param.replace('_', ' ')
    plt.ylabel(f'{ylabel} (% of baseline)')
    plt.title(title or f'{ylabel} Normalized to Baseline')
    plt.xticks(rotation=20)
    plt.grid(axis='y', linestyle=':', alpha=0.7)
    plt.tight_layout()

    # Save if needed
    if save_path:
        filename = title.replace(" ", "_").replace("/", "_") + '.png'
        plt.savefig(os.path.join(save_path, filename), dpi=300)

    plt.show()

parameters = []
for param in params:
    parameters.append(param +"_normalized")
print(parameters)
    
for param in parameters:
    plot_normalized_bar(normal_df, param,  comparison_dict)