import tkinter as tk
from tkinter import ttk
from battery_tab import BatteryTab

if __name__ == "__main__":
    # Create the main window
    root = tk.Tk()
    root.title("UoP Racing CAN Interface")
    root.geometry("1644x880")
    root.iconbitmap("formula.ico")

    # Create the tab control

    tab_control = ttk.Notebook(root)

    # Create a frame for the 'Battery' tab
    battery_tab_frame = ttk.Frame(tab_control)
    battery_tab = BatteryTab(battery_tab_frame)  # Create an instance of BatteryTab
    battery_tab_frame.pack(fill="both", expand=True)  # Pack the frame to the window

    tab_control.add(battery_tab_frame, text='Battery')
    tab_control.pack(expand=1, fill="both")

    root.protocol("WM_DELETE_WINDOW", battery_tab.close_application)
    # Start the GUI loop
    root.mainloop()

