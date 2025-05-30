#!/bin/bash

# Configuration
BASE_DIR="$HOME/aetherone"
REPO_DIR="$BASE_DIR/AetherOnePy"
MAX_WAIT=60
WAIT_INTERVAL=3

# Wait until network is up (LAN or Wi-Fi)
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

# --- System Dependencies ---

echo "Checking system dependencies..."

required_packages=(python3 python3-pip git python3-gpiozero python3-lgpio)

for pkg in "${required_packages[@]}"; do
  if ! dpkg -s "$pkg" >/dev/null 2>&1; then
    echo "Installing missing package: $pkg"
    sudo apt install -y "$pkg"
  else
    echo "✓ $pkg already installed"
  fi
done

# Optional: pip dependencies (edit this as needed)
pip_packages=(flask flask_socketio flask-cors requests qrcode[pil] pygame pyperclip python-dateutil gitpython opencv-python matplotlib eventlet scipy openai)

echo "Installing/updating Python packages via pip..."
for pip_pkg in "${pip_packages[@]}"; do
  pip3 install --upgrade "$pip_pkg"
done

# --- AetherOnePy Repo Handling ---

if [ -d "$REPO_DIR" ]; then
  echo "Repository found. Pulling latest updates..."
  cd "$REPO_DIR/py"
  git pull
  python3 setup.py
else
  echo "Cloning AetherOnePy repository..."
  mkdir -p "$BASE_DIR"
  cd "$BASE_DIR"
  git clone https://github.com/isuretpolos/AetherOnePy.git
  cd AetherOnePy/py
  python3 setup.py
fi

# --- Start Application ---
cd "$REPO_DIR/py"
echo "Starting AetherOnePy..."
python3 main.py --port 7000
