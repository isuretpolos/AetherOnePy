import os
import subprocess
import sys
from pathlib import Path

def find_main_file(repo_path):
    """Search for the main.py file dynamically."""
    for root, _, files in os.walk(repo_path):
        if "main.py" in files:
            return Path(root) / "main.py"
    return None

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

    # Dynamically find the main.py file
    main_file_path = find_main_file(repo_dir)
    if main_file_path:
        main_dir = main_file_path.parent
        os.chdir(main_dir)
        print(f"Starting application from {main_file_path}...")
        subprocess.run([sys.executable, str(main_file_path), "--port", "7000"])
    else:
        print(f"Error: Could not find main.py in {repo_dir}. Please check the repository structure.")

if __name__ == "__main__":
    main()
