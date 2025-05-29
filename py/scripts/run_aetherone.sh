#!/bin/bash

# Define variables
BASE_DIR="aetherone"
REPO_DIR="$BASE_DIR/AetherOnePy"
MAX_WAIT=60  # max seconds to wait for network
WAIT_INTERVAL=3

# Wait until either LAN or Wi-Fi is up (has IP address)
echo "Waiting for any network connection (LAN or Wi-Fi)..."
elapsed=0
while ! ip addr | grep -q "inet .*brd"; do
  if [ $elapsed -ge $MAX_WAIT ]; then
    echo "No network connection after $MAX_WAIT seconds. Exiting."
    exit 1
  fi
  echo "Still waiting... ($elapsed/$MAX_WAIT)"
  sleep $WAIT_INTERVAL
  elapsed=$((elapsed + WAIT_INTERVAL))
done
echo "Network is available. Continuing..."

# Kill all existing AetherOne processes
pkill -f aetherone

# Create and activate the virtual environment if it doesn't already exist
if [ ! -d "$BASE_DIR" ]; then
  python3 -m venv "$BASE_DIR"
fi

source "$BASE_DIR/bin/activate"

# Check if the repository exists
if [ -d "$REPO_DIR" ]; then
  echo "Directory $REPO_DIR exists. Updating repository..."
  cd "$REPO_DIR/py"
  git pull
  python3 setup.py
else
  echo "Directory $REPO_DIR does not exist. Cloning repository..."
  mkdir -p "$BASE_DIR"
  cd "$BASE_DIR"
  git clone https://github.com/isuretpolos/AetherOnePy.git
  cd AetherOnePy/py
  python3 setup.py
fi

cd "$REPO_DIR/py"
echo "Starting application..."
python3 main.py --port 7000
