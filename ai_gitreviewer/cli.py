import typer
from ai_gitreviewer.core.git_utils import get_git_diff
from ai_gitreviewer.core.analyzer import ReviewerEngine

app = typer.Typer()

@app.command()
def review():
    """Run the Robust Code Reviewer on staged changes."""
    typer.echo("Fetching git diff...")
    
    raw_diff = get_git_diff()
    
    if raw_diff is None:
        typer.secho("ERROR: Could not fetch git diff.", fg=typer.colors.RED)
        return
    
    if not raw_diff.strip():
        typer.secho("No staged changes detected.", fg=typer.colors.YELLOW)
        return

    typer.echo("Analyzing code structure...")
    
    # Initialize and run the engine
    engine = ReviewerEngine()
    issues = engine.analyze_content(raw_diff)
    
    if issues:
        typer.secho(f"\nFound {len(issues)} issues:", fg=typer.colors.BRIGHT_RED, bold=True)
        for issue in issues:
            typer.echo(f"  {issue}")
    else:
        typer.secho("\n No structural issues found! Code looks clean.", fg=typer.colors.GREEN)

@app.command()
def version():
    """Show version."""
    typer.echo("AI-GitReviewer v0.1.0 (Robust Mode)")

if __name__ == "__main__":
    app()