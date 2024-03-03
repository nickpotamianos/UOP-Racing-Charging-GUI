import os
import re
import csv
from datetime import datetime


def parse_log_contents(log_contents):
    messages = log_contents.strip().split('-----------------------------\n')[::-1]
    all_combined_readings = []  # Store combined readings for all messages

    for message in messages:
        voltage_readings, temperature_readings = [], []

        # Split message to process voltage and temperature separately
        sections = message.split("Printing temperatures:")
        voltage_section = sections[0]
        temperature_section = sections[1] if len(sections) > 1 else ""

        # Extract voltage readings
        voltage_matches = re.findall(r"(-?\d+\.\d+-?)", voltage_section)
        voltage_readings = [v.strip('-') for v in voltage_matches]

        # Extract temperature readings, considering 'NaN' and numeric values
        temperature_matches = re.findall(r"NaN|\d+\.\d+", temperature_section)
        temperature_readings.extend(temperature_matches)

        combined_readings = voltage_readings[:144] + temperature_readings[:60]
        all_combined_readings.append(combined_readings)

    return all_combined_readings


def save_to_csv(data):
    directory = "logs"
    if not os.path.exists(directory):
        os.makedirs(directory)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{directory}/log_{timestamp}.csv"

    # Generate headers for cells and thermistors
    headers = [f"Cell #{i+1}" for i in range(144)] + [f"Therm #{i+1}" for i in range(60)]

    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(data)

    print(f"Data logged successfully to {filename}")


def main(log_contents):
    try:
        data = parse_log_contents(log_contents)
        save_to_csv(data)
        print("Log processing completed successfully.")
    except Exception as e:
        print(f"An error occurred during log processing: {e}")


# Example usage
if __name__ == "__main__":
    log_contents = """
    ... your log content here ...
    """
    main(log_contents)
