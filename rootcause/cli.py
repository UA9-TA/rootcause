import re
import time
from dataclasses import asdict
from pathlib import Path

import typer
from rich.prompt import Confirm

from . import config, display
from .analyzer import analyze_failure
from .context import gather_context
from .patcher import apply_fix
from .runner import FailureReport, parse_log_file, parse_raw_text, run_test_command

app = typer.Typer(
    name="rootcause", help="AI-powered root cause analysis for failing tests and errors"
)


def run_analysis_flow(report: FailureReport, auto_fix: bool = False):
    console = display.get_console()
    display.print_header()

    if report.exit_code == 0 and report.framework != "log":
        console.print("[success]Test passed! Nothing to analyze.[/success]")
        return

    with console.status("[bold cyan]Gathering context...[/bold cyan]", spinner="dots"):
        context = gather_context(report)
        time.sleep(0.3)

    with console.status("[bold cyan]Analyzing with AI...[/bold cyan]", spinner="dots"):
        try:
            analysis = analyze_failure(report, context)
        except Exception as e:
            display.print_error(str(e))
            raise typer.Exit(1)

    display.print_analysis(asdict(analysis))

    if analysis.fix_diff:
        if auto_fix:
            do_fix = True
        else:
            do_fix = Confirm.ask("Apply fix automatically?", default=False)

        if do_fix:
            success = apply_fix(analysis)
            if success:
                console.print("[success]Fix applied successfully![/success]")
            else:
                console.print("[danger]Failed to apply fix automatically.[/danger]")


@app.command()
def pytest(test_path: str, auto_fix: bool = typer.Option(False, "--auto-fix")):
    """Analyze a failing pytest test."""
    report = run_test_command(["pytest", test_path])
    run_analysis_flow(report, auto_fix)


@app.command()
def jest(test_path: str, auto_fix: bool = typer.Option(False, "--auto-fix")):
    """Analyze a failing jest or mocha test."""
    report = run_test_command(["npx", "jest", test_path])
    run_analysis_flow(report, auto_fix)


@app.command()
def mocha(test_path: str, auto_fix: bool = typer.Option(False, "--auto-fix")):
    """Analyze a failing mocha test."""
    report = run_test_command(["npx", "mocha", test_path])
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
    """Analyze the last error from your terminal history."""
    console = display.get_console()

    error_text = _read_last_error_from_history()
    if not error_text:
        console.print("[warning]No recent error found in shell history.[/warning]")
        console.print("Tip: pipe an error directly with: rootcause analyze error.log")
        raise typer.Exit(1)

    console.print(
        f"[dim]Found error block ({len(error_text.splitlines())} lines) from shell history[/dim]"
    )
    report = parse_raw_text(error_text, source="shell history")
    run_analysis_flow(report, auto_fix=False)


@app.command("config")
def config_key(api_key: str):
    """Set your Anthropic API key."""
    config.set_api_key(api_key)
    display.get_console().print("[success]API key saved to ~/.rootcause/config.toml[/success]")


def _read_last_error_from_history() -> str:
    """Read the most recent error-looking block from shell history."""
    # Try zsh history first, then bash
    candidates = [
        Path.home() / ".zsh_history",
        Path.home() / ".bash_history",
    ]

    error_keywords = re.compile(
        r"(Traceback|Error:|FAILED|AssertionError|Exception|stderr|exit code [1-9])", re.IGNORECASE
    )

    for history_file in candidates:
        if not history_file.exists():
            continue
        try:
            text = history_file.read_text(errors="replace")
            # zsh history lines start with ": timestamp:0;" — strip that
            lines = []
            for line in text.splitlines():
                if line.startswith(": ") and ";" in line:
                    line = line.split(";", 1)[-1]
                lines.append(line)

            # Walk backwards to find the last block containing error keywords
            for i in range(len(lines) - 1, max(0, len(lines) - 500), -1):
                if error_keywords.search(lines[i]):
                    # Grab a window around it
                    start = max(0, i - 20)
                    end = min(len(lines), i + 30)
                    return "\n".join(lines[start:end])
        except Exception:
            continue

    return ""


if __name__ == "__main__":
    app()
