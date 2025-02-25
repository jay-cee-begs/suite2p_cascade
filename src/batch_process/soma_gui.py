import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import filedialog
from pathlib import Path
import os
import subprocess
import time
import threading 
import json

class ConfigEditor:
    def __init__(self, master):
        self.master = master
        self.master.title("Ultimate Suite2P + Cascade Configuration Editor")
        self.master.geometry("700x750")  # Set initial window size

        # Create a canvas and a scrollbar
        self.canvas = tk.Canvas(master)
        self.scrollbar = tk.Scrollbar(master, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)


        # Configure the scrollbar #### Find a way to have the whole frame scrollable
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

        # Load existing configurations, needs an existing file to load from
        self.config = self.load_config()
        general_settings = self.config.get("general_settings", {})

        
        # if 'parameters' not in self.config:
        #     self.config['parameters'] = {
        #         'feature': ['Active_Neuron_Proportion'],  # Default features
        #         'stat_test': 't-test',                   # Default stat_test
        #         'type': 'box',                           # Default plot type
        #         'legend': 'auto',                        # Default legend option
        #         # Add other default parameters as needed
        #     }

        self.main_folder_var = tk.StringVar(value=general_settings.get('main_folder', ''))
        self.selected_bat_file = tk.StringVar()  # Initialize selected_bat_file
        self.data_extension_var = tk.StringVar(value=general_settings.get('data_extension', ''))
        self.frame_rate_var = tk.IntVar(value=general_settings.get('frame_rate', 10))
        self.ops_path_var = tk.StringVar(value=general_settings.get('ops_path', ''))
        self.csc_path_var = tk.StringVar(value=general_settings.get('cascade_file_path', ''))
        self.groups = general_settings.get('groups', [])
        self.exp_condition = {}#{key: value for key, value in self.config.get('exp_condition', {}).items()}
        self.exp_dur_var = tk.IntVar(value=general_settings.get("EXPERIMENT_DURATION", 60))
        self.bin_width_var = tk.IntVar(value=general_settings.get("BIN_WIDTH", ))

        # Main folder input
        self.main_frame = tk.Frame(self.scrollable_frame)
        self.main_frame.pack(padx=10, pady=5, anchor='w')
        tk.Label(self.main_frame, text="Experiment / Main Folder Path:").pack(side=tk.LEFT)
        tk.Entry(self.main_frame, textvariable=self.main_folder_var, width=50).pack(side=tk.LEFT)
        # Button to open file explorer for selecting a folder
        tk.Button(self.main_frame, text="Browse", command=self.browse_folder).pack(side=tk.LEFT)
        

        # Data extension input
        self.data_frame = tk.Frame(self.scrollable_frame)
        self.data_frame.pack(padx=10, pady=5, anchor='w')
        tk.Label(self.data_frame, text="Data Extension:").pack(side=tk.LEFT)
        tk.Entry(self.data_frame, textvariable=self.data_extension_var, width= 7).pack(padx=10)

        
        # Group input
        self.group_frame = tk.Frame(self.scrollable_frame)
        self.group_frame.pack(padx=10, pady=5, anchor='w')
        tk.Label(self.group_frame, text="Adds all subfolders from the Experiment:").pack(side=tk.LEFT)
        tk.Button(self.group_frame, text="Add Experiment Conditions", command=self.add_group).pack(side=tk.LEFT)

        #cascade path input
        self.csc_frame = tk.Frame(self.scrollable_frame)
        self.csc_frame.pack(padx=10, pady=5, anchor='w')
        tk.Label(self.csc_frame, text="Cascade File Path:").pack(side=tk.LEFT)
        tk.Entry(self.csc_frame, textvariable=self.csc_path_var, width=40).pack(side=tk.LEFT)
        tk.Button(self.csc_frame, text="Browse", command=self.browse_cascade).pack(side=tk.LEFT)
       
        # Ops path input
        self.ops_frame = tk.Frame(self.scrollable_frame)
        self.ops_frame.pack(padx=10, pady=5, anchor='w')
        tk.Label(self.ops_frame, text="Ops.npy Path Options:").pack(side=tk.LEFT)
        #tk.Entry(self.ops_frame, textvariable=self.ops_path_var, width=40).pack(side=tk.LEFT)
        
        
        # Option a: Insert file path
       
        tk.Entry(self.ops_frame, textvariable=self.ops_path_var, width=40).pack(side=tk.LEFT)
        tk.Button(self.ops_frame, text="Browse", command=self.browse_ops_file).pack(side=tk.LEFT)

        
        # Option c: Create new ops file
        tk.Button(self.ops_frame, text="Create New Ops File (WIP)", command=self.create_new_ops_file).pack(pady=5, side=tk.LEFT)
        
        
        # Frame rate input
        self.Frame_frame = tk.Frame(self.scrollable_frame)
        self.Frame_frame.pack(padx=10, pady=5, anchor='w')
        tk.Label(self.Frame_frame, text="Frame Rate:").pack(side=tk.LEFT)
        tk.Entry(self.Frame_frame, textvariable=self.frame_rate_var, width =7).pack(padx=10)
        tk.Label(self.scrollable_frame, text="Press any key in terminal when GUI is stuck", background='yellow').pack( padx=10, pady=5)

        # Editable exp_condition
        # tk.Label(self.scrollable_frame, text="Same goes for your Groups, dont leave the brackets empty:").pack(anchor='w')
        # tk.Label(self.scrollable_frame, text="(In case your structure looks like 'TimePoint_Condition' you can remove 'TimePoint_' )").pack(anchor='w')
        
        self.exp_condition_frame = tk.Frame(self.scrollable_frame)
        self.exp_condition_frame.pack(padx=10, pady=5)
        self.create_dict_entries(self.exp_condition_frame, " ", self.exp_condition)

        # Save button
        self.setup_ui()

        # Skip Suite2P option
        # self.selected_bat_file = tk.StringVar()
        # tk.Checkbutton(self.scrollable_frame, text="Skip Suite2P, no need to run it twice :)", variable=self.skip_suite2p_var).pack(anchor='w', padx=10, pady=5)


  

