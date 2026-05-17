import typer
import webbrowser
import os
import time

from ai_gitreviewer.__main__ import run_and_report, get_project_context, IGNORE_DIRS
from ai_gitreviewer.core.git_utils import get_git_diff, parse_diff, generate_project_tree
from ai_gitreviewer.core.analyzer import ReviewerEngine
from ai_gitreviewer.core.reporter import HTMLReporter

app = typer.Typer(help="AI-GitReviewer CLI: Your local Llama-3 Code Auditor")

@app.command()
def status():
    """Check the connection to the Groq cloud backend."""
    engine = ReviewerEngine(use_ai=True)
    try:
        # Probe Groq by listing available models
        engine.nlp_engine.client.models.list()
        typer.secho("✅ Connected to Groq API successfully.", fg=typer.colors.GREEN)
        typer.echo(f"   Model in use: {engine.nlp_engine.llama_model}")
    except Exception as e:
        typer.secho(f"❌ Connection failed: {str(e)}", fg=typer.colors.RED)
        typer.echo("   Check that GROQ_API_KEY is correctly set in your project.env")

@app.command()
def review():
    """Run review on STAGED changes only, organized by file."""
    typer.echo("🔍 Fetching staged git diff...")
    raw_diff = get_git_diff()
    
    if not raw_diff or not raw_diff.strip():
        typer.secho("✅ No staged changes detected. Stage some files first!", fg=typer.colors.YELLOW)
        return

    # 1. Prepare Global Context
    root = os.getcwd()
    project_context = get_project_context(root)
    # Passed IGNORE_DIRS correctly here
    tree_map = generate_project_tree(root, IGNORE_DIRS)
    
    # 2. Parse the diff
    changed_files = parse_diff(raw_diff)
    engine = ReviewerEngine(use_ai=True)
    all_results = {}

    # 3. Analyze Architecture (Local Llama-3 call)
    typer.echo("🏗️  Analyzing project architecture with Llama-3...")
    arch_feedback = engine.analyze_architecture(tree_map, project_context)
    time.sleep(2)

    # 4. Analyze each file individually
    for filename, content in changed_files.items():
        typer.echo(f"🔍 Analyzing {filename}...")
        issues = engine.analyze_content(content, filename=filename, project_context=arch_feedback)
        time.sleep(1.5)
        if issues:
            all_results[filename] = issues
    
    # 5. Generate the Report
    if all_results or arch_feedback:
        output_dir = os.path.join(os.path.expanduser("~"), ".ai-gitreviewer", "reports")
        os.makedirs(output_dir, exist_ok=True)
        report_file = os.path.join(output_dir, "staged_report.html")
        reporter = HTMLReporter(all_results, arch_feedback=arch_feedback, output_file=report_file)
        reporter.generate()

        report_path = os.path.abspath(report_file)
        webbrowser.open(f"file://{report_path}")
        typer.secho(f"\n🚀 Staged report ready: {report_path}", fg=typer.colors.CYAN, bold=True)
    else:
        typer.secho("🎉 No issues found in staged changes.", fg=typer.colors.GREEN)

@app.command()
def full_scan(directory: str = "."):
    """Run a full repository scan using the master logic in __main__."""
    report_path = run_and_report(directory)
    if report_path:
        webbrowser.open(f"file://{report_path}")

@app.command()
def version():
    typer.echo("AI-GitReviewer v1.0.0 (Local Llama-3 Edition)")

if __name__ == "__main__":
    app()