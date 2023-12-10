#!/bin/bash

# Get the directory of the script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Set the directory for the virtual environment
VENV_DIR="$DIR/venv"

# Change to the script's directory
cd "$DIR"

# Check if the virtual environment directory exists
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating a new virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# Activate the virtual environment
source "$VENV_DIR/bin/activate"

# Checking and installing required packages
echo "Checking and installing required packages..."
pip install --upgrade pip
pip install pygame
pip install watchdog
pip install Pillow
pip install requests
pip install scikit-learn
pip install openai
pip install piexif

# Check if the last command was successful
if [ $? -ne 0 ]; then
    echo "Failed to install required dependencies. Exiting."
    exit 1
fi

# Launching main application
echo "Launching main application..."
python3 main.py

# Deactivate the virtual environment on completion
deactivate