################ Functions AREA ################    put in seperate file eventually
    def setup_ui(self):
        # Setup the UI components in here in the future
        tk.Button(self.scrollable_frame, text="Edit Cascade Settings", command=self.edit_cascade_settings).pack(pady=5)
        tk.Button(self.scrollable_frame, text="Edit Graphical Outputs", command=self.edit_graphical_outputs).pack(pady=10)
        tk.Button(self.scrollable_frame, text="Save Configurations", command=self.save_config).pack(pady=10)

        self.create_process_buttons()

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(-1 * (event.delta // 120), "units")   

    def edit_cascade_settings(self):
        """Call the function to edit cascade analysis settings"""
        current_dir = Path(__file__).parent
        scripts_dir = current_dir / "Scripts"
        bat_file = scripts_dir / "edit_cascade_settings.bat"
        subprocess.call([str(bat_file)])  # Execute run_default_ops.bat
        self.merge_cascade_settings()
    
    def edit_graphical_outputs(self):
        """Call GUI to edit graphical outputs"""
        current_dir = Path(__file__).parent
        scripts_dir = current_dir / "Scripts"
        bat_file = scripts_dir / "edit_graphical_outputs.bat"
        subprocess.call([str(bat_file)])  # Execute run_default_ops.bat
        self.merge_graphical_outputs()

    def merge_cascade_settings(self):
        script_dir = Path(__file__).resolve().parent
        cascade_settings_file = script_dir / "../../config/cascade_settings.json"
        config_file_path = script_dir / "../../config/config.json"

        if Path(cascade_settings_file).exists():
            with open(cascade_settings_file, 'r') as f:
                cascade_settings = json.load(f)
        
            if Path(config_file_path).exists():
                with open(config_file_path, 'r') as f:
                    config_data = json.load(f)
            else:
                config_data = {}
            
            config_data['cascade_settings'] = cascade_settings
            with open(config_file_path, 'w') as f:
                json.dump(config_data, f, indent=1)

            messagebox.showinfo("Success","Cascade settings were updated! \n Merged with config.json was successful!")
        else:
            messagebox.showerror("Error", "No analysis parameters found;\n using default parameters")
            
            cascade_settings = { #self.default_cascade_parameters
            'predicted_spike_threshold': 0.1, #need to check if 0.0 or 0.1 gives different results
            'nb_neurons': 16,
            'model_name': "Global_EXC_10Hz_smoothing200ms",
            'use_suite2p_ROI_classifier': False,
            'update_suite2p_iscell': True,
            'overwrite_existing_cascade_output': False,
        }
            if Path(config_file_path).exists():
                with open(config_file_path, 'r') as f:
                    config_data = json.load(f)
            else:
                config_data = {}
            
            config_data['cascade_settings'] = cascade_settings

    def merge_graphical_outputs(self):
            script_dir = Path(__file__).resolve().parent
            graphical_outputs_file = script_dir / "../../config/cascade_settings.json"
            config_file_path = script_dir / "../../config/config.json"

            if Path(graphical_outputs_file).exists():
                with open(graphical_outputs_file, 'r') as f:
                    graphical_outputs = json.load(f)
            
                if Path(config_file_path).exists():
                    with open(config_file_path, 'r') as f:
                        config_data = json.load(f)
                else:
                    config_data = {}
                
                config_data['graphical_outputs'] = graphical_outputs
                with open(config_file_path, 'w') as f:
                    json.dump(config_data, f, indent=1)

                messagebox.showinfo("Success","Graph Outputs were updated! \n Merged with config.json was successful!")
            else:
                messagebox.showerror("Error", "No graphical output json file was found;\n using default parameters")
                
                graphical_outputs = { #self.default_cascade_parameters
                'total_estimated_spike_histogram': False, #need to check if 0.0 or 0.1 gives different results
                'total_estimated_spikes_per_frame': True,
                'avg_estimated_spikes_per_frame': True,
                'Img_ROI_Overlay': 'max_proj',
                
            }
                if Path(config_file_path).exists():
                    with open(config_file_path, 'r') as f:
                        config_data = json.load(f)
                else:
                    config_data = {}
                
                config_data['graphical_outputs'] = graphical_outputs
    
    def create_new_ops_file(self):
        """Call the function to create new ops file"""
        current_dir = Path(__file__).parent
        scripts_dir = current_dir / "Scripts"
        bat_file = scripts_dir / "run_s2p_gui.bat"
        subprocess.call([str(bat_file)])  # Execute run_s2p_gui.bat


    def browse_ops_file(self):
        file_selected = filedialog.askopenfilename(filetypes=[("Ops Files", "*.npy")])
        if file_selected:
            self.ops_path_var.set(file_selected)

    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.main_folder_var.set(folder_selected)
    
    def browse_cascade(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.csc_path_var.set(folder_selected)


    def load_config(self):
        try:    
            script_dir = Path(__file__).resolve().parent  # Get current script directory (project/src/gui_config)
            config_file_path = (script_dir / "../../config/config.json").resolve()  # Navigate to config folder

            with open(config_file_path, 'r')as f:
                config = json.load(f)
        except FileNotFoundError:
            messagebox.showerror("Error", "Configuration file not found. Starting with default settings.")
            return {}
        return config

    def add_group(self):
        self.groups.clear()
        main_folder = self.main_folder_var.get().strip()
        if not Path(main_folder).exists():
            messagebox.showerror("Error", "Main folder does not exist.")
            return
        
        file_ending = self.data_extension_var.get().strip()  # Get the specified file extension

        def check_for_single_image_file_in_folder(current_path, file_ending):
            """
            Check if the specified path contains exactly one file with the given extension.
            """
            files = [file for file in os.listdir(current_path) if file.endswith(file_ending)]
            return len(files)
        all_folders = [f for f in os.listdir(main_folder) if os.path.isdir(os.path.join(main_folder, f))]
        excluded_substrings = []
        unique_folders = [folder for folder in all_folders if not any(excluded in folder for excluded in excluded_substrings)]

        file_ending = self.data_extension_var.get().strip()  # Get the specified file extension

        valid_folders = []  # To hold valid folders
        
        for folder_name in unique_folders:
            current_folder_path = os.path.join(main_folder, folder_name)
            if check_for_single_image_file_in_folder(current_folder_path, file_ending) >= 1:
                valid_folders.append(folder_name)
                
            else:
                # Check if any subfolder has exactly one file with the specified extension
                subfolders = [f for f in os.listdir(current_folder_path) if os.path.isdir(os.path.join(current_folder_path, f))]
                for subfolder in subfolders:
                    subfolder_path = os.path.join(current_folder_path, subfolder)
                    if check_for_single_image_file_in_folder(subfolder_path, file_ending) == 1:
                        valid_folders.append(folder_name)
                        break  # No need to check other subfolders if one matches

        for folder_name in valid_folders:
            group_path = f"\\{folder_name}" if not folder_name.startswith("\\") else folder_name
            
            if folder_name not in self.exp_condition:
                self.exp_condition[folder_name] = f"{folder_name}" #populates it with the folder name for the user to change?
            
            if group_path not in self.groups:
                self.groups.append(group_path)

        self.update_exp_condition_entries()
        
        if valid_folders:
            messagebox.showinfo("Groups Added", f"Added Groups: {', '.join(valid_folders)}")
        else:
            messagebox.showinfo("No Groups Added", "No (sub-)folders with one or more files matching the specified extension were found.")      

    def create_dict_entries(self, master, title, dictionary):
        """will allow you to edit dictionaries in the configurations file"""
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

    def update_exp_condition_entries(self):
        """Update the entries in the exp_condition dictionary with the use of create_dict_entries"""
        for widget in self.exp_condition_frame.winfo_children():
            widget.destroy()  # Remove old entries
        self.create_dict_entries(self.exp_condition_frame, "exp_condition", self.exp_condition)
   
    def csc_path(self):
        """Call this function to get or set the path to the cascade file"""
        csc_path = self.csc_path_var.get().strip()

        # Check if the path is already in the configuration
        if 'cascade_file_path' in self.config:
            csc_path = self.config['cascade_file_path']
            self.csc_path_var.set(csc_path)
        else:
            self.config['cascade_file_path'] = csc_path
        
        return csc_path
    
    def reload_config(self):
        """Reload the configuration file to refresh the GUI."""
        self.config = self.load_config("config.json")  # Reload the configuration file
        # Update the GUI variables with the new values from the config
        self.main_folder_var.set(self.config.get('main_folder', ''))
        self.data_extension_var.set(self.config.get('data_extension', ''))
        self.frame_rate_var.set(self.config.get('frame_rate', 10))
        self.ops_path_var.set(self.config.get('ops_path', ''))
        self.csc_path_var.set(self.config.get('cascade_file_path', ''))

        # Update the GUI components to reflect the new values
        self.update_exp_condition_entries()
        self.create_parameters_entries()
  
        # Optionally, you can also refresh other specific widgets or labels here.
        messagebox.showinfo("Config Reloaded", "Configuration file has been reloaded successfully.")
    
    def save_config(self):
        main_folder = str(Path(self.main_folder_var.get().strip()).resolve())
        data_extension = self.data_extension_var.get().strip()
        frame_rate = self.frame_rate_var.get()
        ops_path = str(Path(self.ops_path_var.get().strip()).resolve())
        csc_path = str(Path(self.csc_path_var.get().strip()).resolve())
        BIN_WIDTH = self.bin_width_var.get()
        EXPERIMENT_DURATION = self.exp_dur_var.get()

        if not Path(main_folder).exists():
            messagebox.showerror("Error", "Main folder does not exist.")
            return

        exp_condition = {key_var.get(): value_var.get() for key_var, (key_var, value_var) in self.dict_vars.items()} ### ????????????? is this still needed?? 

        # Construct the absolute path to the configuration file, saving uses the same logic as loading now
        script_dir = Path(__file__).resolve().parent  # Get current script directory (project/src/gui_config)
        config_filepath = (script_dir / "../../config").resolve()
        if not config_filepath.exists():
            config_filepath.mkdir(parents=True, exist_ok=True)
        json_filepath = (script_dir / "../../config/config.json").resolve()  # Navigate to config folder
        cascade_settings_path = (script_dir / "../../config/cascade_settings.json")
        graph_settings_path = (script_dir / "../../config/graph_settings.json")
        if cascade_settings_path.exists():
            with open(cascade_settings_path, 'r') as f:
                cascade_settings = json.load(f)
        else:
            cascade_settings = {'overwrite_suite2p': False,
            'skew_threshold': 1.0,
            'compactness_threshold': 1.4, #TODO implement cutoff / filter to rule out compact failing ROIs
            "peak_detection_threshold": 4.5,
            'peak_count_threshold': 2,
            'Img_Overlay': 'max_proj',
            'use_suite2p_ROI_classifier': False,
            'update_suite2p_iscell': True,
            'return_decay_times': False,
            }
        if graph_settings_path.exists():
            with open(graph_settings_path, 'r') as f:
                graph_settings = json.load(f)
        else:
            graph_settings = {
                'total_estimated_spike_histogram': False, 
            'total_estimated_spikes_per_frame': True,
            'avg_estimated_spikes_per_frame': True,
            'Img_ROI_Overlay': 'max_proj',
            }

        config_data = {
            "general_settings":{
                "main_folder": main_folder,
                "groups": [str(Path(main_folder) / condition) for condition in self.dict_vars.keys()],
                "group_number": len(self.groups),
                # "exp_condition": {key_var.get(): value_var.get() for key_var, (key_var, value_var) in self.dict_vars.items()},
                "data_extension": data_extension,
                "cascade_file_path": csc_path,
                "frame_rate": frame_rate,
                "ops_path": ops_path,
                "BIN_WIDTH": BIN_WIDTH,
                "EXPERIMENT_DURATION": EXPERIMENT_DURATION,
                "FRAME_INTERVAL": 1 / float(frame_rate),
                "FILTER_NEURONS": True,
            },
            "cascade_settings": cascade_settings,
            "graph_settings": graph_settings,
        }
        with open(json_filepath, 'w') as json_file:
            json.dump(config_data, json_file, indent = 1)

        # with open(config_filepath, 'w') as f:
        #     f.write('import numpy as np \n')
        #     f.write(f"main_folder = r'{main_folder}'\n")
        #     for i, group in enumerate(self.groups, start=1):
        #         f.write(f"group{i} = main_folder + r'{group}'\n")
        #     f.write(f"group_number = {len(self.groups)}\n")
        #     f.write(f"data_extension = '{data_extension}'\n")
        #     f.write(f"frame_rate = {frame_rate}\n")
        #     f.write(f"cascade_file_path = r'{csc_path}'\n")
        #     f.write(f"ops_path = r'{ops_path}'\n")
        #     f.write("ops = np.load(ops_path, allow_pickle=True).item()\n")
        #     f.write("ops['frame_rate'] = frame_rate\n")
        #     f.write("ops['input_format'] = data_extension\n")
        #     f.write(f"BIN_WIDTH = {BIN_WIDTH}\n")
        #     f.write(f"EXPERIMENT_DURATION = {EXPERIMENT_DURATION}\n")
        #     f.write("FRAME_INTERVAL = 1 / frame_rate\n")
        #     f.write("FILTER_NEURONS = True\n")
        #     f.write("exp_condition = {\n")
        #     for key, (key_var, value_var) in self.dict_vars.items():
        #         f.write(f"    '{key_var.get()}': '{value_var.get()}',\n")
        #     f.write("}\n")

            #TODO examine iscell_var to fix calls for json file

            # if self.iscell_var.get() == False:
            #     f.write("overwrite = True \n")
            #     f.write("iscell_check= False \n")
            #     f.write("update_iscell = True \n")
            # else:
            #     f.write("overwrite = False \n")
            #     f.write("iscell_check= True \n")
            #     f.write("update_iscell = False \n")
            
            # #### Add addtionals here, maybe make them editable in the gui as well
            # #TODO implement additional parameters to json file
            # f.write("## Additional configurations\n")
            # f.write("nb_neurons = 16\n")
            # f.write('model_name = "Global_EXC_10Hz_smoothing200ms"\n')
            # f.write("FILTER_NEURONS = True\n")
        messagebox.showinfo("Success", "Configurations saved successfully.")

        #reload the gui
        #self.reload_config()

    def get_current_dir(self):
        return self.current_dir 
    
    def move_up(self, levels = 1):
        new_dir = self.current_dir


    def show_log_window(self, log_file):
        log_window = tk.Toplevel(self.master)
        log_window.title("Process Log")

        with open(log_file, "r") as f:
            log_content = f.read()

        text_widget = tk.Text(log_window, wrap="word")
        text_widget.insert("1.0", log_content)
        text_widget.config(state=tk.DISABLED)  # Make the text widget read-only
        text_widget.pack(expand=True, fill="both")

        tk.Button(log_window, text="Close", command=log_window.destroy).pack(pady=5)

    def create_bat_file_radiobuttons(self, parent_frame):
        bat_files = [
            ("Skip Suite2p", "run_cascade.bat"),
            ("Skip Suite2p AND Cascade", "run_plots.bat"),
            ("Run Full Process", "run_sequence.bat")
        ]

        for text, value in bat_files:
            tk.Radiobutton(parent_frame, text=text, variable=self.selected_bat_file, value=value).pack(anchor='w')
    
    def create_iscell_button(self, parent_frame):
        self.iscell_var = tk.BooleanVar()
        tk.Checkbutton(parent_frame, text="use iscell.npy", variable=self.iscell_var).pack(pady=5)
        return self.iscell_var

    def create_process_button(self, parent_frame):
        tk.Button(parent_frame, text="Process", command=self.proceed).pack(pady=5)


    def create_process_buttons(self):
        """
        Create buttons for selecting and executing different processing options.

        This method creates a frame containing radio buttons for selecting different 
        .bat files to run, and a button to start the processing based on the selected option.
        """
        process_frame = tk.Frame(self.scrollable_frame)
        process_frame.pack(pady=10)

        tk.Label(process_frame, text="Select Process:").pack(anchor='w')

        self.create_bat_file_radiobuttons(process_frame)
        self.create_iscell_button(process_frame)
        self.create_process_button(process_frame)

    

    def proceed(self):  #Option to skip suite2p, will execute a different .bat then
        current_dir = Path(__file__).parent
        scripts_dir = current_dir / "Scripts" 
        bat_file = scripts_dir / self.selected_bat_file.get()
        
        if "run_sequence" in self.selected_bat_file.get():
            file_count = self.count_files_with_ending()
            if file_count > 0:
                self.show_progress_bar(file_count)
            else:
                messagebox.showerror("Error", "No files found with the specified file ending.")
                

            
        print(f"Executing {bat_file}")
        #subprocess.call([str(bat_file)])  # Execute sequence.bat
        threading.Thread(target=self.run_subprocess, args=(bat_file,)).start()

    def run_subprocess(self, bat_file):
        subprocess.call([str(bat_file)])  # Execute sequence.bat
        # Redirect the terminal output to a text file, seperate function to reduce interference with the process bar
        scripts_dir = Path(bat_file).parent
        log_file = scripts_dir / "process_log.txt"
        with open(log_file, "w") as f:
            process = subprocess.Popen([str(bat_file)], stdout=f, stderr=subprocess.STDOUT)
            process.wait()

        # Display the log file content in a new GUI window
        self.show_log_window(log_file)

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

###### Progress bar #####

    def process_files(self):
        if not self.skip_suite2p_var.get():
            file_count = self.count_files_with_ending()
            if file_count > 0:
                self.show_progress_bar(file_count)
            else:
                messagebox.showerror("Error", "No files found with the specified file ending.")
        else:
            messagebox.showinfo("Info", "Skipping Suite2p processing.")

    def count_files_with_ending(self):
        main_folder = self.main_folder_var.get().strip()
        file_ending = self.data_extension_var.get().strip()
        file_count = 0

        for root, dirs, files in os.walk(main_folder):
            for file in files:
                if file.endswith(file_ending):
                    file_count += 1

        return file_count

    def show_progress_bar(self, file_count):
        progress_window = tk.Toplevel(self.scrollable_frame)
        progress_window.title("Processing Files")

        tk.Label(progress_window, text="Processing files...").pack(pady=10)

        progress_bar = ttk.Progressbar(progress_window, length=300, mode='determinate')
        progress_bar.pack(pady=10)

        estimated_time = 55 * 60  # 55 minutes for 24 files
        time_per_file = estimated_time / 24
        total_time = time_per_file * file_count

        def update_progress():
            for i in range(file_count):
                time.sleep(time_per_file)
                progress_bar['value'] += (100 / file_count)
                progress_window.update_idletasks()

            progress_window.destroy()
            messagebox.showinfo("Info", "Processing completed.")

        threading.Thread(target=update_progress).start()


if __name__ == "__main__":
    root = tk.Tk()
    app = ConfigEditor(root)
    root.mainloop()
