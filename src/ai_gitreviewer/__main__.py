import os, sys, time
try:
    from pathlib import Path
    from dotenv import load_dotenv
    load_dotenv("project.env")                        # project-level
    load_dotenv(Path.home() / ".ai-gitreviewer.env")  # global fallback
except ImportError:
    pass

os.environ["TOKENIZERS_PARALLELISM"] = "false"

from ai_gitreviewer.core.git_utils import generate_project_tree
from ai_gitreviewer.core.analyzer import ReviewerEngine
from ai_gitreviewer.core.reporter import HTMLReporter
from ai_gitreviewer.core.cache_manager import CacheManager

IGNORE_DIRS = {"venv", "__pycache__", ".git"}
TOOL_INFRA_FILES = {"__main__.py", "cli.py", "__init__.py"}

def get_project_context(repo_path):
    readme_path = os.path.join(repo_path, "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r") as f:
            return f.read(1500) 
    return "AI-GitReviewer: A hybrid structural and semantic code auditor."

def scan_entire_repo(directory="."):
    abs_directory = os.path.abspath(directory)
    project_context = get_project_context(abs_directory)
    
    # The Engine now initializes Llama 3 locally
    engine = ReviewerEngine()
    cache = CacheManager()
    all_results = {}
    tool_dir_abs = os.path.dirname(os.path.abspath(__file__))
    force_scan = "--force" in sys.argv

    print(f"🚀 Starting Local Repo Scan: {abs_directory}")
    print("💡 Note: The first file may take a moment while Llama 3 loads into RAM.")

    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS and not d.startswith('.')]
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                file_path_abs = os.path.abspath(file_path)

                if file in TOOL_INFRA_FILES and os.path.commonpath([tool_dir_abs, file_path_abs]) == tool_dir_abs:
                    continue
                    
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()

                if not force_scan and not cache.is_changed(file_path, content):
                    print(f"Skipping {file_path} (Unchanged)")
                    continue

                print(f"🔍 Analyzing {file_path}...")
                
                issues = engine.analyze_content(content, filename=file, project_context=project_context)
                
                if issues:
                    all_results[file_path] = issues
                
                cache.update(file_path, content)
                        
    return all_results

def run_and_report(directory="."):
    """The 'Master' function that runs the scan and makes the HTML file."""
    engine = ReviewerEngine(use_ai=True)
    project_context = get_project_context(directory)
    
    # 2. Architecture Analysis (Now powered by Llama 3)
    print("🏗️  Analyzing project architecture with Llama 3...")
    tree_str = generate_project_tree(directory, IGNORE_DIRS)
    arch_feedback = engine.analyze_architecture(tree_str, project_context)

    # 3. Run the file scan
    results = scan_entire_repo(directory)
    
    if not results and not arch_feedback:
        print("✅ No issues or architectural insights found.")
        return None
    
    # 4. Generate Report
    output_dir = os.path.join(os.path.expanduser("~"), ".ai-gitreviewer", "reports")
    os.makedirs(output_dir, exist_ok=True)
    report_filename = os.path.join(output_dir, "full_project_report.html")
    reporter = HTMLReporter(results, arch_feedback=arch_feedback, output_file=report_filename)
    reporter.generate()

    print(f"\n✨ Scan Complete!")
    print(f"📊 Report: {report_filename}")
    return report_filename

if __name__ == "__main__":
    run_and_report(".")