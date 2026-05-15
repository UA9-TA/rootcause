import re
import subprocess
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


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
    locations: List[Dict[str, Any]] = None

    def __post_init__(self):
        if self.locations is None:
            self.locations = []


def run_test_command(command_args: List[str]) -> FailureReport:
    """Run a test command, capture its output, and parse the failure."""
    cmd_str = " ".join(command_args)
    framework = _detect_framework(command_args)

    start_time = time.time()

    run_env = None
    if framework == "pytest":
        import os
        import sys

        run_env = os.environ.copy()
        run_env["PYTEST_PLUGINS"] = "rootcause.pytest_plugin"
        if command_args[0] == "pytest":
            command_args = [sys.executable, "-m", "pytest"] + command_args[1:]

    result = subprocess.run(command_args, capture_output=True, text=True, env=run_env)

    runtime = time.time() - start_time

    report = FailureReport(
        command=cmd_str,
        exit_code=result.returncode,
        stdout=result.stdout,
        stderr=result.stderr,
        runtime_seconds=runtime,
        framework=framework,
    )

    if result.returncode != 0:
        parse_failure(report)

    return report


def _detect_framework(command_args: List[str]) -> str:
    cmd = " ".join(command_args).lower()
    if "pytest" in cmd:
        return "pytest"
    if "jest" in cmd:
        return "jest"
    if "mocha" in cmd:
        return "mocha"
    return "unknown"


def parse_failure(report: FailureReport) -> None:
    """Extract useful information from the failure output."""
    output = report.stdout + "\n" + report.stderr

    if report.framework == "pytest":
        test_name_match = re.search(r"_{3,} (.+?) _{3,}", output)
        if test_name_match:
            report.test_name = test_name_match.group(1)

        err_type_match = re.search(r"([A-Za-z]+Error):", output)
        if err_type_match:
            report.error_type = err_type_match.group(1)

        locations = []
        for match in re.finditer(r"([a-zA-Z0-9_/\.\-]+\.py):(\d+):", output):
            locations.append({"file": match.group(1), "line": int(match.group(2))})
        for match in re.finditer(r'File "([^"]+)", line (\d+)', output):
            locations.append({"file": match.group(1), "line": int(match.group(2))})

        report.locations = locations
        report.traceback = output

    elif report.framework in ("jest", "mocha"):
        # Jest and Mocha both print stack frames as: at ... (file.js:line:col)
        locations = []
        for match in re.finditer(r"\(([^:)]+\.[jt]sx?):(\d+):\d+\)", output):
            locations.append({"file": match.group(1), "line": int(match.group(2))})

        # Mocha also prints: at Context.<anonymous> (test/auth.spec.js:14:7)
        # Jest prints: FAIL src/__tests__/auth.test.js
        fail_match = re.search(r"(?:FAIL|failing)\s+(\S+\.(?:spec|test)\.[jt]sx?)", output)
        if fail_match:
            report.test_name = fail_match.group(1)

        err_match = re.search(r"(Error|AssertionError|TypeError)[::]?\s+(.+)", output)
        if err_match:
            report.error_type = err_match.group(1)

        report.locations = locations
        report.traceback = output

    else:
        locations = []
        for match in re.finditer(r'File "([^"]+)", line (\d+)', output):
            locations.append({"file": match.group(1), "line": int(match.group(2))})
        report.locations = locations
        report.traceback = output


def parse_log_file(filepath: str) -> FailureReport:
    """Parse a raw log file or traceback."""
    with open(filepath, "r") as f:
        content = f.read()

    report = FailureReport(
        command="analyze " + filepath,
        exit_code=1,
        stdout=content,
        stderr="",
        runtime_seconds=0.0,
        framework="log",
    )

    parse_failure(report)
    return report


def parse_raw_text(text: str, source: str = "terminal") -> FailureReport:
    """Parse raw error text (e.g. from shell history)."""
    report = FailureReport(
        command=f"last ({source})",
        exit_code=1,
        stdout=text,
        stderr="",
        runtime_seconds=0.0,
        framework="log",
    )
    parse_failure(report)
    return report
