import subprocess
import re
import os

def get_git_diff():
    """Fetches the staged diff from git."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--unified=0"], 
            capture_output=True, 
            text=True, 
            check=True,
            encoding='utf-8'
        )
        return result.stdout
    except Exception as e:
        return None
    
def parse_diff(diff_text):
    """
    Parses a raw git diff and returns a dictionary:
    { "filename.py": "the changed lines only" }
    """
    files_data = {}
    # Split by the 'diff --git' header to isolate each file
    file_diffs = re.split(r'^diff --git ', diff_text, flags=re.MULTILINE)
    
    for file_diff in file_diffs:
        if not file_diff.strip():
            continue
            
        # Extract the filename (usually starts with 'b/')
        name_match = re.search(r'b/(.*?)\s', file_diff)
        if name_match:
            filename = name_match.group(1)
            # We only care about Python files
            if filename.endswith('.py'):
                # Extract only the lines that were added (starting with +)
                lines = file_diff.split('\n')
                added_content = "\n".join([
                    line[1:] for line in lines 
                    if line.startswith('+') and not line.startswith('+++')
                ])
                if added_content.strip():
                    files_data[filename] = added_content
                    
    return files_data

def generate_project_tree(root_dir, ignore_dirs=None):
    """Generates a clean, filtered directory tree for the AI."""
    tree = []
    # Combine system defaults with user-provided ignores
    system_ignores = {'.git', '__pycache__', 'venv', '.venv', '.vscode', '.idea', 'dist', 'build'}
    if ignore_dirs:
        system_ignores.update(ignore_dirs)
    
    # Use absolute path to avoid directory traversal issues
    root_dir = os.path.abspath(root_dir)
    
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in system_ignores and not d.startswith('.')]
        
        level = os.path.relpath(root, root_dir).count(os.sep)
        if level == 0 and os.path.basename(root) == '': # Handle root
            display_name = os.path.basename(root_dir)
        else:
            display_name = os.path.basename(root)
            
        indent = ' ' * 4 * level
        tree.append(f"{indent}📂 {display_name}/")
        
        sub_indent = ' ' * 4 * (level + 1)
        for f in files:
            if f.endswith(('.pyc', '.pyo', '.so', '.pkg')):
                continue
            tree.append(f"{sub_indent}📄 {f}")
    
    # Safety check for Llama 3 context limits
    tree_str = "\n".join(tree)
    if len(tree_str) > 8000:
        return tree_str[:8000] + "\n... [Tree truncated for context efficiency]"
    
    return tree_str