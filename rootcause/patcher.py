import os
import tempfile

from .analyzer import Analysis
from .display import get_console


def apply_fix(analysis: Analysis) -> bool:
    """Attempts to apply the fix automatically using the unified diff."""
    if not analysis.fix_diff:
        console = get_console()
        console.print("[warning]No unified diff provided in analysis to apply fix.[/warning]")
        return False

    # We create a temporary file with the diff
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".diff") as tmp:
        tmp.write(analysis.fix_diff)
        tmp_path = tmp.name

    try:
        # Instead of relying on the system `patch` command, use python's difflib or simple parsing if possible.
        # However, Python stdlib doesn't have a built-in patch applier.
        # We can implement a naive patcher for standard unified diffs or use simple search/replace.
        # For our purposes, a simple diff parser that reads unified diff and replaces lines is sufficient.
        success = _apply_patch_naive(analysis.fix_diff)
        if success:
            return True
        else:
            console = get_console()
            console.print("[danger]Failed to apply patch with naive Python applier.[/danger]")
            return False
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def _apply_patch_naive(diff_text: str) -> bool:
    """A naive unified diff applier in pure Python."""
    # This expects a standard unified diff
    lines = diff_text.splitlines()
    if not lines:
        return False

    file_path = None

    # Simple state machine
    for line in lines:
        if line.startswith("--- ") or line.startswith("+++ "):
            # Extract filename. E.g. "+++ b/src/file.py" -> "src/file.py"
            parts = line.split("\t")[0].split(" ")
            if len(parts) > 1:
                potential_path = parts[1]
                if potential_path.startswith("a/") or potential_path.startswith("b/"):
                    potential_path = potential_path[2:]

                # If we're at the +++ line, we should load the file
                if line.startswith("+++ "):
                    file_path = potential_path
                    if os.path.exists(file_path):
                        pass
                    else:
                        # File doesn't exist? Try without any path stripping
                        if os.path.exists(parts[1]):
                            file_path = parts[1]
                            # with open(file_path, "r") as f:
                            #     file_content = f.read().splitlines()
        elif line.startswith("@@"):
            # We skip proper hunk handling for simplicity in this naive implementation
            # and just try to find the context in the file and replace it.
            pass

    # Given the complexity of writing a full patch applier, we will try a different approach:
    # Instead of full hunk parsing, we find the exact block of removed lines and replace with added lines.

    if not file_path or not os.path.exists(file_path):
        return False

    with open(file_path, "r") as f:
        file_text = f.read()

    # We'll group the diff into hunks based on @@ lines
    hunks = diff_text.split("@@")
    if len(hunks) < 3:
        return False  # Invalid format

    # Process each hunk
    for i in range(2, len(hunks), 2):
        # We don't really use the hunk header, we just parse the body
        hunk_body = hunks[i]

        search_block = []
        replace_block = []

        hunk_lines = hunk_body.splitlines()
        # First element is always empty — the \n right after @@ when splitting on @@
        if hunk_lines and hunk_lines[0] == "":
            hunk_lines = hunk_lines[1:]

        for h_line in hunk_lines:
            if h_line == "":
                # blank context line in unified diff
                search_block.append("")
                replace_block.append("")
                continue
            if h_line.startswith("-"):
                search_block.append(h_line[1:])
            elif h_line.startswith("+"):
                replace_block.append(h_line[1:])
            elif h_line.startswith(" "):
                search_block.append(h_line[1:])
                replace_block.append(h_line[1:])

        search_str = "\n".join(search_block)
        replace_str = "\n".join(replace_block)

        if search_str and search_str in file_text:
            file_text = file_text.replace(search_str, replace_str, 1)
        else:
            # Maybe the newlines are different
            # Try stripping trailing spaces
            search_str_stripped = "\n".join([line_str.rstrip() for line_str in search_block])
            file_text_stripped = "\n".join(
                [line_str.rstrip() for line_str in file_text.splitlines()]
            )
            if search_str_stripped in file_text_stripped:
                # To do this safely, we'd need to reconstruct, but for simplicity we fail here if not exact
                return False
            return False

    with open(file_path, "w") as f:
        f.write(file_text)

    return True
