#!/bin/bash

# Define variables
BASE_DIR="aetherone"
REPO_DIR="$BASE_DIR/AetherOnePy"

# Create and activate the virtual environment if it doesn't already exist
if [ ! -d "$BASE_DIR" ]; then
python3 -m venv "$BASE_DIR"
fi

source "$BASE_DIR/bin/activate"

# Check if the repository exists
if [ -d "$REPO_DIR" ]; then
# If the repository exists, navigate to it and pull the latest changes
echo "Directory $REPO_DIR exists. Updating repository..."
cd "$REPO_DIR/py"
git pull
python3 setup.py
else
# Clone the repository if it doesn't exist
echo "Directory $REPO_DIR does not exist. Cloning repository..."
mkdir -p "$BASE_DIR"
cd "$BASE_DIR"
git clone https://github.com/isuretpolos/AetherOnePy.git
cd AetherOnePy/py
python3 setup.py
fi

# Navigate to the repository's py directory and run the application
cd "$REPO_DIR/py"
echo "Starting application..."
python3 main.py --port 7000
