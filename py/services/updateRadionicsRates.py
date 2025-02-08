import os, sys
import git
from git.exc import GitCommandError

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))

async def update_or_clone_repo(target_dir, repo_url):
    # Check if the target directory exists
    if os.path.exists(target_dir):
        print(f"Repository exists at {target_dir}. Pulling the latest changes...")
        try:
            repo = git.Repo(target_dir)
            repo.git.pull('origin', 'master')
            print("Repository updated successfully!")
        except GitCommandError as e:
            print(f"Error while pulling changes: {e}")
    else:
        print(f"Cloning repository into {target_dir}...")
        try:
            git.Repo.clone_from(repo_url, target_dir)
            print("Repository cloned successfully!")
        except GitCommandError as e:
            print(f"Error while cloning repository: {e}")

if __name__ == "__main__":
    update_or_clone_repo(os.path.join(PROJECT_ROOT, "data", "radionics-rates"), 
                        "https://github.com/isuretpolos/radionics-rates.git")
