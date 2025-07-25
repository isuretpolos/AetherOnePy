import os
import subprocess
import sys
from pathlib import Path

def main():
    # Define paths
    base_dir = Path("aetherone").absolute()
    repo_dir = base_dir / "AetherOnePy"
    py_dir = repo_dir / "py"
    main_file = py_dir / "main.py"

    # Ensure the base directory and virtual environment exist
    if not base_dir.exists():
        print(f"Creating virtual environment in {base_dir}")
        subprocess.run([sys.executable, "-m", "venv", str(base_dir)])

    # Activate the virtual environment
    activate_script = base_dir / "bin" / "activate"
    if activate_script.exists():
        activate_command = f"source {activate_script}"
        subprocess.run(activate_command, shell=True, executable="/bin/bash")
    else:
        print(f"Warning: Virtual environment activation script {activate_script} not found. Proceeding without activation.")

    # Clone or update the repository
    if repo_dir.exists():
        print(f"Directory {repo_dir} exists. Updating repository...")
        os.chdir(repo_dir)
        subprocess.run(["git", "pull"])
    else:
        print(f"Directory {repo_dir} does not exist. Cloning repository...")
        base_dir.mkdir(parents=True, exist_ok=True)
        os.chdir(base_dir)
        subprocess.run(["git", "clone", "https://github.com/isuretpolos/AetherOnePy.git"])

    # Navigate to the py directory and verify main.py exists
    if py_dir.exists():
        print(f"Navigating to {py_dir}...")
        os.chdir(py_dir)

        # Run setup.py if it exists
        setup_file = py_dir / "setup.py"
        if setup_file.exists():
            print(f"Running {setup_file}...")
            subprocess.run([sys.executable, str(setup_file)])

        # Check for main.py and start the application
        # search for a free port, start with port 7000
        free_port = find_free_port()
        if main_file.exists():
            print(f"Starting application using {main_file}...")
            subprocess.run([sys.executable, str(main_file), "--port", str(free_port)])
        else:
            print(f"Error: main.py not found in {py_dir}. Check the repository structure.")
    else:
        print(f"Error: The 'py' directory does not exist in {repo_dir}. Check the repository structure.")

# Suche nach einem freien Port, beginnend mit Port 7000
def find_free_port(start_port=7000, max_port=7100):
    import socket
    for port in range(start_port, max_port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("", port))
                return port
            except OSError:
                continue
    raise RuntimeError("Not even a single free port found in the range between 7000 and 7100. Please check your firewall settings!")

if __name__ == "__main__":
    main()
