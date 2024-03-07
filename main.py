import tkinter as tk
from tkinter import ttk
from battery_tab import BatteryTab

if __name__ == "__main__":
    # Create the main window
    root = tk.Tk()
    root.title("UoP Racing CAN Interface")
    root.geometry("1644x880")

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

# battery_tab.py content

# Importing necessary libraries for GUI creation within the tab


from tkinter import ttk


# BatteryTab class definition

class BatteryTab:

    def __init__(self, master):
        # Initialize the tab frame

        self.frame = ttk.Frame(master)
        self.master = master
        self.battery_tab = BatteryTab(self.master)

        # Bind the close_application method of BatteryTab to the window's close event
        self.master.protocol("WM_DELETE_WINDOW", self.battery_tab.close_application)
        # Call a method to set up widgets in the frame

        self.setup_widgets()

    def setup_widgets(self):
        # This method will create and place all widgets for the battery tab.

        # For now, we will just create a placeholder label.

        placeholder_label = ttk.Label(self.frame, text="This is the Battery tab.")

        placeholder_label.pack()

# Note: The actual use of BatteryTab class will be done in the main.py file,

# where an instance of this class will be created and added to the tab control.
