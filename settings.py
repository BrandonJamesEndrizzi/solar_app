"""Project paths, configuration loading, and secret lookup.

Everything here resolves relative to this file, so the project runs from any
directory on any machine. Secrets live in a .env file that is never committed;
non-secret settings live in config.ini.
"""

import configparser
import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent
CONFIG_PATH = PROJECT_ROOT / "config.ini"
DATA_DIR = PROJECT_ROOT / "data_dump"

load_dotenv(PROJECT_ROOT / ".env")


def load_config():
    """Read config.ini and return the parser.

    Raises a clear error if the file is missing, since a fresh clone only ships
    config.ini.example.
    """
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(
            f"No config file at {CONFIG_PATH}. "
            "Copy config.ini.example to config.ini and edit it."
        )
    parser = configparser.ConfigParser()
    parser.read(CONFIG_PATH)
    return parser


def require_env(name):
    """Return an environment variable, or explain how to set it."""
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(
            f"Missing required environment variable {name!r}. "
            "Copy .env.example to .env and fill in your credentials."
        )
    return value


def data_path(*parts):
    """Return a path inside data_dump/, creating the directory if needed."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return DATA_DIR.joinpath(*parts)
