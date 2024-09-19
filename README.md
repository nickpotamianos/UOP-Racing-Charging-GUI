# UoP Racing CAN Interface

**Copyright (c) 2024 Nick Potamianos. All rights reserved.**

Permission is granted to use and distribute this software with attribution to the author and the UoP Racing Team, provided that this copyright notice and permission notice appear in all copies and derivatives. This software is provided 'as is' with no warranties, express or implied.

## Overview

The **UoP Racing CAN Interface** is a graphical user interface designed to monitor and log the status of a racing car’s battery management system (BMS). It is an integral tool for ensuring safety during charging of the car, providing real-time data acquisition from the CAN system via a Teensy microcontroller.

## Features

- **Console Section:**  
  Facilitates control over the system with buttons for viewing BMS flags and accessing detailed views for voltages and temperatures.

- **Indicator Lights:**  
  Provide status information about the serial connection, battery online status, and battery charging condition.

- **Received Messages Area:**  
  Displays timestamped voltage and temperature readings from the CAN interface, providing essential diagnostic information.

- **Panels:**
  - **Charge:**  
    Shows the state of charge (SOC), voltage, and current, along with a graphical representation of SOC.
  
  - **General:**  
    Displays the rate of energy consumption and indicates bad cells and thermistors if present.
  
  - **Cell Voltages:**  
    Provides the highest, average, and lowest cell voltages.
  
  - **Cell Temperatures:**  
    Shows the highest, average, and lowest cell temperatures.
  
  - **IVT Data:**  
    Lists voltage, current, and accumulated charge.

- **Device Selection:**  
  Enables the user to select, refresh, open, and close the COM port connection and extract logs.

- **Baud Rate Selection:**  
  Allows setting the communication rate for the serial interface.

## Detailed Views

### Voltage Details

Accessible via the "Voltage Details" button, the detailed voltage view offers in-depth insight into individual cell voltages across 12 slaves, each containing 12 cells. The application ensures that voltage levels are within safe operating limits.


### Temperature Details

The "Temperature Details" window, activated through a dedicated button, provides temperature readings from 12 slaves. It monitors temperatures to prevent thermal runaway conditions, ensuring the battery pack operates within safe temperature ranges.


### BMS Flags

When clicking on "BMS Flags," the application presents a separate window that outlines the status of various BMS conditions, encoded in a binary string and visually represented by red and green indicators. It alerts users to any abnormal conditions that may require attention.

## Logging Functionality

The application features robust logging capabilities. It can extract and save logs of the received data, enabling post-operation analysis and historical data review. This is crucial for troubleshooting and performance optimization. It also offers an automatic creation of a `logs` folder inside the application directory, where the context of the received messages window will be parsed, and only the temperatures and voltage values will be stored in a `.csv` file.

## Connectivity

The system establishes communication via a serial connection, with selectable COM ports and configurable baud rates (9600, 19200, 38400, 57600, 115200, 230400) to ensure compatibility with different hardware setups.

## Safety and Diagnostics

The application is equipped with numerous safety features, including:

- Real-time monitoring of battery voltage and temperature.
- Immediate display of BMS flags upon detection of anomalies.
- Logging functionality for post-race analysis and diagnostics.
- Automatic logging of the temperature and voltage values upon closing the application.

## Interface Design

The interface design is user-friendly, with logically organized data and control elements. It offers a balance between comprehensive data presentation and ease of use, which is vital for fast-paced racing environments.
