import tkinter as tk
from tkinter import ttk
from batch_core.analysis_model import AnalysisParams
from batch_core.multivid_reg_model import MultiVid_Reg_Params

class OpsEditor:
    def __init__(self, master, config):
        self.master = master
        self.config = config
        self.params = config.analysis_params

        self.vars = {}
        self.create_widgets()

    def create_widgets(self):
        self.param_rows = {}
        for idx, (param, value) in enumerate(self.params.to_dict().items()):

            if param in ['correction_method','normalization_method']:
                continue  
            tk.Label(self.master, text=param).grid(row=idx, column=0)
            self.param_rows[param] = idx

            if isinstance(value, bool):
                var = tk.BooleanVar(value=value)
                tk.Checkbutton(self.master, variable=var).grid(row=idx, column=1)
                if param == 'baseline_correction':
                    var.trace_add("write", self.add_baseline_correction)
                
                if param == "normalize_peaks":
                    var.trace_add("write", self.add_normalization)

            elif param == "Img_Overlay":
                var = tk.StringVar(value=value)
                ttk.Combobox(
                    self.master,
                    textvariable=var,
                    values=["max_proj", "meanImg"],
                    state="readonly"
                ).grid(row=idx, column=1)
                        
            else:
                var = tk.StringVar(value=str(value))
                tk.Entry(self.master, textvariable=var).grid(row=idx, column=1)

            self.vars[param] = var
        
        baseline_row = self.param_rows['baseline_correction'] + 1
        normalization_row = self.param_rows['normalize_peaks'] + 1

        self.baseline_frame = tk.Frame(self.master)
        self.baseline_frame.grid(
            row=baseline_row,
            column=0,
            columnspan=2,
            sticky="w",
            padx=20,
            pady=2
        )

        self.normalization_frame = tk.Frame(self.master)
        self.normalization_frame.grid(
            row=normalization_row,
            column=0,
            columnspan=2,
            sticky="w",
            padx=20,
            pady=2
        )
        # self.baseline_frame = tk.Frame(self.master)
        # self.baseline_frame.grid(row = 10, column = 0, columnspan=2, pady = 10)
        # self.normalization_frame = tk.Frame(self.master)
        # self.normalization_frame.grid(row = 10, column = 0, columnspan=2, pady = 10)
        if self.vars['baseline_correction'].get():
            self.add_baseline_correction()
        if self.vars['normalize_peaks'].get():
            self.add_normalization()
        
        tk.Button(self.master, text = "Save", command = self.save).grid(row = 30, column = 0)

    def add_baseline_correction(self, *args):

        if not self.vars['baseline_correction'].get():
            self.baseline_frame.grid_remove()
            return

        self.baseline_frame.grid()
            
        for widget in self.baseline_frame.winfo_children():
            widget.destroy()
        
        tk.Label(self.baseline_frame,
                    text = "correction_method"
                    ).grid(row=0, column=0)
        
        self.correction_method_var = tk.StringVar(
            value = self.params.correction_method
        )
        
        ttk.Combobox(
            self.baseline_frame,
            textvariable=self.correction_method_var,
            values=["airPLS", "rolling median"],
            state="readonly",
            width = 15
        ).grid(row=0, column=1)


    def add_normalization(self, *args):

        if not self.vars['normalize_peaks'].get():
            self.normalization_frame.grid_remove()
            return
        
        self.normalization_frame.grid()
            
        for widget in self.normalization_frame.winfo_children():
            widget.destroy()
        
        tk.Label(self.normalization_frame,
                    text = "F Normalization"
                    ).grid(row=0, column=0)
        
        self.normalization_method_var = tk.StringVar(
            value = self.params.normalization_method
        )
        
        ttk.Combobox(
            self.normalization_frame,
            textvariable=self.normalization_method_var,
            values=["Cell", "Population"],
            state="readonly",
            width = 15
        ).grid(row=0, column=1)

    def save(self):
        updated = {}

        for key, var in self.vars.items():
            val = var.get()

            if isinstance(var, tk.BooleanVar):
                updated[key] = val
            else:
                try:
                    updated[key] = float(val) if "." in val else int(val)
                except:
                    updated[key] = val
        
        updated['correction_method'] = self.correction_method_var.get()
        updated['normalization_method'] = self.normalization_method_var.get()

        self.config.analysis_params = AnalysisParams.from_dict(updated)
        self.master.destroy()


