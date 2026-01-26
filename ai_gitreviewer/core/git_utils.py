import subprocess

def get_git_diff():
    """Fetches the staged diff from git."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--unified=0"], 
            capture_output=True, 
            text=True, 
            check=True
        )
        return result.stdout
    except Exception as e:
        return None