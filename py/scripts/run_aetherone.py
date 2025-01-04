import os
import subprocess
import sys
from pathlib import Path

def main():
    # Define variables
    base_dir = Path("aetherone")
    repo_dir = base_dir / "AetherOnePy"

    # Create and activate the virtual environment if it doesn't already exist
    if not base_dir.exists():
        print(f"Creating virtual environment in {base_dir}")
        subprocess.run([sys.executable, "-m", "venv", str(base_dir)])

    # Activate virtual environment
    activate_script = base_dir / "bin" / "activate_this.py"
    if activate_script.exists():
        with open(activate_script) as f:
            exec(f.read(), {'__file__': str(activate_script)})

    # Check if the repository exists
    if repo_dir.exists():
        # If the repository exists, navigate to it and pull the latest changes
        print(f"Directory {repo_dir} exists. Updating repository...")
        os.chdir(repo_dir)
        subprocess.run(["git", "pull"])
        py_dir = repo_dir / "py"
        if py_dir.exists():
            os.chdir(py_dir)
            subprocess.run([sys.executable, "setup.py"])
        else:
            print(f"Warning: The 'py' subdirectory does not exist in {repo_dir}")
    else:
        # Clone the repository if it doesn't exist
        print(f"Directory {repo_dir} does not exist. Cloning repository...")
        base_dir.mkdir(parents=True, exist_ok=True)
        os.chdir(base_dir)
        subprocess.run(["git", "clone", "https://github.com/isuretpolos/AetherOnePy.git"])
        py_dir = repo_dir / "py"
        if py_dir.exists():
            os.chdir(py_dir)
            subprocess.run([sys.executable, "setup.py"])
        else:
            print(f"Error: The 'py' subdirectory was not found after cloning {repo_dir}")
            return

    # Navigate to the repository's py directory and run the application
    if py_dir.exists():
        os.chdir(py_dir)
        print("Starting application...")
        subprocess.run([sys.executable, "main.py", "--port", "7000"])
    else:
        print(f"Error: The 'py' subdirectory does not exist, application cannot start.")

if __name__ == "__main__":
    main()
