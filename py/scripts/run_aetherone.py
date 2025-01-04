import os
import subprocess
import sys
from pathlib import Path

def main():
    # Define paths
    base_dir = Path("aetherone")
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
    print(py_dir)
    if py_dir.exists():
        print(f"Navigating to {py_dir}...")
        os.chdir(py_dir)

        # Run setup.py if it exists
        setup_file = py_dir / "setup.py"
        if setup_file.exists():
            print(f"Running {setup_file}...")
            subprocess.run([sys.executable, str(setup_file)])

        # Check for main.py and start the application
        if main_file.exists():
            print(f"Starting application using {main_file}...")
            subprocess.run([sys.executable, str(main_file), "--port", "7000"])
        else:
            print(f"Error: main.py not found in {py_dir}. Check the repository structure.")
    else:
        print(f"Error: The 'py' directory does not exist in {repo_dir}. Check the repository structure.")

if __name__ == "__main__":
    main()
