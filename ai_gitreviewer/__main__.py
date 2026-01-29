import os
import sys
from ai_gitreviewer.core.analyzer import ReviewerEngine

# Folders that should never be scanned (internal logic and environments)
IGNORE_DIRS = {"core", "tests", "venv", "__pycache__", ".git"}

# Specific files belonging to the tool's infrastructure
TOOL_INFRA_FILES = {"__main__.py", "cli.py", "__init__.py"}

def scan_entire_repo(directory="."):
    engine = ReviewerEngine()
    all_results = {}

    tool_dir_abs = os.path.dirname(os.path.abspath(__file__))

    print(f"Starting Repo Scan in: {os.path.abspath(directory)}")

    for root, dirs, files in os.walk(directory):
        # 1. Prune hidden directories in-place
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS and not d.startswith('.')]
        
        # 2. Skip the internal core/tests folders completely
        if any(folder in root for folder in IGNORE_DIRS):
            continue
        
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                file_path_abs = os.path.abspath(file_path)

                # 3. Check if this file is a tool internal file
                is_internal = (
                    file in TOOL_INFRA_FILES and 
                    os.path.commonpath([tool_dir_abs, file_path_abs]) == tool_dir_abs
                )
                
                if is_internal:
                    continue
                    
                with open(file_path, 'r') as f:
                    content = f.read()
                    issues = engine.analyze_content(content) 
                    if issues:
                        all_results[file_path] = issues
                        
    return all_results

if __name__ == "__main__":
    results = scan_entire_repo(".")
    
    if not results:
        print("No issues found in the repository.")
    else:
        print(f"\n Found issues in {len(results)} files:\n")
        for path, issues in results.items():
            print(f"File: {path}")
            for issue in issues:
                print(f"  - {issue}")
            print("-" * 40)