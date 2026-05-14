import os
import tempfile
from rootcause.patcher import _apply_patch_naive

def test_naive_patcher():
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        f.write("def foo():\n    return 1\n\ndef bar():\n    return 2\n")
        tmp_path = f.name

    diff = f"""--- a/{tmp_path}
+++ b/{tmp_path}
@@ -1,4 +1,4 @@
 def foo():
-    return 1
+    return 3

 def bar():
"""
    try:
        success = _apply_patch_naive(diff)
        assert success
        with open(tmp_path, "r") as f:
            content = f.read()
        assert "return 3" in content
        assert "return 1" not in content
    finally:
        os.remove(tmp_path)
