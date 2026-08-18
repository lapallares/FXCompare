"""Application configuration."""

import json
from pathlib import Path


CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.json"


def load_config() -> dict:
    """Load FXCompare settings from config.json."""
    with CONFIG_PATH.open(encoding="utf-8") as config_file:
        return json.load(config_file)
