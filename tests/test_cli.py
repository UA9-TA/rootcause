from typer.testing import CliRunner
from rootcause.cli import app

runner = CliRunner()

def test_config_command():
    # Just run the config command and check it doesn't crash and outputs success
    # Need to patch the actual config saving to avoid mutating real config
    import rootcause.config
    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as tmpdir:
        orig_config_file = rootcause.config.CONFIG_FILE
        orig_config_dir = rootcause.config.CONFIG_DIR
        try:
            rootcause.config.CONFIG_DIR = Path(tmpdir)
            rootcause.config.CONFIG_FILE = Path(tmpdir) / "config.toml"
            result = runner.invoke(app, ["config", "my_test_key"])
            assert result.exit_code == 0
            assert "API key" in result.stdout
        finally:
            rootcause.config.CONFIG_FILE = orig_config_file
            rootcause.config.CONFIG_DIR = orig_config_dir
