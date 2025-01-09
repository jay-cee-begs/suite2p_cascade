import tkinter as tk
from tkinter import ttk

def run_pipeline():
    print("Pipeline executed!")

# Main window
root = tk.Tk()
root.title("Configuration Tabs")
root.geometry("600x400")

# Notebook for tabs
notebook = ttk.Notebook(root)

# Tab 1
tab1 = ttk.Frame(notebook)
notebook.add(tab1, text="Page 1")
ttk.Label(tab1, text="Configuration for Page 1").pack(pady=20, padx=20)

# Tab 2
tab2 = ttk.Frame(notebook)
notebook.add(tab2, text="Page 2")
ttk.Label(tab2, text="Configuration for Page 2").pack(pady=20, padx=20)

# Tab 3
tab3 = ttk.Frame(notebook)
notebook.add(tab3, text="Page 3")
ttk.Label(tab3, text="Configuration for Page 3").pack(pady=20, padx=20)

# Add the notebook to the main window
notebook.pack(expand=True, fill="both")

# Button to run the pipeline
run_button = ttk.Button(root, text="Run Pipeline", command=run_pipeline)
run_button.pack(pady=10)

# Run the application
root.mainloop()
