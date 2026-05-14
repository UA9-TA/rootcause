import typer
import time
from rich.prompt import Confirm
from dataclasses import asdict

from . import config
from . import display
from .runner import run_test_command, parse_log_file, FailureReport
from .context import gather_context
from .analyzer import analyze_failure
from .patcher import apply_fix

app = typer.Typer(
    name="rootcause",
    help="AI-powered root cause analysis for failing tests and errors"
)

def run_analysis_flow(report: FailureReport, auto_fix: bool = False):
    console = display.get_console()
    display.print_header()

    if report.exit_code == 0 and report.framework != "log":
        console.print("[success]Test passed! Nothing to analyze.[/success]")
        return

    with console.status("[bold cyan]Gathering context...[/bold cyan]", spinner="dots"):
        context = gather_context(report)
        time.sleep(0.5) # Slight delay for visual UX

    with console.status("[bold cyan]Analyzing with AI...[/bold cyan]", spinner="dots"):
        try:
            analysis = analyze_failure(report, context)
        except Exception as e:
            display.print_error(str(e))
            raise typer.Exit(1)

    # Print analysis
    display.print_analysis(asdict(analysis))

    # Auto fix
    if analysis.fix_diff:
        if auto_fix:
            do_fix = True
        else:
            do_fix = Confirm.ask("Apply fix automatically?", default=False)

        if do_fix:
            success = apply_fix(analysis)
            if success:
                console.print("[success]Fix applied successfully![/success]")
                # We could potentially re-run the test here
            else:
                console.print("[danger]Failed to apply fix automatically.[/danger]")

@app.command()
def pytest(test_path: str, auto_fix: bool = False):
    """Analyze a failing pytest test."""
    args = ["pytest", test_path]
    report = run_test_command(args)
    run_analysis_flow(report, auto_fix)

@app.command()
def jest(test_path: str, auto_fix: bool = False):
    """Analyze a failing jest test."""
    # Assuming jest is installed locally or via npx
    args = ["npx", "jest", test_path]
    report = run_test_command(args)
    run_analysis_flow(report, auto_fix)

@app.command()
def analyze(file: str):
    """Analyze a raw error log or traceback file."""
    try:
        report = parse_log_file(file)
        run_analysis_flow(report, auto_fix=False)
    except Exception as e:
        display.print_error(f"Failed to read or parse file: {e}")

@app.command()
def last():
    """Analyze the last error in terminal history."""
    display.get_console().print("[warning]The 'last' command relies on shell integrations that are not yet implemented in v1.[/warning]")
    raise typer.Exit(1)

@app.command("config")
def config_key(api_key: str):
    """Set your Anthropic API key."""
    config.set_api_key(api_key)
    display.get_console().print("[success]API key successfully configured![/success]")

if __name__ == "__main__":
    app()
