import tkinter as tk
from tkinter import ttk


def open_bms_window(master, update_callback, on_close_callback=None):
    details_window = tk.Toplevel(master)
    details_window.title("BMS Flags")
    details_window.iconbitmap("formula.ico")

    flags_description = [
        "System Safe", "Over Voltage", "Under Voltage", "Over Temp Cells", "Under Temp Cells",
        "Abnormality Error", "Voltage Abnormality", "Temp Abnormality", "Voltage Sampling Abnormality",
        "Temperature Sampling Abnormality", "Over Current", "Under Current", "IVT Not Present",
        "Shutdown Status", "BMS Shutdown", "Is Precharged"
    ]

    # Display the BMS flag on top
    bms_flag_label = ttk.Label(details_window, text="BMS Flag: ", font=("Arial", 10))
    bms_flag_label.grid(row=0, column=0, columnspan=3, pady=2)

    indicators = {}

    for i, desc in enumerate(flags_description):
        row = i * 2 + 1  # Adjust row number for labels considering separators
        ttk.Label(details_window, text=desc).grid(row=row, column=0, sticky='w')
        canvas = tk.Canvas(details_window, width=20, height=20)
        canvas.grid(row=row, column=1, padx=5, pady=2)
        indicator = canvas.create_oval(5, 5, 15, 15, fill='grey')
        indicators[desc] = canvas

        # Add a horizontal separator after each row
        separator = ttk.Separator(details_window, orient='horizontal')
        separator.grid(row=row + 1, column=0, columnspan=2, sticky='ew', pady=2)

    def update_indicators():
        new_bms_flags = update_callback()  # Fetch latest BMS flags using the callback
        bms_flag_label.config(text="BMS Flag: " + new_bms_flags)  # Update the BMS flag label
        for i, desc in enumerate(flags_description):
            color = 'grey' if len(new_bms_flags) < i + 1 else ('#06b025' if new_bms_flags[i] == '1' else 'red')
            indicators[desc].itemconfig(indicator, fill=color)

    def schedule_update():
        update_indicators()
        details_window.after(1000, schedule_update)  # Schedule the next update

    schedule_update()  # Initial call to start the update loop

    def on_close():
        if on_close_callback:
            on_close_callback()  # Call the on_close_callback to reset the open window flag
        details_window.destroy()

    details_window.protocol("WM_DELETE_WINDOW", on_close)

    details_window.minsize(227, 566)

    return details_window
