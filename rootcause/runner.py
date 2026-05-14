import subprocess
import time
from dataclasses import dataclass
import re
from typing import Optional, List, Dict, Any

@dataclass
class FailureReport:
    command: str
    exit_code: int
    stdout: str
    stderr: str
    runtime_seconds: float
    framework: str
    test_name: Optional[str] = None
    error_type: Optional[str] = None
    traceback: Optional[str] = None
    locations: List[Dict[str, Any]] = None  # List of {'file': str, 'line': int}

    def __post_init__(self):
        if self.locations is None:
            self.locations = []

def run_test_command(command_args: List[str]) -> FailureReport:
    """Run a test command, capture its output, and parse the failure."""
    cmd_str = " ".join(command_args)
    framework = "unknown"
    if "pytest" in command_args[0]:
        framework = "pytest"
    elif "jest" in command_args[0]:
        framework = "jest"

    start_time = time.time()

    # Try to inject our tracer for pytest by using it as a plugin
    run_env = None
    if framework == "pytest":
        import os
        import sys
        run_env = os.environ.copy()
        # Prepend our package to PYTHONPATH if needed, and set PYTEST_PLUGINS
        run_env["PYTEST_PLUGINS"] = "rootcause.pytest_plugin"
        # We also need to use the python executable explicitly to ensure correct env resolution if needed
        # but let's just use the command_args provided and hope they resolve correctly.
        # However, to be safe, if the command is just 'pytest', maybe we can use `sys.executable -m pytest`
        if command_args[0] == "pytest":
            command_args = [sys.executable, "-m", "pytest"] + command_args[1:]

    # Run the command
    result = subprocess.run(
        command_args,
        capture_output=True,
        text=True,
        env=run_env
    )

    runtime = time.time() - start_time

    report = FailureReport(
        command=cmd_str,
        exit_code=result.returncode,
        stdout=result.stdout,
        stderr=result.stderr,
        runtime_seconds=runtime,
        framework=framework
    )

    if result.returncode != 0:
        parse_failure(report)

    return report

def parse_failure(report: FailureReport) -> None:
    """Extract useful information from the failure output."""
    output = report.stdout + "\n" + report.stderr

    if report.framework == "pytest":
        # Basic parsing for pytest
        # Find test name
        test_name_match = re.search(r"_{3,} (.+?) _{3,}", output)
        if test_name_match:
            report.test_name = test_name_match.group(1)

        # Find error type
        err_type_match = re.search(r"([A-Za-z]+Error):", output)
        if err_type_match:
            report.error_type = err_type_match.group(1)

        # Find locations (file:line) in tracebacks
        # Look for things like "tests/test_auth.py:12:" or "File ".../file.py", line 12"
        locations = []

        # Pytest style: "tests/test_auth.py:12: AssertionError"
        for match in re.finditer(r"([a-zA-Z0-9_/\.\-]+):(\d+):", output):
            locations.append({
                "file": match.group(1),
                "line": int(match.group(2))
            })

        # Standard Python traceback style: "File "/path/to/file.py", line 12"
        for match in re.finditer(r'File "([^"]+)", line (\d+)', output):
            locations.append({
                "file": match.group(1),
                "line": int(match.group(2))
            })

        report.locations = locations
        report.traceback = output # for simplicity, store full output

    elif report.framework == "jest":
        # Very basic jest parsing
        # Jest prints files and line numbers often like "at Object.<anonymous> (src/auth.js:14:7)"
        locations = []
        for match in re.finditer(r"\(([^:]+):(\d+):(\d+)\)", output):
            locations.append({
                "file": match.group(1),
                "line": int(match.group(2))
            })
        report.locations = locations
        report.traceback = output
    else:
        # Generic parsing
        locations = []
        for match in re.finditer(r'File "([^"]+)", line (\d+)', output):
            locations.append({
                "file": match.group(1),
                "line": int(match.group(2))
            })
        report.locations = locations
        report.traceback = output

def parse_log_file(filepath: str) -> FailureReport:
    """Parse a raw log file."""
    with open(filepath, "r") as f:
        content = f.read()

    report = FailureReport(
        command="analyze " + filepath,
        exit_code=1,
        stdout=content,
        stderr="",
        runtime_seconds=0.0,
        framework="log"
    )

    parse_failure(report)
    return report
