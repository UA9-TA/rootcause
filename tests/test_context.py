import os
import tempfile
from rootcause.context import gather_file_context

def test_gather_file_context():
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write("line 1\nline 2\nline 3\nline 4\nline 5\n")
        tmp_path = f.name

    try:
        context = gather_file_context(tmp_path, {3}, context_lines=1)
        assert "line 2" in context
        assert ">> 3: line 3" in context
        assert "line 4" in context
        assert "line 1" not in context
        assert "line 5" not in context
    finally:
        os.remove(tmp_path)
