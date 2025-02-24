import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd

# Predefined cell ratios
CELL_RATIOS = {
    "WT, RCL, BAP(J)": {"WT": 0.1925, "RCL": 0.1925, "BAP(J)": 0.615},
    "WT, RCL, BAP(J), TE 2": {"WT": 0.1925, "RCL": 0.1925, "BAP(J)": 0.3075, "TE 2": 0.3075},
    "WT, RCL, BAP(J), PrE 2": {"WT": 0.1925, "RCL": 0.09625, "BAP(J)": 0.615, "PrE 2": 0.09625},
    "WT, RCL, BAP(J), TE 2, PrE 2": {"WT": 0.1925, "RCL": 0.09625, "BAP(J)": 0.3075, "TE 2": 0.3075, "PrE 2": 0.09625}
}

# Store tab-specific variables
tabs_data = {}

def cells_calculation(cells_counts, dilution, total_cells_per_uwell, uwell_per_well, ratio, num_of_wells, volume_per_well, sorter_used):
    volumes = {}
    for cell_type, count in cells_counts.items():
        cells_per_ml = count if sorter_used else (count / 4) * 10**4 * dilution
        cell_type_ratio = ratio.get(cell_type, 1)
        cells_per_well = total_cells_per_uwell * uwell_per_well * cell_type_ratio
        total_num_of_cells = cells_per_well * (num_of_wells + 2)  # Extra for pipetting errors
        volume_to_add = total_num_of_cells / cells_per_ml
        volumes[cell_type] = round(volume_to_add * 1000, 2)  # Convert to µL
    media_vol = round((num_of_wells + 2) * volume_per_well - sum(volumes.values()), 2)
    roki_volume = round(((media_vol + sum(volumes.values())) / 1000) * 2, 2)
    total_volume = round(media_vol + sum(volumes.values()), 2)
    return volumes, media_vol, roki_volume, total_volume

def update_entries(tab_id):
    selected_cell_types = tabs_data[tab_id]['cell_type_var'].get()
    selected_ratio = CELL_RATIOS[selected_cell_types]
    sorter_used = tabs_data[tab_id]['sorter_var'].get()
    for cell, entry in tabs_data[tab_id]['entries'].items():
        if cell in selected_ratio.keys():
            entry.config(state="normal")
            label_text = f"{cell} Cells per mL" if sorter_used else f"{cell} number in 4 squares"
            tabs_data[tab_id]['entry_labels'][cell].config(text=label_text)
        else:
            entry.config(state="disabled")
            entry.delete(0, tk.END)

def calculate(tab_id):
    try:
        selected_cell_types = tabs_data[tab_id]['cell_type_var'].get()
        selected_ratio = CELL_RATIOS[selected_cell_types]
        sorter_used = tabs_data[tab_id]['sorter_var'].get()
        
        # Get user input for cell counts
        cells_counts = {cell: float(tabs_data[tab_id]['entries'][cell].get()) for cell in selected_ratio.keys()} if sorter_used else {cell: int(tabs_data[tab_id]['entries'][cell].get()) for cell in selected_ratio.keys()}
        
        # Get additional parameters
        dilution = float(tabs_data[tab_id]['dilution_entry'].get())
        total_cells_per_uwell = float(tabs_data[tab_id]['total_cells_per_uwell_entry'].get())
        uwell_per_well = float(tabs_data[tab_id]['uwell_per_well_entry'].get())
        num_of_wells = int(tabs_data[tab_id]['num_of_wells_entry'].get())
        volume_per_well = float(tabs_data[tab_id]['volume_per_well_entry'].get())

        # Perform calculations
        volumes, media_vol, roki_vol, total_vol = cells_calculation(
            cells_counts, dilution, total_cells_per_uwell, uwell_per_well, selected_ratio, num_of_wells, volume_per_well, sorter_used
        )

        # 🔥 Store the calculated results in `tabs_data`
        tabs_data[tab_id]["calculated_volumes"] = volumes
        tabs_data[tab_id]["media_volume"] = media_vol
        tabs_data[tab_id]["roki_volume"] = roki_vol
        tabs_data[tab_id]["total_volume"] = total_vol

        # Update the results in the UI
        tabs_data[tab_id]['result_text'].set(
            f"Volume to add (µL): {volumes}\n"
            f"Media Volume: {media_vol:.2f} µL\n"
            f"ROCKi Volume: {roki_vol:.2f} µL\n"
            f"Total Volume: {total_vol:.2f} µL"
        )

    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid numbers for all fields.")

