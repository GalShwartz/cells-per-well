import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd

# Predefined cell ratios
CELL_RATIOS = {
    "WT, RCL, BAP(J)": {"WT": 0.1925, "RCL": 0.1925, "BAP(J)": 0.615},
    "WT, RCL, BAP(J), iTEAD4": {"WT": 0.1925, "RCL": 0.1925, "BAP(J)": 0.3075, "iTEAD4": 0.3075},
    "WT, RCL, BAP(J), Rapamycin": {"WT": 0.1925, "RCL": 0.09625, "BAP(J)": 0.615, "Rapamycin": 0.09625},
    "WT, RCL, BAP(J), iTEAD4, Rapamycin": {"WT": 0.1925, "RCL": 0.09625, "BAP(J)": 0.3075, "iTEAD4": 0.3075, "Rapamycin": 0.09625}
}

def cells_calculation(cells_counts, dilution, total_cells_per_uwell, uwell_per_well, ratio, num_of_wells, volume_per_well, sorter_used):
    volumes = {}
    
    for cell_type, count in cells_counts.items():
        if sorter_used:
            cells_per_ml = count  # Use the provided cells per mL directly
        else:
            cells_per_ml = (count / 4) * 10**4 * dilution
        
        cell_type_ratio = ratio.get(cell_type, 1)
        cells_per_well = total_cells_per_uwell * uwell_per_well * cell_type_ratio
        total_num_of_cells = cells_per_well * (num_of_wells + 2)  # Extra for pipetting errors
        volume_to_add = total_num_of_cells / cells_per_ml
        volumes[cell_type] = volume_to_add * 1000  # Convert to µL
    
    media_vol = (num_of_wells + 2) * volume_per_well - sum(volumes.values())
    roki_volume = ((media_vol + sum(volumes.values())) / 1000) * 2
    total_volume = media_vol + sum(volumes.values())
    
    return volumes, media_vol, roki_volume, total_volume

def calculate():
    try:
        selected_cell_types = cell_type_var.get()
        selected_ratio = CELL_RATIOS[selected_cell_types]
        sorter_used = sorter_var.get()
        
        cells_counts = {cell: float(entries[cell].get()) for cell in selected_ratio.keys()} if sorter_used else {cell: int(entries[cell].get()) for cell in selected_ratio.keys()}
        
        dilution = float(dilution_entry.get())
        total_cells_per_uwell = float(total_cells_per_uwell_entry.get())
        uwell_per_well = float(uwell_per_well_entry.get())
        num_of_wells = int(num_of_wells_entry.get())
        volume_per_well = float(volume_per_well_entry.get())
        
        volumes, media_vol, roki_vol, total_vol = cells_calculation(
            cells_counts, dilution, total_cells_per_uwell, uwell_per_well, selected_ratio, num_of_wells, volume_per_well, sorter_used
        )
        
        result_text.set(f"Volume to add (µL): {volumes}\nMedia Volume: {media_vol:.2f} µL\nROCKi Volume: {roki_vol:.2f} µL\nTotal Volume: {total_vol:.2f} µL")
    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid numbers for all fields.")

def export_to_csv():
    try:
        filepath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not filepath:
            return
        
        data = {"Cell Type": list(entries.keys()), "Volume (µL)": [entries[cell].get() for cell in entries.keys()]}
        df = pd.DataFrame(data)
        df.to_csv(filepath, index=False)
        messagebox.showinfo("Export Successful", "Results exported to CSV successfully.")
    except Exception as e:
        messagebox.showerror("Export Error", f"An error occurred: {e}")

# Create GUI window
root = tk.Tk()
root.title("Cell Volume Calculator")
root.geometry("500x700")

# Input fields
frame = ttk.Frame(root)
frame.pack(pady=10)

ttk.Label(frame, text="Select Cell Types").grid(row=0, column=0)
cell_type_var = tk.StringVar(value="WT, RCL, BAP(J)")
cell_type_menu = ttk.Combobox(frame, textvariable=cell_type_var, values=list(CELL_RATIOS.keys()))
cell_type_menu.grid(row=0, column=1)

entries = {}
for idx, cell in enumerate(CELL_RATIOS["WT, RCL, BAP(J)"].keys()):
    ttk.Label(frame, text=f"{cell} Count/Cells per mL").grid(row=idx+1, column=0)
    entries[cell] = ttk.Entry(frame)
    entries[cell].grid(row=idx+1, column=1)

ttk.Label(frame, text="Dilution Factor").grid(row=4, column=0)
dilution_entry = ttk.Entry(frame)
dilution_entry.grid(row=4, column=1)
dilution_entry.insert(0, "10")

ttk.Label(frame, text="Total Cells Per UWell").grid(row=5, column=0)
total_cells_per_uwell_entry = ttk.Entry(frame)
total_cells_per_uwell_entry.grid(row=5, column=1)
total_cells_per_uwell_entry.insert(0, "120")

ttk.Label(frame, text="Number of Wells").grid(row=6, column=0)
num_of_wells_entry = ttk.Entry(frame)
num_of_wells_entry.grid(row=6, column=1)
num_of_wells_entry.insert(0, "24")

ttk.Label(frame, text="Micro wells per wells").grid(row=7, column=0)
uwell_per_well_entry = ttk.Entry(frame)
uwell_per_well_entry.grid(row=7, column=1)
uwell_per_well_entry.insert(0, "1200")

ttk.Label(frame, text="Well's volume").grid(row=8, column=0)
volume_per_well_entry = ttk.Entry(frame)
volume_per_well_entry.grid(row=8, column=1)
volume_per_well_entry.insert(0, "500")

sorter_var = tk.BooleanVar()
sorter_check = ttk.Checkbutton(frame, text="Used Cell Sorter?", variable=sorter_var)
sorter_check.grid(row=9, columnspan=2)

ttk.Button(root, text="Calculate", command=calculate).pack(pady=10)
ttk.Button(root, text="Export to CSV", command=export_to_csv).pack(pady=5)

result_text = tk.StringVar()
result_label = ttk.Label(root, textvariable=result_text, font=("Arial", 10), wraplength=450)
result_label.pack(pady=10)

root.mainloop()
