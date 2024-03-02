import threading
import serial
import time
import datetime


class SerialInterface:
    def __init__(self, port, baudrate, update_callback, clear_messages_callback, display_message_callback=None):
        self.port = port
        self.baudrate = baudrate
        self.update_callback = update_callback
        self.clear_messages_callback = clear_messages_callback
        self.display_message_callback = display_message_callback
        self.serial_connection = None  # Initialize the serial connection
        self.read_thread = None
        self.running = False  # Flag to control the thread
        self.reading_voltages = False  # Instance attribute for parsing flag
        self.reading_temperatures = False
        SerialInterface.change_baudrate = self.change_baudrate

    def open_serial_port(self, port):
        if port:
            try:
                self.serial_connection = serial.Serial(port=port, baudrate=self.baudrate, timeout=1)
                print(f"Opened serial port: {port}")
                self.running = True  # Set the running flag to True
                self.read_thread = threading.Thread(target=self.read_from_port, daemon=True)
                self.read_thread.start()
            except serial.SerialException as e:
                print(f"Error opening serial port: {e}")

    def read_from_port(self):
        print("inside read_from_port")
        message_buffer = []  # Buffer to hold lines of a block
        last_time_displayed = time.time() - 1  # Initialize to enable immediate first display
        complete_message_received = False

        while self.serial_connection and self.serial_connection.is_open:
            try:
                if time.time() - last_time_displayed >= 1 and not complete_message_received:
                    line = self.serial_connection.readline()
                    if line:
                        decoded_line = line.decode('utf-8').rstrip('\r\n')

                        # Check if we're at the start of a new message block
                        if 'Printing voltages:' in decoded_line:
                            # Detected the start of a new message, reset buffer and prepend with timestamped separator
                            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            separator = f"{timestamp} -----------------------------"
                            message_buffer = [separator, decoded_line]
                            complete_message_received = False  # Reset flag as we're starting a new message
                        elif 'Bad_Thermistor:' in decoded_line:
                            # Detected the end of a complete message
                            message_buffer.append(decoded_line)
                            complete_message_received = True
                        elif message_buffer:
                            # If we're in the middle of reading a message, continue appending lines
                            message_buffer.append(decoded_line)

                    if complete_message_received:
                        self.display_complete_message(message_buffer)
                        last_time_displayed = time.time()
                        message_buffer = []  # Clear the buffer for the next message
                        complete_message_received = False
                        time.sleep(1)  # Throttle the output to once per second

                else:
                    # If not enough time has passed, just sleep for a short duration to prevent busy waiting
                    time.sleep(0.1)  # Sleep to reduce CPU usage, adjust as needed

            except Exception as e:
                print(f"Error reading from port: {e}")
                continue

    def display_complete_message(self, message_lines):
        # Join the message lines into a single string
        complete_message_str = "\n".join(message_lines)
        # Display the complete message
        self.display_message_callback(complete_message_str)

        parsed_data = self.parse_data("\n".join(message_lines))
        # Update GUI with parsed data
        if self.update_callback:
            self.update_callback(parsed_data)

    '''def process_and_reset_block(self, message_block):
        formatted_message = "\n".join(message_block)
        if self.display_message_callback:
            self.display_message_callback(formatted_message)
        # Parse the block into structured data
        parsed_data = self.parse_data("\n".join(message_block))
        # Update GUI with parsed data
        if self.update_callback:
            self.update_callback(parsed_data)'''

    def parse_data(self, data):
        # Initial data structure
        parsed_data = {
            'voltages': {},
            'temperatures': {},
            'max_voltage': None,
            'min_voltage': None,
            'battery_voltage': None,
            'battery_current': None,
            'ivt_voltage': None,
            'ivt_current': None,
            'ivt_current_counter': None,
            'charging_status': None,
            'soc': None,
            'bms_flags': None,
            'bad_cell': None,
            'bad_thermistor': None
        }

        # Split the input data by lines
        lines = data.split('\n')

        # Parsing flags
        self.reading_voltages = False
        self.reading_temperatures = False

        for line in lines:
            if 'Printing voltages:' in line:
                self.reading_voltages = True
                self.reading_temperatures = False
                continue

            if 'Printing temperatures:' in line:
                self.reading_voltages = False
                self.reading_temperatures = True
                continue

            if self.reading_voltages and line.startswith('IC'):
                parts = line.split()
                slave_id = f"Slave {parts[1]}"  # IC number is used to generate the slave ID
                # Extract the cell voltages from the line, stripping any dashes and converting to float
                cell_voltages = []
                for v in parts[2:]:  # Start from the third element to skip 'IC' and its number
                    v = v.strip('-')  # Remove leading and trailing dashes if present
                    try:
                        voltage = float(v)
                        cell_voltages.append(voltage)
                    except ValueError:
                        print(f"Error: Unable to convert value '{v}' to float")
                parsed_data['voltages'][slave_id] = cell_voltages

            if self.reading_temperatures and line.startswith('IC'):
                parts = line.split()
                slave_id = f"Slave {parts[1]}"  # IC number is used to generate the slave ID
                # Extract the cell temperatures from the line, handling NaN and converting to float where possible
                cell_temperatures = []
                for t in parts[2:]:  # Start from the third element to skip 'IC' and its number
                    if t == 'NaN':  # Check if the temperature value is 'NaN'
                        cell_temperatures.append(None)  # Append None to indicate no data for this cell
                    else:
                        try:
                            temperature = float(t)
                            cell_temperatures.append(temperature)
                        except ValueError:
                            print(f"Error: Unable to convert value '{t}' to float")
                parsed_data['temperatures'][slave_id] = cell_temperatures

            elif 'Max Voltage:' in line:
               # Extract and parse max voltage
               self.reading_voltages = False
               self.reading_temperatures = False
               parsed_data['max_voltage'] = self.parse_float(line.split(':')[1])

            elif 'Min Voltage:' in line:
                # Extract and parse min voltage
                parsed_data['min_voltage'] = self.parse_float(line.split(':')[1])

            elif 'Printing voltages:' in line:
                reading_voltages = True

            elif 'Printing temperatures:' in line:
                reading_temperatures = True

            elif 'Battery Voltage:' in line:
                parsed_data['battery_voltage'] = self.parse_float(line.split(':')[1])

            elif 'Battery Current:' in line:
                parsed_data['battery_current'] = self.parse_float(line.split(':')[1])

            elif 'IVT Voltage:' in line:
                parsed_data['ivt_voltage'] = self.parse_float(line.split(':')[1])

            elif 'IVT Current:' in line:
                parsed_data['ivt_current'] = self.parse_float(line.split(':')[1])

            elif 'IVT Current Counter:' in line:
                parsed_data['ivt_current_counter'] = self.parse_float(line.split('Ah')[0].split(':')[1])
                parsed_data['charging_status'] = int(line.split('Status:')[1].split()[0])

            elif 'SOC:' in line:
                parsed_data['soc'] = int(line.split(':')[1].strip().split('%')[0])

            elif 'BMS_Flags:' in line:
                parsed_data['bms_flags'] = line.split(':')[1].strip()

            elif 'Bad_Cell:' in line:
                parsed_data['bad_cell'] = int(line.split(':')[1].strip())

            elif 'Bad_Thermistor:' in line:
                parsed_data['bad_thermistor'] = int(line.split(':')[1].strip())

        return parsed_data

    def parse_float(self, value):
        try:
            # Remove any trailing units like 'V' or 'A' before converting to float
            return float(value.strip('VA'))
        except ValueError:
            # Log an error or handle it as appropriate
            print(f"Error: Unable to convert value '{value}' to float")
            return None  # Or return a default value if that's preferred

    def change_baudrate(self, new_baudrate):
        # Check if the connection is open
        if self.serial_connection and self.serial_connection.is_open:
            # Close the current connection
            self.serial_connection.close()
            # Change the baudrate
            self.baudrate = new_baudrate
            # Re-open the serial connection with the new baudrate
            self.open_serial_port(self.port)
        else:
            # Just change the baudrate without opening the connection
            self.baudrate = new_baudrate
            print("Changed baudrate to {}, but the connection is not open.".format(new_baudrate))

    def close_serial_port(self):
        # Signal to the reading thread that it should stop
        self.running = False

        # Check if the serial connection was ever established
        if self.serial_connection:
            # Close the serial port if it's open
            if self.serial_connection.is_open:
                self.serial_connection.close()
                print("Serial port closed.")

            # Wait for the reading thread to finish if it's running
            if self.read_thread and self.read_thread.is_alive():
                self.read_thread.join(timeout=1)

            # After calling join, check if the thread is still alive
            if self.read_thread and self.read_thread.is_alive():
                print("Read thread did not terminate. It may be stuck in blocking I/O.")
        else:
            print("Serial connection was not established.")


