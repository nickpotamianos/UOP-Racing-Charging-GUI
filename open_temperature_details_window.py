import tkinter as tk
from tkinter import ttk


def open_temperature_details_window(master, initial_temperatures, update_callback=None, on_close_callback=None):
    details_window = tk.Toplevel(master)
    details_window.title("Temperature Detailed View")

    temperature_labels = {}

    for i in range(1, 13):
        slave_frame = ttk.LabelFrame(details_window, text=f"Slave {i}", relief=tk.RIDGE, borderwidth=2)
        slave_frame.grid(row=(i - 1) // 3, column=(i - 1) % 3, padx=5, pady=5, sticky='nsew')

        temperature_labels[f"Slave {i}"] = []

        for temp_index in range(5):  # Assuming each slave has 5 temperature values
            ttk.Label(slave_frame, text=f"Temp {temp_index + 1}:").grid(row=temp_index, column=0, sticky='w')

            temp_value_label = ttk.Label(slave_frame, text="0.0 °C")
            temp_value_label.grid(row=temp_index, column=1, sticky='ew')
            temperature_labels[f"Slave {i}"].append(temp_value_label)

    def update_temperatures():
        new_temperatures = update_callback() if update_callback else initial_temperatures
        for slave_key, labels in temperature_labels.items():
            for temp_index, label in enumerate(labels):
                temp_value = new_temperatures.get(slave_key, [0.0] * 5)[temp_index]
                temp_value_display = f"{temp_value:.2f} °C" if temp_value is not None else "NaN"
                label.config(text=temp_value_display)

    def schedule_update():
        update_temperatures()
        details_window.after(1000, schedule_update)  # Update every 1 second

    schedule_update()

    def on_close():
        if on_close_callback:
            on_close_callback()  # Reset the flag in the BatteryTab class
        details_window.destroy()  # Close the window

    details_window.protocol("WM_DELETE_WINDOW", on_close)

    # Set minsize for the details window if necessary
    details_window.minsize(303, 294)
