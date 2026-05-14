import os
import subprocess
from typing import Dict, Set

from .runner import FailureReport

def get_recent_git_changes(filepath: str, max_commits: int = 5) -> str:
    """Gets the recent git changes for a specific file."""
    try:
        # Check if inside a git repo
        subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            check=True, capture_output=True
        )

        result = subprocess.run(
            ["git", "log", f"-n{max_commits}", "-p", "--", filepath],
            capture_output=True,
            text=True
        )
        return result.stdout
    except subprocess.CalledProcessError:
        return ""
    except FileNotFoundError:
        return ""

def gather_file_context(filepath: str, line_numbers: Set[int], context_lines: int = 30) -> str:
    """Reads a file and extracts surrounding lines around target line numbers."""
    if not os.path.exists(filepath):
        return ""

    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()
    except Exception:
        return ""

    if not lines:
        return ""

    result = []
    result.append(f"--- File: {filepath} ---")

    # We want to show a window of lines around each target line
    # Merge overlapping windows to avoid duplication
    windows = []
    for line_no in sorted(list(line_numbers)):
        start = max(0, line_no - context_lines - 1)
        end = min(len(lines), line_no + context_lines)
        windows.append((start, end))

    # Merge overlapping windows
    merged_windows = []
    if windows:
        current_start, current_end = windows[0]
        for start, end in windows[1:]:
            if start <= current_end:
                current_end = max(current_end, end)
            else:
                merged_windows.append((current_start, current_end))
                current_start, current_end = start, end
        merged_windows.append((current_start, current_end))

    for start, end in merged_windows:
        if start > 0:
            result.append("...")
        for i in range(start, end):
            # i is 0-indexed, line numbers are 1-indexed
            prefix = ">> " if (i + 1) in line_numbers else "   "
            result.append(f"{prefix}{i+1}: {lines[i].rstrip()}")

    return "\n".join(result)

def gather_context(report: FailureReport) -> Dict[str, str]:
    """Gathers source context and git context based on the failure report."""
    source_contexts = []
    git_contexts = []

    # Group line numbers by file
    files_to_lines = {}
    for loc in report.locations:
        # Ignore obvious stdlib or third party libraries if we can
        file_path = loc['file']
        if "site-packages" in file_path or "/lib/python" in file_path or file_path.startswith("<"):
            continue

        # Try to resolve relative path if needed, we assume we run from project root
        if not os.path.exists(file_path):
            # Just a heuristic, maybe it's an absolute path
            pass

        if file_path not in files_to_lines:
            files_to_lines[file_path] = set()
        files_to_lines[file_path].add(loc['line'])

    for filepath, lines in files_to_lines.items():
        if os.path.exists(filepath):
            src_context = gather_file_context(filepath, lines)
            if src_context:
                source_contexts.append(src_context)

            git_diff = get_recent_git_changes(filepath)
            if git_diff:
                git_contexts.append(f"--- Git history for {filepath} ---\n{git_diff}")

    return {
        "source_context": "\n\n".join(source_contexts),
        "git_context": "\n\n".join(git_contexts)
    }
