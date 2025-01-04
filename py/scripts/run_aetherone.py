import os
import subprocess
import sys
from pathlib import Path

def main():
    # Define variables
    base_dir = Path("aetherone")
    repo_dir = base_dir / "AetherOnePy"
    py_dir = repo_dir / "py"

    # Create and activate the virtual environment if it doesn't already exist
    if not base_dir.exists():
        print(f"Creating virtual environment in {base_dir}")
        subprocess.run([sys.executable, "-m", "venv", str(base_dir)])

    # Activate virtual environment
    activate_script = base_dir / "bin" / "activate_this.py"
    if activate_script.exists():
        with open(activate_script) as f:
            exec(f.read(), {'__file__': str(activate_script)})
    else:
        print(f"Warning: Could not find activation script {activate_script}")

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

    # Check if the py directory exists
    if py_dir.exists():
        os.chdir(py_dir)
        print(f"Running setup.py in {py_dir}...")
        subprocess.run([sys.executable, "setup.py"])

        # Start the application
        main_file = py_dir / "main.py"
        if main_file.exists():
            print(f"Starting application from {main_file}...")
            subprocess.run([sys.executable, str(main_file), "--port", "7000"])
        else:
            print(f"Error: main.py not found in {py_dir}")
    else:
        print(f"Error: The 'py' directory does not exist in {repo_dir}. Check the repository structure.")

if __name__ == "__main__":
    main()
