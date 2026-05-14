import os
import sys
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

CONFIG_DIR = Path.home() / ".rootcause"
CONFIG_FILE = CONFIG_DIR / "config.toml"

def get_api_key() -> str | None:
    # First check environment variable
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if api_key:
        return api_key

    # Fallback to config file
    if not CONFIG_FILE.exists():
        return None

    try:
        with open(CONFIG_FILE, "rb") as f:
            config = tomllib.load(f)
            return config.get("api_key")
    except Exception:
        return None

def set_api_key(api_key: str) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    # Simple write, overwriting if exists
    with open(CONFIG_FILE, "w") as f:
        f.write(f'api_key = "{api_key}"\n')
