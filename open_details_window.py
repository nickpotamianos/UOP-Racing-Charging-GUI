import tkinter as tk
from tkinter import ttk


def open_details_window(master, initial_voltages, update_callback=None, on_close_callback=None):
    details_window = tk.Toplevel(master)
    details_window.title("Slave Detailed View")
    details_window.iconbitmap("formula.ico")

    # Store references to the voltage value labels
    voltage_labels = {}

    for i in range(1, 13):
        slave_frame = ttk.LabelFrame(details_window, text=f"Slave {i}", relief=tk.RIDGE, borderwidth=2)
        slave_frame.grid(row=(i - 1) // 4, column=(i - 1) % 4, padx=5, pady=5, sticky='nsew')

        voltage_labels[f"Slave {i}"] = []

        for cell in range(12):  # Assuming each slave has 12 cells
            ttk.Label(slave_frame, text=f"Cell {cell + 1}:").grid(row=cell, column=0, sticky='w')

            # Initialize the label for the cell voltage with default value
            volt_value_label = ttk.Label(slave_frame, text="0.00 V")
            volt_value_label.grid(row=cell, column=1, sticky='ew')

            voltage_labels[f"Slave {i}"].append(volt_value_label)

    # Function to update voltage labels
    def update_voltages():
        new_voltages = update_callback() if update_callback else initial_voltages
        flat_voltages = [v for slave_voltages in new_voltages.values() for v in slave_voltages]
        if flat_voltages:  # Check if flat_voltages is not empty
            min_voltage = min(flat_voltages)
            max_voltage = max(flat_voltages)

            for slave_key, labels in voltage_labels.items():
                slave_voltages = new_voltages.get(slave_key, [0.0] * 12)
                for cell, label in enumerate(labels):
                    cell_voltage = slave_voltages[cell]
                    label.config(text=f"{cell_voltage:.2f} V")

                    # Update label color based on voltage
                    if cell_voltage == min_voltage:
                        label.config(foreground='light green')
                    elif cell_voltage == max_voltage:
                        label.config(foreground='red')
                    else:
                        label.config(foreground='black')

    # Initial call to update voltages
    update_voltages()
    if on_close_callback:
        details_window.protocol("WM_DELETE_WINDOW", on_close_callback)
    # Schedule periodic updates

    def schedule_update():
        update_voltages()
        details_window.after(1000, schedule_update)  # Update every 1 second

    schedule_update()

    def on_close():
        if on_close_callback:
            on_close_callback()  # Call the passed callback, e.g., to reset the flag
        details_window.destroy()  # Close the window

    details_window.protocol("WM_DELETE_WINDOW", on_close)

    # Set minsize for the details window if necessary
    details_window.minsize(364, 400)

    return details_window
