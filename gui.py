import tkinter as tk
from tkinter import ttk


# Main GUI Application


class BatteryGUI(tk.Tk):
    def __init__(self):
        super().__init__()

        # Build GUI elements
        self.build_gui()

    def build_gui(self):
        # Main frame for the entire GUI
        main_frame = tk.Frame(self)
        main_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Create a frame to hold the buttons
        button_frame = tk.Frame(main_frame)
        button_frame.grid(row=0, column=0, sticky="nw", padx=10, pady=10)

        # Define the buttons and their placement
        ttk.Button(button_frame, text="TS Toggle", command=self.on_ts_toggle).grid(side=tk.TOP, fill=tk.X)
        ttk.Button(button_frame, text="Reset Error", command=self.on_reset_error).grid(side=tk.TOP, fill=tk.X)

        # TS on/off Button and Status
        ttk.Button(button_frame, text="TS on/off", command=self.on_ts_toggle).grid(row=0, column=0, padx=5, pady=5,
                                                                                   sticky="ew")
        # Reset Error Button and Status
        ttk.Button(button_frame, text="Reset error", command=self.on_reset_error).grid(row=0, column=2, padx=5, pady=5,
                                                                                       sticky="ew")
        self.error_status = tk.Canvas(button_frame, width=20, height=20)
        self.error_status.grid(row=0, column=3)
        self.error_status.create_oval(2, 2, 18, 18, fill='red')  # Change to 'green' if error is reset

        # Additional buttons and indicators follow the same pattern...

        # Text Widget for displaying log/console output
        log_frame = tk.Frame(main_frame, relief=tk.SUNKEN, borderwidth=1)
        log_frame.grid(row=0, column=1, sticky="nsew")

        self.log_text = tk.Text(log_frame, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # Configure the grid weights so the log_frame expands to fill the space
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)

    def on_reset_error(self):
        print("Reset Error clicked")
        # Code to handle error reset

    def on_details(self):
        # Code to handle Details - Opens a new window for slave detailed view
        details_window = tk.Toplevel(self)
        details_window.title("Slave Detailed View")
        tk.Label(details_window, text="Slave Details Here").pack(padx=20, pady=20)


if __name__ == '__main__':
    app = BatteryGUI()
    app.mainloop()
