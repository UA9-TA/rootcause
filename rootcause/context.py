import os
import subprocess
from typing import Dict, Set

from .runner import FailureReport


def get_recent_git_changes(filepath: str, max_commits: int = 5) -> str:
    """Gets the recent git log + diff for a file."""
    try:
        subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"], check=True, capture_output=True
        )
        result = subprocess.run(
            ["git", "log", f"-n{max_commits}", "-p", "--", filepath], capture_output=True, text=True
        )
        return result.stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""


def gather_file_context(filepath: str, line_numbers: Set[int], context_lines: int = 30) -> str:
    """Reads a file and extracts ±context_lines around each target line."""
    if not os.path.exists(filepath):
        return ""

    try:
        with open(filepath, "r") as f:
            lines = f.readlines()
    except Exception:
        return ""

    if not lines:
        return ""

    result = [f"--- File: {filepath} ---"]

    windows = []
    for line_no in sorted(line_numbers):
        start = max(0, line_no - context_lines - 1)
        end = min(len(lines), line_no + context_lines)
        windows.append((start, end))

    # Merge overlapping windows
    merged = []
    if windows:
        cur_start, cur_end = windows[0]
        for start, end in windows[1:]:
            if start <= cur_end:
                cur_end = max(cur_end, end)
            else:
                merged.append((cur_start, cur_end))
                cur_start, cur_end = start, end
        merged.append((cur_start, cur_end))

    for start, end in merged:
        if start > 0:
            result.append("...")
        for i in range(start, end):
            prefix = ">> " if (i + 1) in line_numbers else "   "
            result.append(f"{prefix}{i + 1}: {lines[i].rstrip()}")

    return "\n".join(result)


def gather_context(report: FailureReport, tracer=None) -> Dict[str, str]:
    """
    Gathers source context, git history, and optional execution traces.
    tracer: a Tracer instance (optional) — if provided, includes frame context.
    """
    source_contexts = []
    git_contexts = []

    files_to_lines: Dict[str, Set[int]] = {}
    for loc in report.locations:
        file_path = loc["file"]
        if "site-packages" in file_path or "/lib/python" in file_path or file_path.startswith("<"):
            continue
        if file_path not in files_to_lines:
            files_to_lines[file_path] = set()
        files_to_lines[file_path].add(loc["line"])

    for filepath, lines in files_to_lines.items():
        if os.path.exists(filepath):
            src = gather_file_context(filepath, lines)
            if src:
                source_contexts.append(src)
            git = get_recent_git_changes(filepath)
            if git:
                git_contexts.append(f"--- Git history for {filepath} ---\n{git}")

    result = {
        "source_context": "\n\n".join(source_contexts),
        "git_context": "\n\n".join(git_contexts),
    }

    if tracer:
        trace_str = tracer.format_for_context()
        if trace_str:
            result["trace_context"] = trace_str

    return result
