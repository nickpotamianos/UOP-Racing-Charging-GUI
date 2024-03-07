import tkinter as tk
from tkinter import ttk


def open_bms_window(update_callback, on_close_callback=None):
    window = tk.Tk()
    window.title("BMS Flags")

    flags_description = [
        "System Safe", "Over Voltage", "Under Voltage", "Over Temp Cells", "Under Temp Cells",
        "Abnormality Error", "Voltage Abnormality", "Temp Abnormality", "Voltage Sampling Abnormality",
        "Temperature Sampling Abnormality", "Over Current", "Under Current", "IVT Not Present",
        "Shutdown Status", "BMS Shutdown", "Is Precharged"
    ]

    indicators = {}

    for i, desc in enumerate(flags_description):
        ttk.Label(window, text=desc).grid(row=i, column=0, sticky='w')
        canvas = tk.Canvas(window, width=20, height=20)
        canvas.grid(row=i, column=1, padx=5, pady=2)
        # Initialize indicators as grey; they will be updated in `update_indicators`
        indicator = canvas.create_oval(5, 5, 15, 15, fill='grey')
        indicators[desc] = canvas

    def update_indicators():
        new_bms_flags = update_callback()  # Fetch latest BMS flags using the callback
        for i, desc in enumerate(flags_description):
            color = 'grey' if len(new_bms_flags) < i + 1 else ('#06b025' if new_bms_flags[i] == '1' else 'red')
            indicators[desc].itemconfig(indicator, fill=color)

    def schedule_update():
        update_indicators()
        window.after(1000, schedule_update)  # Schedule the next update

    schedule_update()  # Initial call to start the update loop

    def on_close():
        if on_close_callback:
            on_close_callback()  # Call the on_close_callback to reset the open window flag
        window.destroy()

    window.protocol("WM_DELETE_WINDOW", on_close)

    window.mainloop()
