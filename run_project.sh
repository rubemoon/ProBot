#!/bin/bash

# Load the CH340 driver
echo "Loading CH340 driver..."
sudo modprobe ch341

# Check if the device is available
if ls /dev/ttyUSB* 1> /dev/null 2>&1; then
    echo "Device connected on: $(ls /dev/ttyUSB*)"
else
    echo "No USB device found. Make sure the Arduino is connected."
    exit 1
fi

# Run the Python script
echo "Starting the task manager..."
python3 scripts/task_manager.py

