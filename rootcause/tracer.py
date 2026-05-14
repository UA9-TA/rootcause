import sys
import threading
from typing import List, Dict, Any

class Tracer:
    """
    A minimal system tracer to instrument Python execution.
    For v1 we keep it simple since we mostly rely on pytest's tracebacks,
    but this provides a framework for execution trace collection.
    """
    def __init__(self):
        self.traces: List[Dict[str, Any]] = []
        self._lock = threading.Lock()

    def trace_calls(self, frame, event, arg):
        if event != 'call':
            return

        co = frame.f_code
        func_name = co.co_name
        line_no = frame.f_lineno
        filename = co.co_filename

        # Filter out standard library paths to reduce noise
        if "site-packages" in filename or "/lib/python" in filename:
            return

        with self._lock:
            self.traces.append({
                "file": filename,
                "line": line_no,
                "function": func_name
            })

        return self.trace_calls

    def start(self):
        sys.settrace(self.trace_calls)

    def stop(self):
        sys.settrace(None)

    def get_traces(self) -> List[Dict[str, Any]]:
        return self.traces

# Global tracer instance if needed
global_tracer = Tracer()
