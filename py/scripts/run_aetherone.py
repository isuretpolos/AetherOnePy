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
        os.chdir(repo_dir / "py")
        subprocess.run(["git", "pull"])
        subprocess.run([sys.executable, "setup.py"])
    else:
        # Clone the repository if it doesn't exist
        print(f"Directory {repo_dir} does not exist. Cloning repository...")
        base_dir.mkdir(parents=True, exist_ok=True)
        os.chdir(base_dir)
        subprocess.run(["git", "clone", "https://github.com/isuretpolos/AetherOnePy.git"])
        os.chdir(repo_dir / "py")
        subprocess.run([sys.executable, "setup.py"])

    # Navigate to the repository's py directory and run the application
    os.chdir(repo_dir / "py")
    print("Starting application...")
    subprocess.run([sys.executable, "main.py", "--port", "7000"])

if __name__ == "__main__":
    main()
