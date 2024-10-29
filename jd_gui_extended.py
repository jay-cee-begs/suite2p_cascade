import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
import os
import subprocess

class ConfigEditor:
    def __init__(self, master):
        self.master = master
        self.master.title("GUI Configurations Editor")
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
        tk.Label(self.scrollable_frame, text="Ops Path Options:").pack(anchor='w', padx=10, pady=5)
        #tk.Entry(self.scrollable_frame, textvariable=self.ops_path_var, width=50).pack(padx=10)
        
        # Option a: Insert file path
        ops_frame = tk.Frame(self.scrollable_frame)
        ops_frame.pack(padx=10, pady=5)
        tk.Entry(ops_frame, textvariable=self.ops_path_var, width=40).pack(side=tk.LEFT)
        tk.Button(ops_frame, text="Browse", command=self.browse_ops_file).pack(side=tk.LEFT)

        # Option b: Edit default ops
        tk.Button(self.scrollable_frame, text="Edit Default Ops", command=self.edit_default_ops).pack(pady=5)

        # Option c: Create new ops file
        tk.Button(self.scrollable_frame, text="Create New Ops File", command=self.create_new_ops_file).pack(pady=5)
        
        # TimePoints input
        self.timepoint_frame = tk.Frame(self.scrollable_frame)
        self.timepoint_frame.pack(padx=10, pady=5)
        tk.Label(self.scrollable_frame, text="In case you need to rename your Baseconditions:").pack(anchor='w')
        self.timepoint_key_var = tk.StringVar()
        self.timepoint_value_var = tk.StringVar()
        tk.Entry(self.timepoint_frame, textvariable=self.timepoint_key_var, width=20).pack(side=tk.LEFT)
        tk.Entry(self.timepoint_frame, textvariable=self.timepoint_value_var, width=20).pack(side=tk.LEFT)
        tk.Button(self.scrollable_frame, text="Add TimePoint", command=self.add_timepoint).pack(padx=10)

        # Editable Groups22
        self.groups22_frame = tk.Frame(self.scrollable_frame)
        self.groups22_frame.pack(padx=10, pady=5)
        self.create_dict_entries(self.groups22_frame, "Groups22", self.groups22)

        # Editable parameters
        self.parameters_frame = tk.Frame(self.scrollable_frame)
        self.parameters_frame.pack(padx=10, pady=5)
        self.create_parameters_entries()

        # Save button
        tk.Button(self.scrollable_frame, text="Save Configurations", command=self.save_config).pack(pady=10)

        # Skip Suite2P option
        self.skip_suite2p_var = tk.BooleanVar()
        tk.Checkbutton(self.scrollable_frame, text="Skip Suite2P", variable=self.skip_suite2p_var).pack(anchor='w', padx=10, pady=5)

        # Processing button
        tk.Button(self.scrollable_frame, text="Process", command=self.proceed).pack(pady=10)

        # Initialize empty TimePoints dictionary
        self.timepoints = {}
    
    def edit_default_ops(self):
        # Call the function to edit default ops
        default_ops_suite2p()

    def create_new_ops_file(self):
        # Call the function to create new ops file
        run_suite2p()

    def browse_ops_file(self):
        file_selected = filedialog.askopenfilename(filetypes=[("Ops Files", "*.ops")])
        if file_selected:
            self.ops_path_var.set(file_selected)

    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.main_folder_var.set(folder_selected)

    def load_config(self, filepath):
        config = {}
        try:
            with open(filepath) as f:
                exec(f.read(), config)
        except FileNotFoundError:
            messagebox.showerror("Error", "Configuration file not found. Starting with default settings.")
            return {}
        return config

    def add_group(self):
        main_folder = self.main_folder_var.get().strip()
        if not os.path.exists(main_folder):
            messagebox.showerror("Error", "Main folder does not exist.")
            return

        all_folders = [f for f in os.listdir(main_folder) if os.path.isdir(os.path.join(main_folder, f))]
        excluded_substrings = ['csv_files', 'pkl_files', 'csv_files_deltaF']
        unique_folders = [folder for folder in all_folders if not any(excluded in folder for excluded in excluded_substrings)]

        for folder_name in unique_folders:
            group_path = f"\\{folder_name}" if not folder_name.startswith("\\") else folder_name
            
            if folder_name not in self.groups22:
                self.groups22[folder_name] = ''
            
            if group_path not in self.groups:
                self.groups.append(group_path)

        self.update_groups22_entries()
        messagebox.showinfo("Groups Added", f"Added Groups: {', '.join(unique_folders)}")

    def add_timepoint(self):
        key = self.timepoint_key_var.get().strip()
        value = self.timepoint_value_var.get().strip()
        if key and value:
            self.timepoints[key] = value
            self.timepoint_key_var.set('')  # Clear input
            self.timepoint_value_var.set('')  # Clear input
            messagebox.showinfo("TimePoint Added", f"Added TimePoint: {key} -> {value}")
        else:
            messagebox.showwarning("Input Error", "Please enter both key and value for TimePoint.")

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

    def create_parameters_entries(self):
        self.parameters_vars = {}
        
        stat_test_options = [
            "t-test", "Mann-Whitney", "Wilcoxon", "Kruskal", "Brunner-Munzel"
        ]
        
        type_options = [
            "strip", "swarm", "box", "violin", 
            "boxen", "point", "bar", "count"
        ]
        
        legend_options = ["auto", "inside", "false"]
        
        for key, value in self.config.get('parameters', {}).items():
            frame = tk.Frame(self.parameters_frame)
            frame.pack(pady=5)
            tk.Label(frame, text=key).pack(side=tk.LEFT)
            
            var = tk.StringVar(value=value)
            self.parameters_vars[key] = var
            
            if key == 'stat_test':
                dropdown = tk.OptionMenu(frame, var, *stat_test_options)
                dropdown.pack(side=tk.LEFT)
            elif key == 'type':
                dropdown = tk.OptionMenu(frame, var, *type_options)
                dropdown.pack(side=tk.LEFT)
            elif key == 'legend':
                dropdown = tk.OptionMenu(frame, var, *legend_options)
                dropdown.pack(side=tk.LEFT)
            elif key == 'pairs':
                tk.Entry(frame, textvariable=var, width=20, state='readonly').pack(side=tk.LEFT)
            else:
                tk.Entry(frame, textvariable=var, width=20).pack(side=tk.LEFT)

    def save_config(self):
        main_folder = self.main_folder_var.get().strip()
        data_extension = self.data_extension_var.get().strip()
        frame_rate = self.frame_rate_var.get()
        ops_path = self.ops_path_var.get().strip()

        if not os.path.exists(main_folder):
            messagebox.showerror("Error", "Main folder does not exist.")
            return

        groups22 = {key_var.get(): value_var.get() for key_var, (key_var, value_var) in self.dict_vars.items()}

        pairs_input = self.pairs_var.get().strip()

        with open('gui_configurations.py', 'w') as f:
            f.write(f"main_folder = r'{main_folder}'\n")
            for i, group in enumerate(self.groups, start=1):
                f.write(f"group{i} = main_folder + r'{group}'\n")
            f.write(f"group_number = {len(self.groups)}\n")
            f.write(f"data_extension = '{data_extension}'\n")
            f.write(f"frame_rate = {frame_rate}\n")
            f.write(f"ops_path = r'{ops_path}'\n")

            f.write("TimePoints = {\n")
            for key, value in self.timepoints.items():
                f.write(f"    '{key}': '{value}',\n")
            f.write("}\n")

            f.write("Groups22 = {\n")
            for key, (key_var, value_var) in self.dict_vars.items():
                f.write(f"    '{key_var.get()}': '{value_var.get()}',\n")
            f.write("}\n")

            f.write(f"pairs = [ {pairs_input} ]\n")

            f.write("parameters = {\n")
            for key, var in self.parameters_vars.items():
                f.write(f"    '{key}': '{var.get()}',\n")
            f.write("}\n")

            f.write("## Additional configurations\n")
            f.write("nb_neurons = 16\n")
            f.write('model_name = "Global_EXC_10Hz_smoothing200ms"\n')
            f.write("EXPERIMENT_DURATION = 60\n")
            f.write("FRAME_INTERVAL = 1 / frame_rate\n")
            f.write("BIN_WIDTH = 20\n")
            f.write("FILTER_NEURONS = True\n")
            f.write("groups = []\n")
            f.write("for n in range(group_number):\n")
            f.write("    group_name = f\"group{n + 1}\"\n")
            f.write("    groups.append(eval(group_name))\n")
            f.write("for name, value in Groups22.items():\n")
            f.write("    # Add your logic to handle Groups22\n")
            f.write("    pass\n")

        messagebox.showinfo("Success", "Configurations saved successfully.")

    def proceed(self):
        if self.skip_suite2p_var.get():
            subprocess.call(["run_plots.bat"])  # Execute run_plots.bat
        else:
            self.show_ops_options()

    def show_ops_options(self):
        ops_window = tk.Toplevel(self.master)
        ops_window.title("Select Ops File Option")

        tk.Label(ops_window, text="Choose how to obtain the .ops file:").pack(padx=10, pady=10)

        # Option a: Insert file path
        tk.Label(ops_window, text="Insert Ops File Path:").pack(padx=10, pady=5)
        ops_path_entry = tk.Entry(ops_window, width=50)
        ops_path_entry.pack(padx=10, pady=5)
        
        def set_ops_path():
            self.ops_path_var.set(ops_path_entry.get())
            ops_window.destroy()

        tk.Button(ops_window, text="Set Ops Path", command=set_ops_path).pack(pady=5)

        # Option b: Edit default ops
        tk.Button(ops_window, text="Edit Default Ops", command=self.default_ops_suite2p).pack(pady=5)

        # Option c: Run Suite2P GUI
        tk.Button(ops_window, text="Run Suite2P", command=self.run_suite2p).pack(pady=5)

    def default_ops_suite2p(self):
        # Placeholder for the default ops function
        messagebox.showinfo("Default Ops", "Running default_ops_suite2p... (implement this function)")

    def run_suite2p(self):
        # Placeholder for running the Suite2P GUI
        messagebox.showinfo("Suite2P GUI", "Running Suite2P GUI... (implement this function)")

if __name__ == "__main__":
    root = tk.Tk()
    app = ConfigEditor(root)
    root.mainloop()
