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

# Activate the virtual environment
echo "Activating the virtual environment..."
source venv/bin/activate

# Run the Python script with the correct path to the configuration file
echo "Starting the task manager..."
CONFIG_FILE="config/config.yaml"
if [ -f "$CONFIG_FILE" ]; then
    python3 scripts/task_manager.py --config "$CONFIG_FILE"
else
    echo "[ERROR] Failed to load configuration: No such file or directory: '$CONFIG_FILE'"
    deactivate
    exit 1
fi

# Deactivate the virtual environment
deactivate
    echo "[ERROR] Failed to load configuration: No such file or directory: '$CONFIG_FILE'"
    deactivate
    exit 1
fi

# Deactivate the virtual environment
deactivate