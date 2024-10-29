import tkinter as tk
from tkinter import messagebox, filedialog
import os
import subprocess

class ConfigEditor:
    def __init__(self, master):
        # Load existing configurations
        self.master = master
        self.master.title("Ultimate Suite2P + Cascade Pipeline GUI")
        self.master.geometry("700x900")  # Set initial window size

        # Create a canvas and a scrollbar
        self.canvas = tk.Canvas(master)
        self.scrollbar = tk.Scrollbar(master, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        # Configure the scrollbar
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        # Link the scrollbar to the canvas
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Pack the canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Load existing configurations
        self.config = self.load_config("gui_configurations.py")

        self.main_folder_var = tk.StringVar(value=self.config.get('main_folder', ''))
        self.data_extension_var = tk.StringVar(value=self.config.get('data_extension', ''))
        self.frame_rate_var = tk.IntVar(value=self.config.get('frame_rate', 0))
        self.ops_path_var = tk.StringVar(value=self.config.get('ops_path', ''))
        self.groups = self.config.get('groups', [])
        self.groups22 = {key: value for key, value in self.config.get('Groups22', {}).items()}

        # Main folder input
        tk.Label(self.scrollable_frame, text="Experiment / Main Folder Path:").pack(anchor='w', padx=10, pady=5)
        tk.Entry(self.scrollable_frame, textvariable=self.main_folder_var, width=50).pack(padx=10)

        # Button to open file explorer for selecting a folder
        tk.Button(self.scrollable_frame, text="Browse", command=self.browse_folder).pack(padx=10, pady=5)

        # Group input
        self.group_frame = tk.Frame(self.scrollable_frame)
        self.group_frame.pack(padx=10, pady=5)
        tk.Label(self.group_frame, text="Adds all subfolders from the Experiment:").pack(side=tk.LEFT)
        tk.Button(self.group_frame, text="Add Group", command=self.add_group).pack(side=tk.LEFT)

        # Data extension input
        tk.Label(self.scrollable_frame, text="Data Extension:").pack(anchor='w', padx=10, pady=5)
        tk.Entry(self.scrollable_frame, textvariable=self.data_extension_var).pack(padx=10)

        # Frame rate input
        tk.Label(self.scrollable_frame, text="Frame Rate:").pack(anchor='w', padx=10, pady=5)
        tk.Entry(self.scrollable_frame, textvariable=self.frame_rate_var).pack(padx=10)

        # Ops path input
        tk.Label(self.scrollable_frame, text="Select Ops Path:").pack(anchor='w', padx=10, pady=5)
        tk.Entry(self.scrollable_frame, textvariable=self.ops_path_var, width=50).pack(padx=10)

        # Option to skip Suite2P
        self.skip_suite2p_var = tk.BooleanVar()
        tk.Checkbutton(self.scrollable_frame, text="Skip Suite2P", variable=self.skip_suite2p_var).pack(anchor='w', padx=10, pady=5)

        # Buttons for Suite2P options
        tk.Button(self.scrollable_frame, text="Proceed", command=self.proceed).pack(pady=10)

        # Editable Groups22
        self.groups22_frame = tk.Frame(self.scrollable_frame)
        self.groups22_frame.pack(padx=10, pady=5)
        self.create_dict_entries(self.scrollable_frame, "Groups22", self.groups22)

        # Save button
        tk.Button(self.scrollable_frame, text="Save Configurations", command=self.save_config).pack(pady=10)

        # Initialize empty TimePoints dictionary
        self.timepoints = {}

    def browse_folder(self):
        """Open a file dialog to select a folder and set the main folder path."""
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.main_folder_var.set(folder_selected)

    def load_config(self, filepath):
        """Load configurations from a file."""
        config = {}
        try:
            with open(filepath) as f:
                exec(f.read(), config)
        except FileNotFoundError:
            messagebox.showerror("Error", "Configuration file not found. Starting with default settings.")
            return {}
        return config

    def add_group(self):
        """Add all subfolders in the main folder, excluding certain names."""
        main_folder = self.main_folder_var.get().strip()  # Get the main folder path from the input

        if not os.path.exists(main_folder):
            messagebox.showerror("Error", "Main folder does not exist.")
            return

        # List all directories in the main folder
        all_folders = [f for f in os.listdir(main_folder) if os.path.isdir(os.path.join(main_folder, f))]

        # Filter out folders with specific substrings
        excluded_substrings = ['csv_files', 'pkl_files', 'csv_files_deltaF']
        unique_folders = [folder for folder in all_folders if not any(excluded in folder for excluded in excluded_substrings)]

        for folder_name in unique_folders:
            group_path = f"\\{folder_name}" if not folder_name.startswith("\\") else folder_name
            
            # Add to Groups22 if not already present
            if folder_name not in self.groups22:
                self.groups22[folder_name] = ''
            
            # Prevent duplicates in groups
            if group_path not in self.groups:
                self.groups.append(group_path)

        self.update_groups22_entries()
        messagebox.showinfo("Groups Added", f"Added Groups: {', '.join(unique_folders)}")

    def proceed(self):
        """Proceed based on whether to skip Suite2P or not."""
        if self.skip_suite2p_var.get():
            self.skip_suite2p_flow()
        else:
            self.suite2p_flow()

    def skip_suite2p_flow(self):
        """Handle the flow when Suite2P is skipped."""
        # Prompt for TimePoints, Group22 values, and parameters
        self.prompt_timepoints()
        self.run_batch_file("run_plots.bat")

    def suite2p_flow(self):
        """Handle the flow when Suite2P is not skipped."""
        # Adjust data extension and frame rate
        data_extension = self.data_extension_var.get()
        frame_rate = self.frame_rate_var.get()
        
        if not data_extension or not frame_rate:
            messagebox.showwarning("Input Error", "Please specify both Data Extension and Frame Rate.")
            return

        # Options for ops file
        ops_options_frame = tk.Toplevel(self.master)
        ops_options_frame.title("Ops File Options")

        tk.Label(ops_options_frame, text="Select Ops File Option:").pack(pady=5)

        tk.Button(ops_options_frame, text="Insert Filepath", command=self.insert_ops_filepath).pack(pady=5)
        tk.Button(ops_options_frame, text="Run Default Ops Suite2P", command=self.default_ops_suite2p).pack(pady=5)
        tk.Button(ops_options_frame, text="Run Suite2P GUI", command=self.run_suite2p).pack(pady=5)

    def insert_ops_filepath(self):
        """Handle file path insertion for ops file."""
        filepath = filedialog.askopenfilename(title="Select Ops File")
        if filepath:
            self.ops_path_var.set(filepath)
            self.run_batch_file("run_s2p_cascade.bat")
            self.prompt_timepoints()
            self.run_batch_file("run_plots.bat")

    def default_ops_suite2p(self):
        """Run the default_ops_suite2p function (stub)."""
        # Assuming this is defined elsewhere in your code
        # default_ops_suite2p()  
        self.run_batch_file("run_s2p_cascade.bat")
        self.prompt_timepoints()
        self.run_batch_file("run_plots.bat")

    def run_suite2p(self):
        """Open the Suite2P GUI (stub)."""
        # Assuming this is defined elsewhere in your code
        # run_suite2p()
        self.run_batch_file("run_s2p_cascade.bat")
        self.prompt_timepoints()
        self.run_batch_file("run_plots.bat")

    def prompt_timepoints(self):
        """Prompt the user to change TimePoints and Group22 values."""
        # Implement your prompt for TimePoints and Group22 values here
        # You can use simple entry dialogs or extend the GUI
        messagebox.showinfo("TimePoints and Group22", "Please change the TimePoints and Group22 values as needed.")

    def run_batch_file(self, filename):
        """Run a specified batch file."""
        try:
            subprocess.run([filename], check=True)
            print(f"{filename} executed successfully.")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"An error occurred while running {filename}: {e}")

    def create_dict_entries(self, master, title, dictionary):
        tk.Label(master, text=title).pack(anchor='w', padx=10, pady=5)
        self.dict_vars = {}
        for key, value in dictionary.items():
            frame = tk.Frame(master)
            frame.pack(padx=10, pady=5)
            tk.Label(frame, text="Key:").pack(side=tk.LEFT)
            key_var = tk.StringVar(value=key)
            value_var = tk.StringVar(value=value)
            self.dict_vars[key] = (key_var, value_var)
            tk.Entry(frame, textvariable=key_var, width=15).pack(side=tk.LEFT)
            tk.Label(frame, text="Value:").pack(side=tk.LEFT)
            tk.Entry(frame, textvariable=value_var, width=15).pack(side=tk.LEFT)

    def update_groups22_entries(self):
        for widget in self.groups22_frame.winfo_children():
            widget.destroy()  # Remove old entries
        self.create_dict_entries(self.groups22_frame, "Groups22", self.groups22)

    def save_config(self):
        main_folder = self.main_folder_var.get().strip()
        data_extension = self.data_extension_var.get().strip()
        frame_rate = self.frame_rate_var.get()
        ops_path = self.ops_path_var.get().strip()

        # Ensure the main folder exists
        if not os.path.exists(main_folder):
            messagebox.showerror("Error", "Main folder does not exist.")
            return

        # Prepare TimePoints and Groups22
        groups22 = {key_var.get(): value_var.get() for key_var, (key_var, value_var) in self.dict_vars.items()}

        # Get pairs from user input
        pairs_input = self.pairs_var.get().strip()

        # Write configurations back to the file
        with open('gui_configurations.py', 'w') as f:
            f.write(f"main_folder = r'{main_folder}'\n")
            for i, group in enumerate(self.groups, start=1):
                f.write(f"group{i} = main_folder + r'{group}'\n")
            f.write(f"group_number = {len(self.groups)}\n")
            f.write(f"data_extension = '{data_extension}'\n")
            f.write(f"frame_rate = {frame_rate}\n")
            f.write(f"ops_path = r'{ops_path}'\n")
            
            # Write TimePoints
            f.write("TimePoints = {\n")
            for key, value in self.timepoints.items():
                f.write(f"    '{key}': '{value}',\n")
            f.write("}\n")

            # Write Groups22
            f.write("Groups22 = {\n")
            for key, (key_var, value_var) in self.dict_vars.items():
                f.write(f"    '{key_var.get()}': '{value_var.get()}',\n")
            f.write("}\n")

            # Write pairs as a single string
            f.write(f"pairs = [ {pairs_input} ]\n")

            # Write parameters, including testby with pairs
            f.write("parameters = {\n")
            f.write(f"    'testby': pairs,\n")  # Set 'testby' to the string 'pairs'
            for key, var in self.parameters_vars.items():
                if key != 'testby':  # Exclude 'testby' from user input
                    f.write(f"    '{key}': '{var.get()}',\n")
            f.write("}\n")

            # Append the new block of code
            f.write("## plot a set of nb_neurons randomly chosen neuronal traces (first seconds)\n")
            f.write("nb_neurons = 16 ## maybe put directly into cascade_this???\n\n")
            f.write('model_name = "Global_EXC_10Hz_smoothing200ms"\n')
            f.write('## select fitting model from list (created in cascada code) ##\n')
            f.write('## list still in CASCADE code, maybe add here##\n\n')
            f.write("EXPERIMENT_DURATION = 60\n")
            f.write("FRAME_INTERVAL = 1 / frame_rate\n")
            f.write("BIN_WIDTH = 20  # SET TO APPROX 200ms\n")
            f.write("FILTER_NEURONS = True\n\n")
            f.write("groups = []\n")
            f.write("for n in range(group_number):\n")
            f.write("    group_name = f\"group{n+1}\"\n")
            f.write("    if group_name in locals():\n")
            f.write("        groups.append(locals()[group_name])\n\n")

            messagebox.showinfo("Success", "Configurations saved successfully.")


if __name__ == "__main__":
    root = tk.Tk()
    app = ConfigEditor(root)
    root.mainloop()