class MultiVidEditor:
    def __init__(self, master, config):
        self.master = master
        self.config = config
        self.params = config.multivid_params
        
        self.vars = {}
        self.length_frame = None
        self.length_vars = []

        self.create_widgets()

    
    def create_widgets(self):
        for idx, (param, value) in enumerate(self.params.to_dict().items()):
            if param in ['unequal_treatment_lengths','treatment_length_units']:
                continue
            tk.Label(self.master, text=param).grid(row=idx, column=0)
            
            if param == 'Treatment_No':
                var = tk.IntVar(value = value)

                tk.Spinbox(
                    self.master,
                    from_ = 1,
                    to = 20,
                    textvariable=var,
                    width = 5,
                ).grid(row = idx, column = 1)

                var.trace_add("write", self.update_treatment_length_inputs)

            elif isinstance(value, bool):
                var = tk.BooleanVar(value=value)
                tk.Checkbutton(self.master, variable=var).grid(row=idx, column=1)

                if param == 'equal_baseline_and_treatments':
                    var.trace_add("write", self.update_treatment_length_inputs)

            else:
                var = tk.StringVar(value = str(value))
                tk.Entry(self.master, textvariable=var).grid(row = idx, column = 1)
            
            self.vars[param] = var
        
        self.length_frame = tk.Frame(self.master)
        self.length_frame.grid(row = 20, column = 0, columnspan=2, pady = 10)
        if not self.vars['equal_baseline_and_treatments'].get():
            self.update_treatment_length_inputs()
        
        tk.Button(self.master, text = "Save", command = self.save).grid(row = 30, column = 0)

    def update_treatment_length_inputs(self, *args):

        if self.vars['equal_baseline_and_treatments'].get():
            self.length_frame.grid_remove()
            return
        else:
            self.length_frame.grid()
            
        for widget in self.length_frame.winfo_children():
            widget.destroy()
        
        self.length_vars = []
        
        tk.Label(self.length_frame,
                 text = "Treatment length units"
                 ).grid(row=0, column=0)
        
        self.length_unit_var = tk.StringVar(
            value = self.params.treatment_length_units
        )
        
        ttk.Combobox(
            self.length_frame,
            textvariable=self.length_unit_var,
            values=["seconds", "frames"],
            state="readonly",
            width = 10
        ).grid(row=0, column=1)

        try:
            num_treatments = int(self.vars["Treatment_No"].get())
        except:
            return
        
        for i in range(1, num_treatments + 2):
            label = "Baseline length" if i == 1 else f"Treatment {i-1} length"
        
            tk.Label(self.length_frame, text = label).grid(row = i, column = 0)

            var = tk.StringVar()

            if i < len(self.params.unequal_treatment_lengths):
                var.set(str(self.params.unequal_treatment_lengths[i]))

            tk.Entry(
                self.length_frame,
                textvariable=var,
                width = 10
            ).grid(row = i, column = 1)

            self.length_vars.append(var)

    def save(self):
        updated = {}

        for key, var in self.vars.items():
            val = var.get()
            if isinstance(var, tk.BooleanVar):
                updated[key] = val
            else:
                try:
                    updated[key] = float(val) if "." in val else int(val)
                except:
                    updated[key] = val
        if not self.vars['equal_baseline_and_treatments'].get():
            for var in self.length_vars:
                updated['unequal_treatment_lengths'] = [float(var.get())]

            updated['treatment_length_units'] = self.length_unit_var.get()
        else:
            updated['unequal_treatment_lengths'] = []
        

        self.config.multivid_params = MultiVid_Reg_Params.from_dict(updated)
        self.master.destroy()