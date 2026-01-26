import os
from ai_gitreviewer.core.analyzer import ReviewerEngine

def scan_entire_repo(directory="."):
    engine = ReviewerEngine()
    all_results = {}

    # This makes the tool "Dynamic" by walking through every folder
    for root, dirs, files in os.walk(directory):
        # Skip hidden folders like .git or venv
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    content = f.read()
                    # We treat the whole file as "added content"
                    issues = engine.analyze_content(content) 
                    if issues:
                        all_results[file_path] = issues
    return all_results