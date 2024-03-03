import tkinter as tk
from tkinter import ttk, filedialog
import serial.tools.list_ports
import serial
import threading
import datetime
import csv
from logger import main as log_main
from open_details_window import open_details_window
from open_temperature_details_window import open_temperature_details_window
from serial_interface import SerialInterface


class BatteryTab:

    def __init__(self, master):
        self.master = master
        self.frame = ttk.Frame(self.master)
        self.setup_widgets()
        self.build_device_selector()
        self.serial_port = None
        self.ts_on_status = False
        self.is_battery_connected = False
        self.battery_online_status = False
        self.message_buffer = []
        self.buffer_lock = threading.Lock()
        self.update_interval = 1000  # Milliseconds to wait before updating the GUI
        self.last_update_time = 0
        self.update_gui()
        self.clear_requested = False
        self.details_window_open = False
        self.temperature_details_window_open = False
        self.serial_interface = SerialInterface(
            port="COM4",
            baudrate=115200,
            update_callback=self.update_values,
            clear_messages_callback=self.clear_messages,
            display_message_callback=self.display_message
        )
        self.latest_parsed_data = {}

    def handle_new_data(self, data):
        # Handle new data received from SerialInterface
        with self.buffer_lock:
            self.message_buffer.append(data)
        self.display_message(data)

    def clear_messages(self):
        # Clear messages logic
        self.messages_text.config(state='normal')
        self.messages_text.delete('1.0', tk.END)
        self.messages_text.config(state='disabled')
        # Reset buffer
        with self.buffer_lock:
            self.message_buffer.clear()

    def update_values(self, parsed_data):
        # Update the values from the parsed data
        self.update_charge_values(parsed_data)
        self.update_energy_values(parsed_data)
        self.update_cell_voltages(parsed_data)
        self.update_cell_temperatures(parsed_data)
        self.update_ivt_values(parsed_data)
        self.update_indicators(parsed_data)
        self.is_battery_connected = parsed_data.get('battery_voltage', 0) > 0
        self.latest_parsed_data = parsed_data

    def update_charge_values(self, parsed_data):
        soc = parsed_data.get('soc', 0) or 0
        voltage = parsed_data.get('battery_voltage', 0) or 0
        current = parsed_data.get('battery_current', 0) or 0
        bms_flags = parsed_data.get('bms_flags', '') or ''
        max_voltage = 597.6
        voltage_percentage = (voltage / max_voltage) * 100 if max_voltage else 0

        self.soc_progress['value'] = soc
        self.soc_value_label.config(text=f"{soc}%")
        self.voltage_progress['value'] = voltage_percentage
        self.voltage_value_label.config(text=f"{voltage:.2f} V")
        self.current_value_label.config(text=f"{current:.2f} A")
        self.bms_flag_value.config(text=bms_flags)

    def update_energy_values(self, parsed_data):
        # Update the Labels with actual values if the battery is connected, otherwise show "-"
        voltage = parsed_data.get('battery_voltage', 0) or 0
        current = abs(parsed_data.get('battery_current', 0))  # This line is causing the error
        rate = voltage * current / 1000
        bad_thermistor = parsed_data.get('bad_thermistor', 0) or 0
        bad_cell = parsed_data.get('bad_cell', 0) or 0
        self.rate_value.config(text=f"{rate:.2f} kW" if self.is_battery_connected else "-")
        self.bad_thermistor_value.config(text=f"{bad_thermistor}" if self.is_battery_connected else "-")
        self.bad_cell_value.config(text=f"{bad_cell}" if self.is_battery_connected else "-")

    def update_cell_voltages(self, parsed_data):
        # Update the Labels with actual values if the battery is connected, otherwise show "-"
        highest = parsed_data.get('max_voltage', 0) or 0
        lowest = parsed_data.get('min_voltage', 0) or 0
        voltages = parsed_data.get('voltages', {})

        all_voltages = []
        for slave_id, voltage_list in voltages.items():
            all_voltages.extend(voltage_list)

        # Check if there are any voltage readings
        if all_voltages:
            total_voltage = sum(all_voltages)
            count = len(all_voltages)
            average = total_voltage / count if count > 0 else '-'
        else:
            average = '-'

        # Update the GUI components
        self.highest_voltage_value.config(text=f"{highest} V" if highest != '-' else "-")
        self.average_voltage_value.config(text=f"{average:.2f} V" if average != '-' else "-")
        self.lowest_voltage_value.config(text=f"{lowest} V" if lowest != '-' else "-")

    def update_cell_temperatures(self, parsed_data):
        # Calculate the highest, lowest, and average temperatures
        temperatures = parsed_data.get('temperatures', {})
        all_temps = [t for sublist in temperatures.values() for t in sublist if t is not None]
        highest_temp = max(all_temps, default='-')
        lowest_temp = min(all_temps, default='-')
        average_temp = sum(all_temps, 0.0) / len(all_temps) if parsed_data['temperatures'] else '-'
        # Update the Labels with actual values if the battery is connected, otherwise show "-"
        self.highest_temp_value.config(text=f"{highest_temp} °C" if self.is_battery_connected else "-")
        self.average_temp_value.config(text=f"{average_temp:.2f} °C" if self.is_battery_connected else "-")
        self.lowest_temp_value.config(text=f"{lowest_temp} °C" if self.is_battery_connected else "-")

    def update_ivt_values(self, parsed_data):
        # Update the IVT values from the parsed data

        # IVT Voltage
        ivt_voltage = parsed_data.get('ivt_voltage')
        if ivt_voltage is not None:
            self.ivt_voltage_value.config(text=f"{ivt_voltage} V")

        # IVT Current
        ivt_current = parsed_data.get('ivt_current')
        if ivt_current is not None:
            self.ivt_current_value.config(text=f"{ivt_current} A")

        # IVT Current Counter
        ivt_current_counter = parsed_data.get('ivt_current_counter')
        if ivt_current_counter is not None:
            self.ivt_current_counter_value.config(text=f"{ivt_current_counter} Ah")

    def update_indicators(self, parsed_data):
        charging_status = parsed_data.get('charging_status', 0)
        # print("charging_status:", charging_status)
        battery_voltage = parsed_data.get('battery_voltage', 0)
        serial_connection_established = (self.serial_interface.serial_connection is not None and
                                         self.serial_interface.serial_connection.is_open)

        # Logic to determine the color of the battery charging indicator
        if not serial_connection_established:
            # print("case 1:", serial_connection_established, charging_status)
            bcharge_color = 'red'  # Turn red immediately when the connection is closed'''
        elif charging_status == 0:
            # print("case 2:", charging_status)
            bcharge_color = 'red'
        elif charging_status == 1:
            # print("case 3:", charging_status)
            bcharge_color = '#06b025'  # Green when charging
        else:
            bcharge_color = 'grey'
            # print("case 4: inside")

        # Logic to determine the color of the battery online indicator
        battery_online_color = 'red' if not serial_connection_established else ('#06b025' if battery_voltage > 0 else 'grey')

        # Logic to determine the color of the TS on indicator
        ts_on_color = '#06b025' if serial_connection_established else 'red'

        # Apply the determined colors to the canvas items
        self.bcharge_canvas.itemconfig(self.bcharge_indicator, fill=bcharge_color)
        self.battery_online_canvas.itemconfig(self.battery_online_indicator, fill=battery_online_color)
        self.ts_on_canvas.itemconfig(self.ts_on_indicator, fill=ts_on_color)

        # Schedule the next update, ensuring parsed_data is updated if needed
        self.master.after(1000, lambda: self.update_indicators(self.latest_parsed_data))

    def build_device_selector(self):
        # Create device selection frame and other widgets
        device_frame = ttk.LabelFrame(self.frame, text='Device Selection')
        device_frame.grid(row=3, column=0, padx=5, pady=5, sticky='ew')

        # Combobox to list available serial ports
        self.device_combobox = ttk.Combobox(device_frame)
        self.device_combobox.grid(row=0, column=0, padx=5, pady=5, sticky='ew')

        # Button to refresh the list of available serial ports
        refresh_button = ttk.Button(device_frame, text="Refresh", command=self.refresh_serial_ports)
        refresh_button.grid(row=0, column=1, padx=5, pady=5)

        # Button to open the selected serial port
        open_button = ttk.Button(device_frame, text="Open", command=self.open_port)
        open_button.grid(row=0, column=2, padx=5, pady=5)

        # Button to close the selected serial port
        close_button = ttk.Button(device_frame, text="Close", command=self.close_port)
        close_button.grid(row=0, column=3, padx=5, pady=5)

        # Button to extract log from the serial port
        extract_log_button = ttk.Button(device_frame, text="Extract Log", command=self.extract_log)
        extract_log_button.grid(row=0, column=4, padx=5, pady=5)

        # Initially refresh the serial ports list
        self.refresh_serial_ports()

    def refresh_serial_ports(self):
        # Refresh the list of serial ports
        ports = serial.tools.list_ports.comports()
        self.device_combobox['values'] = [port.device for port in ports if 'USB' in port.description]

    def open_port(self):
        selected_port = self.device_combobox.get()
        self.serial_interface.open_serial_port(selected_port)

    def close_port(self):
        if self.serial_interface:
            self.serial_interface.close_serial_port()

    def update_gui(self):
        now = datetime.datetime.now().timestamp() * 1000
        if now - self.last_update_time >= self.update_interval:
            with self.buffer_lock:
                if self.message_buffer:
                    messages_to_display = "\n".join(self.message_buffer)
                    self.message_buffer.clear()
                    self.display_message(messages_to_display)
                    self.last_update_time = now
        # Reschedule the update
        self.master.after(500, self.update_gui)

    def extract_log(self):
        # Open file dialog to select save location
        filename = filedialog.asksaveasfilename(defaultextension=".log",
                                                filetypes=[("Log files", "*.log"), ("All files", "*.*")])
        if not filename:
            return  # The user cancelled the operation

        # Get all the text from the Text widget
        log_contents = self.messages_text.get('1.0', tk.END)

        # Write the stored messages to the CSV file
        with open(filename, 'w', newline='') as csvfile:
            log_writer = csv.writer(csvfile)
            for message in log_contents.splitlines():
                log_writer.writerow([message])

    def open_details_window(self, use_default_values=False):
        if not self.details_window_open:
            self.details_window_open = True

            def on_close():
                self.details_window_open = False

            if use_default_values:
                voltages = {key: 0.0 for key in self.latest_parsed_data.get('voltages', {})}
            else:
                voltages = self.latest_parsed_data.get('voltages', {})

            open_details_window(self.master, voltages,
                                update_callback=lambda: self.latest_parsed_data.get('voltages', {}),
                                on_close_callback=on_close)

    def open_temperature_details_window(self, use_default_values=False):
        if not self.temperature_details_window_open:
            self.temperature_details_window_open = True

            def on_close():
                self.temperature_details_window_open = False

            if use_default_values:
                temperatures = {key: 0.0 for key in self.latest_parsed_data.get('temperatures', {})}
            else:
                temperatures = self.latest_parsed_data.get('temperatures', {})
            print(temperatures)
            open_temperature_details_window(self.master, temperatures, update_callback=lambda: self.latest_parsed_data.get('temperatures', {}), on_close_callback=on_close)

    def apply_baudrate(self):
        # Get the selected baud rate from the Combobox
        selected_baudrate = self.baudrate_combobox.get()
        # Change the baud rate of the serial interface
        self.serial_interface.change_baudrate(int(selected_baudrate))

    def display_message(self, message):
        # Logic to display a message in the GUI
        self.messages_text.config(state='normal')
        self.messages_text.insert('1.0', message + '\n')  # Insert new message at the top
        self.messages_text.config(state='disabled')
        self.messages_text.see('1.0')

    '''def save_log_on_close(self):
        # Ensure the 'log' directory exists
        log_dir = 'log'
        os.makedirs(log_dir, exist_ok=True)

        # Construct the CSV file name with timestamp
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_name = os.path.join(log_dir, f"{timestamp}.csv")

        # Extract messages from the buffer and parse them
        with self.buffer_lock:
            messages_to_parse = list(self.message_buffer)  # Make a copy to safely iterate
        parsed_data = [self.parse_message(message) for message in messages_to_parse]

        # Write the parsed data to the CSV file
        with open(file_name, 'w', newline='') as csvfile:
            log_writer = csv.writer(csvfile)
            for data in parsed_data:
                log_writer.writerow(data)

        print(f"Data saved to {file_name}")'''

    def close_application(self):
        print("inside close")
        # Retrieve contents of messages_text
        log_contents = self.messages_text.get('1.0', 'end-1c')  # Gets all text from the widget
        # Call the logger's main function with the retrieved contents
        log_main(log_contents)
        # Proceed to quit the application
        self.master.quit()

    def setup_widgets(self):
        # Segment the layout into sections using frames
        # skipped for simplicity
        charge_frame = ttk.LabelFrame(self.frame, text='Charge')
        energy_frame = ttk.LabelFrame(self.frame, text='General')
        cell_voltages = ttk.LabelFrame(self.frame, text='Cell Voltages')
        cell_temperatures = ttk.LabelFrame(self.frame, text='Cell Temperatures')
        ivt_data = ttk.LabelFrame(self.frame, text='IVT Data')

        # ... (create frames for each section)
        self.frame.pack(fill="both", expand=True)

        # Console section
        self.console_frame = ttk.LabelFrame(self.frame, text='Console')
        self.console_frame.grid(row=0, column=0, columnspan=2, sticky='ew', padx=5, pady=5)

        # Add widgets to the console frame
        ts_on_off_button = ttk.Button(self.console_frame, text="TS on/off")
        ts_on_off_button.grid(row=0, column=0, padx=5, pady=5, sticky='ew')

        reset_error_button = ttk.Button(self.console_frame, text="Reset error")
        reset_error_button.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        self.details_button = ttk.Button(self.console_frame, text="Voltages Details", command=self.open_details_window)
        self.details_button.grid(row=0, column=2, padx=5, pady=5, sticky='ew')

        # Add the "Temperature Details" button
        self.temperature_details_button = ttk.Button(self.console_frame, text="Temperature Details",
                                                      command=lambda: self.open_temperature_details_window())
        self.temperature_details_button.grid(row=0, column=3, padx=5, pady=5, sticky='ew')

        # Setup for Battery Online indicator
        battery_online_label = ttk.Label(self.console_frame, text="Battery online:")
        battery_online_label.grid(row=2, column=2, padx=5, pady=5)

        self.battery_online_canvas = tk.Canvas(self.console_frame, width=20, height=20)
        self.battery_online_canvas.grid(row=2, column=3, padx=5, pady=5)
        self.battery_online_indicator = self.battery_online_canvas.create_oval(5, 5, 15, 15, fill='grey')

        # Setup for TS on indicator
        ts_on_label = ttk.Label(self.console_frame, text="Serial Connection:")
        ts_on_label.grid(row=2, column=0, padx=5, pady=5)

        self.ts_on_canvas = tk.Canvas(self.console_frame, width=20, height=20)
        self.ts_on_canvas.grid(row=2, column=1, padx=5, pady=5)
        self.ts_on_indicator = self.ts_on_canvas.create_oval(5, 5, 15, 15, fill='grey')

        # Setup for battery charging indicator
        bcharge_label = ttk.Label(self.console_frame, text="Battery Charging:")
        bcharge_label.grid(row=2, column=4, padx=5, pady=5)

        self.bcharge_canvas = tk.Canvas(self.console_frame, width=20, height=20)
        self.bcharge_canvas.grid(row=2, column=5, padx=5, pady=5)
        self.bcharge_indicator = self.bcharge_canvas.create_oval(5, 5, 15, 15, fill='grey')

        # Charge section
        # (create charge_frame and add widgets similarly)
        charge_frame = ttk.LabelFrame(self.frame, text='Charge')
        charge_frame.grid(row=0, column=2, sticky='ew', padx=5, pady=5)

        # SOC as a progress bar
        ttk.Label(charge_frame, text="SOC:").grid(row=0, column=0, sticky='w')
        self.soc_progress = ttk.Progressbar(charge_frame, orient='horizontal', mode='determinate', length=200)
        self.soc_progress.grid(row=0, column=1, sticky='ew', padx=5)
        self.soc_value_label = ttk.Label(charge_frame, text="0%")
        self.soc_value_label.place(in_=self.soc_progress, relx=0.5, rely=0.5, anchor='center')

        # Voltage as a progress bar
        ttk.Label(charge_frame, text="Voltage:").grid(row=1, column=0, sticky='w')
        self.voltage_progress = ttk.Progressbar(charge_frame, orient='horizontal', mode='determinate', length=200)
        self.voltage_progress.grid(row=1, column=1, sticky='ew', padx=5)
        self.voltage_value_label = ttk.Label(charge_frame, text="0V")
        self.voltage_value_label.place(in_=self.voltage_progress, relx=0.5, rely=0.5, anchor='center')

        # Current as a fixed value, displayed in a label
        ttk.Label(charge_frame, text="Current:").grid(row=2, column=0, sticky='w')
        self.current_value_label = ttk.Label(charge_frame,
                                             text="0 A")  # Initialized with 0 A, will be updated with CAN data
        self.current_value_label.grid(row=2, column=1, sticky='ew', padx=5)

        ttk.Label(charge_frame, text="BMS Flags:").grid(row=3, column=0, sticky='w')
        self.bms_flag_value = ttk.Label(charge_frame, text="0000000000000000")  # Changed to Label to display text
        self.bms_flag_value.grid(row=3, column=1, sticky='ew')

        # Energy section
        energy_frame = ttk.LabelFrame(self.frame, text='General')
        energy_frame.grid(row=0, column=3, sticky='ew', padx=5, pady=5)

        ttk.Label(energy_frame, text="Rate:").grid(row=0, column=0, sticky='w')
        self.rate_value = ttk.Label(energy_frame, text="-")  # Changed to Label to display text
        self.rate_value.grid(row=0, column=1, sticky='ew')

        ttk.Label(energy_frame, text="Bad Cell:").grid(row=1, column=0, sticky='w')
        self.bad_cell_value = ttk.Label(energy_frame, text="-")  # Changed to Label to display text
        self.bad_cell_value.grid(row=1, column=1, sticky='ew')


        ttk.Label(energy_frame, text="Bad Thermistor:").grid(row=2, column=0, sticky='w')
        self.bad_thermistor_value = ttk.Label(energy_frame, text="-")  # Changed to Label to display text
        self.bad_thermistor_value.grid(row=2, column=1, sticky='ew')

        # Cell Voltages section
        cell_voltages_frame = ttk.LabelFrame(self.frame, text='Cell Voltages')
        cell_voltages_frame.grid(row=0, column=4, sticky='ew', padx=5, pady=5)

        ttk.Label(cell_voltages_frame, text="Highest:").grid(row=0, column=0, sticky='w')
        self.highest_voltage_value = ttk.Label(cell_voltages_frame, text="-")
        self.highest_voltage_value.grid(row=0, column=1, sticky='ew')

        ttk.Label(cell_voltages_frame, text="Average:").grid(row=1, column=0, sticky='w')
        self.average_voltage_value = ttk.Label(cell_voltages_frame, text="-")
        self.average_voltage_value.grid(row=1, column=1, sticky='ew')

        ttk.Label(cell_voltages_frame, text="Lowest:").grid(row=2, column=0, sticky='w')
        self.lowest_voltage_value = ttk.Label(cell_voltages_frame, text="-")
        self.lowest_voltage_value.grid(row=2, column=1, sticky='ew')

        # Cell Temperatures section
        cell_temperatures_frame = ttk.LabelFrame(self.frame, text='Cell Temperatures')
        cell_temperatures_frame.grid(row=0, column=5, sticky='ew', padx=5, pady=5)

        ttk.Label(cell_temperatures_frame, text="Highest:").grid(row=0, column=0, sticky='w')
        self.highest_temp_value = ttk.Label(cell_temperatures_frame, text="-")
        self.highest_temp_value.grid(row=0, column=1, sticky='ew')

        ttk.Label(cell_temperatures_frame, text="Average:").grid(row=1, column=0, sticky='w')
        self.average_temp_value = ttk.Label(cell_temperatures_frame, text="-")
        self.average_temp_value.grid(row=1, column=1, sticky='ew')

        ttk.Label(cell_temperatures_frame, text="Lowest:").grid(row=2, column=0, sticky='w')
        self.lowest_temp_value = ttk.Label(cell_temperatures_frame, text="-")
        self.lowest_temp_value.grid(row=2, column=1, sticky='ew')

        # Slave Temperatures section is replaced with IVT Data section
        ivt_data_frame = ttk.LabelFrame(self.frame, text='IVT Data')
        ivt_data_frame.grid(row=0, column=6, sticky='ew', padx=5, pady=5)

        # IVT Voltage
        ttk.Label(ivt_data_frame, text="IVT Voltage:").grid(row=0, column=0, sticky='w')
        self.ivt_voltage_value = ttk.Label(ivt_data_frame, text="-")
        self.ivt_voltage_value.grid(row=0, column=1, sticky='ew')

        # IVT Current
        ttk.Label(ivt_data_frame, text="IVT Current:").grid(row=1, column=0, sticky='w')
        self.ivt_current_value = ttk.Label(ivt_data_frame, text="-")
        self.ivt_current_value.grid(row=1, column=1, sticky='ew')

        # IVT Current Counter
        ttk.Label(ivt_data_frame, text="IVT Current Counter:").grid(row=2, column=0, sticky='w')
        self.ivt_current_counter_value = ttk.Label(ivt_data_frame, text="-")
        self.ivt_current_counter_value.grid(row=2, column=1, sticky='ew')

        # Frame for received messages
        messages_frame = tk.LabelFrame(self.frame, text='Received messages')
        messages_frame.grid(row=2, column=0, columnspan=7, sticky='nsew', padx=5, pady=5)
        self.frame.grid_rowconfigure(2, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)

        # Text widget for displaying received messages
        self.messages_text = tk.Text(messages_frame, width=107, height=38, wrap='none')
        self.messages_text.grid(row=0, column=0, sticky='nsew')
        messages_frame.grid_rowconfigure(0, weight=1)
        messages_frame.grid_columnconfigure(0, weight=1)

        # Clear button placed below the text widget and spans two columns
        clear_button = ttk.Button(messages_frame, text="Clear", command=self.clear_messages)
        clear_button.grid(row=1, column=0, columnspan=2, sticky='ew', padx=5, pady=5)

        # Frame for target device selection
        device_frame = tk.LabelFrame(self.frame, text='Target device')
        device_frame.grid(row=3, column=0, columnspan=1, sticky='ew', padx=5, pady=5)

        # Scrollbar for the Text widget
        scrollbar = tk.Scrollbar(messages_frame, orient='vertical', command=self.messages_text.yview)
        scrollbar.grid(row=0, column=1, sticky='ns')
        self.messages_text.config(yscrollcommand=scrollbar.set)

        self.device_combobox = ttk.Combobox(device_frame, values=["/dev/ttyUSB0",
                                                                  "/dev/ttyUSB1"], state="readonly")
        self.device_combobox.grid(row=0, column=0, padx=5, pady=5)

        # Pack the main frame to fill the tab space
        self.frame.pack(fill='both', expand=True)

        # Create a frame for baud rate selection
        baudrate_frame = ttk.LabelFrame(self.frame, text='Baud Rate')
        baudrate_frame.grid(row=3, column=1, padx=5, pady=5, sticky='ew')

        # Create a label for the baud rate dropdown
        baudrate_label = ttk.Label(baudrate_frame, text="Baud Rate:")
        baudrate_label.grid(row=0, column=0, padx=5, pady=5, sticky='w')

        # Create a Combobox for baud rate selection
        self.baudrate_combobox = ttk.Combobox(baudrate_frame,
                                              values=["9600", "19200", "38400", "57600", "115200", "230400"],
                                              state="readonly")
        self.baudrate_combobox.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        self.baudrate_combobox.set("115200")  # Set the default baud rate

        # Create a button to apply the selected baud rate
        apply_baudrate_button = ttk.Button(baudrate_frame, text="Apply", command=self.apply_baudrate)
        apply_baudrate_button.grid(row=0, column=2, padx=5, pady=5)