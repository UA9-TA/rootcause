from rich.console import Console
from rich.panel import Panel
from rich.theme import Theme
from rich.syntax import Syntax

# Custom theme for consistent styling
custom_theme = Theme({
    "info": "dim cyan",
    "warning": "yellow",
    "danger": "bold red",
    "success": "bold green",
})

console = Console(theme=custom_theme)

def get_console() -> Console:
    """Returns the globally configured Rich console."""
    return console

def print_header() -> None:
    """Prints the application header."""
    console.print()
    console.print(" RootCause Analysis ", style="bold white on blue")
    console.print("──────────────────────────────────────────────────", style="dim")

def print_error(message: str) -> None:
    """Prints an error message."""
    console.print(f"[danger]Error:[/danger] {message}")

def print_analysis(analysis_data: dict) -> None:
    """Prints the final AI analysis beautifully."""
    # Confidence coloring
    confidence = analysis_data.get('confidence', 0)
    if confidence >= 80:
        conf_color = "green"
    elif confidence >= 60:
        conf_color = "yellow"
    else:
        conf_color = "red"

    conf_text = f"[{conf_color}]{confidence}%[/{conf_color}]"

    # Also found formatted list
    also_found = analysis_data.get("also_found", [])
    also_found_text = "\n                 ".join(also_found) if also_found else "None"

    # We construct a formatted view of the analysis
    console.print(f"✦ [bold]Root cause[/bold]     {analysis_data.get('root_cause')}")
    console.print(f"✦ [bold]Location[/bold]       [cyan]{analysis_data.get('location')}[/cyan]")

    # Handle long text block for explanation
    explanation = analysis_data.get("explanation", "")
    lines = explanation.split("\n")
    if lines:
        console.print(f"✦ [bold]Explanation[/bold]    {lines[0]}")
        for line in lines[1:]:
            console.print(f"                 {line}")

    # Fix formatting with syntax highlighting if needed
    fix_code = analysis_data.get("fix", "")
    fix_lines = fix_code.split("\n")
    if fix_lines:
        console.print(f"✦ [bold]Fix[/bold]            {fix_lines[0]}")
        for line in fix_lines[1:]:
            console.print(f"                 {line}")

    if also_found:
        console.print(f"✦ [bold]Also found[/bold]     {also_found_text}")

    console.print(f"✦ [bold]Confidence[/bold]     {conf_text}")
    console.print("──────────────────────────────────────────────────", style="dim")

def print_diff(diff_text: str) -> None:
    """Prints a diff nicely."""
    syntax = Syntax(diff_text, "diff", theme="monokai", line_numbers=False)
    console.print(Panel(syntax, title="Proposed Fix", expand=False))