def export_to_excel():
    try:
        experiment_name = experiment_name_entry.get().strip()
        if not experiment_name:
            messagebox.showerror("Export Error", "Please enter an experiment name.")
            return
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            initialfile=f"{experiment_name}_results",
            filetypes=[("Excel files", "*.xlsx")]
        )
        if not filepath:
            return

        data = []
        for tab_id, tab_data in tabs_data.items():
            condition_name = f"Condition {tab_id + 1}"
            
            # 🚀 Now using the **calculated volumes** instead of missing variable
            for cell, volume in tab_data["calculated_volumes"].items():
                data.append([
                    condition_name,
                    cell,
                    volume,  # Volume from calculations
                    tab_data["media_volume"],
                    tab_data["roki_volume"],
                    tab_data["total_volume"]
                ])

            data.append(["", "", "", "", "", ""])

        # Create DataFrame
        df = pd.DataFrame(data, columns=["Condition", "Cell Type", "Volume (µL)", "Media Volume (µL)", "ROCKi Volume (µL)", "Total Volume (µL)"])
        
        # Save to Excel
        df.to_excel(filepath, index=False)
        messagebox.showinfo("Export Successful", "Results exported to Excel successfully.")
    
    except Exception as e:
        messagebox.showerror("Export Error", f"An error occurred: {e}")
        
        # Create DataFrame
        df = pd.DataFrame(data, columns=["Condition", "Cell Type", "Volume (µL)", "Media Volume (µL)", "ROCKi Volume (µL)", "Total Volume (µL)"])
        
        # Save to Excel
        df.to_excel(filepath, index=False)
        messagebox.showinfo("Export Successful", "Results exported to Excel successfully.")
    except Exception as e:
        messagebox.showerror("Export Error", f"An error occurred: {e}")

root = tk.Tk()
root.title("Cell Volume Calculator")
root.geometry("600x800")


def create_main_gui(parent, tab_id):
    frame = ttk.Frame(parent)
    frame.pack(fill='both', expand=True)
    tabs_data[tab_id] = {
        'cell_type_var': tk.StringVar(),
        'sorter_var': tk.BooleanVar(),
        'entries': {},
        'entry_labels': {},
        'result_text': tk.StringVar()
    }

    default_values = {
    "Dilution Factor": "10",
    "Total Cells Per UWell": "120",
    "Micro wells per wells": "1200",
    "Number of Wells": "24",
    "Well's Volume": "500"
    }

    ttk.Label(frame, text="Select Cell Types").grid(row=0, column=0)
    cell_type_menu = ttk.Combobox(frame, textvariable=tabs_data[tab_id]['cell_type_var'], values=list(CELL_RATIOS.keys()), width=30)
    cell_type_menu.grid(row=0, column=1)
    cell_type_menu.bind("<<ComboboxSelected>>", lambda e: update_entries(tab_id))
    
    for idx, cell in enumerate(CELL_RATIOS["WT, RCL, BAP(J), TE 2, PrE 2"].keys()):
        tabs_data[tab_id]['entry_labels'][cell] = ttk.Label(frame, text=f"{cell} number in 4 squares")
        tabs_data[tab_id]['entry_labels'][cell].grid(row=idx+1, column=0)
        tabs_data[tab_id]['entries'][cell] = ttk.Entry(frame)
        tabs_data[tab_id]['entries'][cell].grid(row=idx+1, column=1)

    # Add missing fields inside the GUI
    params = ["Dilution Factor", "Total Cells Per UWell", "Micro wells per wells", "Number of Wells", "Well's Volume"]
    param_vars = ["dilution_entry", "total_cells_per_uwell_entry", "uwell_per_well_entry", "num_of_wells_entry", "volume_per_well_entry"]
    
    for i, param in enumerate(params):
        ttk.Label(frame, text=param).grid(row=idx+2+i, column=0)
        tabs_data[tab_id][param_vars[i]] = ttk.Entry(frame)
        tabs_data[tab_id][param_vars[i]].grid(row=idx+2+i, column=1)
        tabs_data[tab_id][param_vars[i]].insert(0, default_values[param])

    sorter_check = ttk.Checkbutton(frame, text="Used Cell Counter?", variable=tabs_data[tab_id]['sorter_var'], command=lambda: update_entries(tab_id))
    sorter_check.grid(row=idx+7, columnspan=2)

    ttk.Button(frame, text="Calculate", command=lambda: calculate(tab_id)).grid(row=idx+8, columnspan=2, pady=10)
    ttk.Button(frame, text="Export to CSV", command=export_to_excel).grid(row=idx+9, columnspan=2, pady=5)

    result_label = ttk.Label(frame, textvariable=tabs_data[tab_id]['result_text'], font=("Arial", 10), wraplength=450)
    result_label.grid(row=idx+10, columnspan=2, pady=10)

def go_to_main_page():
    experiment_name = experiment_name_entry.get()
    num_conditions = int(num_conditions_entry.get())
    if not experiment_name or num_conditions <= 0:
        messagebox.showerror("Input Error", "Please enter a valid experiment name and number of conditions.")
        return
    
    start_frame.pack_forget()
    notebook.pack(expand=True, fill="both")
    for i in range(num_conditions):
        tab = ttk.Frame(notebook)
        notebook.add(tab, text=f"Condition {i+1}")
        create_main_gui(tab, i)

# Start Page
start_frame = ttk.Frame(root)
start_frame.pack(pady=20)

ttk.Label(start_frame, text="Experiment Name:").grid(row=0, column=0)
experiment_name_entry = ttk.Entry(start_frame, width=30)
experiment_name_entry.grid(row=0, column=1)

ttk.Label(start_frame, text="Number of Conditions:").grid(row=1, column=0)
num_conditions_entry = ttk.Entry(start_frame, width=10)
num_conditions_entry.grid(row=1, column=1)

ttk.Button(start_frame, text="Next", command=go_to_main_page).grid(row=2, columnspan=2, pady=10)

# Notebook (Tabs for each condition)
notebook = ttk.Notebook(root)

root.mainloop()