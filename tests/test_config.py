import os
import tempfile
from unittest import mock
from rootcause import config

def test_config_fallback():
    # Test that api key can be retrieved from env var
    with mock.patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test_key_env"}):
        assert config.get_api_key() == "test_key_env"

def test_config_file_read_write():
    # Test setting and getting API key via file
    with tempfile.TemporaryDirectory() as tmpdir:
        # Patch CONFIG_DIR to use temp dir
        orig_config_dir = config.CONFIG_DIR
        orig_config_file = config.CONFIG_FILE
        try:
            from pathlib import Path
            config.CONFIG_DIR = Path(tmpdir)
            config.CONFIG_FILE = Path(tmpdir) / "config.toml"

            # Ensure env var is not set
            if "ANTHROPIC_API_KEY" in os.environ:
                del os.environ["ANTHROPIC_API_KEY"]

            config.set_api_key("test_key_file")
            assert config.get_api_key() == "test_key_file"
        finally:
            config.CONFIG_DIR = orig_config_dir
            config.CONFIG_FILE = orig_config_file
