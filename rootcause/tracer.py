import sys
import threading
from typing import Any, Dict, List


class Tracer:
    """
    Minimal sys.settrace wrapper that collects call frames from user code.
    Filters out stdlib and site-packages to keep traces relevant.
    """

    def __init__(self):
        self.traces: List[Dict[str, Any]] = []
        self._lock = threading.Lock()

    def trace_calls(self, frame, event, arg):
        if event != "call":
            return

        filename = frame.f_code.co_filename
        if "site-packages" in filename or "/lib/python" in filename:
            return

        with self._lock:
            self.traces.append(
                {
                    "file": filename,
                    "line": frame.f_lineno,
                    "function": frame.f_code.co_name,
                }
            )

        return self.trace_calls

    def start(self):
        sys.settrace(self.trace_calls)

    def stop(self):
        sys.settrace(None)

    def get_frames(self, max_frames: int = 50) -> List[Dict[str, Any]]:
        """Return deduplicated frames, capped for token budget."""
        seen = set()
        result = []
        for frame in self.traces:
            key = (frame["file"], frame["line"], frame["function"])
            if key not in seen:
                seen.add(key)
                result.append(frame)
        return result[:max_frames]

    def format_for_context(self) -> str:
        """Format traces as a readable string for Claude context."""
        frames = self.get_frames()
        if not frames:
            return ""
        lines = ["## Execution Trace (user code only)"]
        for f in frames:
            lines.append(f"  {f['file']}:{f['line']} in {f['function']}()")
        return "\n".join(lines)


global_tracer = Tracer()
