import tkinter as tk

from tkinter import ttk


def run_pipeline():

    print("Pipeline executed!")


def go_to_next_tab(current_tab_index):

    # Select the next tab

    next_tab_index = current_tab_index + 1

    if next_tab_index < notebook.index("end"):  # Check if next tab exists

        notebook.select(next_tab_index)


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


# Next button for Tab 1

next_button_tab1 = ttk.Button(tab1, text="Next", command=lambda: go_to_next_tab(0))

next_button_tab1.pack(pady=10)


# Tab 2

tab2 = ttk.Frame(notebook)

notebook.add(tab2, text="Page 2")

ttk.Label(tab2, text="Configuration for Page 2").pack(pady=20, padx=20)


# Next button for Tab 2

next_button_tab2 = ttk.Button(tab2, text="Next", command=lambda: go_to_next_tab(1))

next_button_tab2.pack(pady=10)


# Tab 3

tab3 = ttk.Frame(notebook)

notebook.add(tab3, text="Page 3")

ttk.Label(tab3, text="Configuration for Page 3").pack(pady=20, padx=20)


# Process button for Tab 3

process_button_tab3 = ttk.Button(tab3, text="Process", command=run_pipeline)

process_button_tab3.pack(pady=10)


# Add the notebook to the main window

notebook.pack(expand=True, fill="both")


# Run the application

root.mainloop()