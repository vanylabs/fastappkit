"""
Configuration file parser for fastappkit.toml.

Uses Python 3.11+ built-in tomllib module.
"""

from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Any

from fastappkit.exceptions import ConfigError


def load_config(config_path: Path | None = None) -> dict[str, Any]:
    """
    Load and parse fastappkit.toml configuration file.

    Args:
        config_path: Path to fastappkit.toml. If None, looks for it
                     in current directory (project root).

    Returns:
        dict: Parsed configuration from [tool.fastappkit] section

    Raises:
        ConfigError: If config file is missing or invalid
    """
    if config_path is None:
        config_path = find_config_file()

    if not config_path or not config_path.exists():
        raise ConfigError(
            f"Configuration file not found: {config_path or 'fastappkit.toml'}. "
            "Run 'fastappkit core new <name>' to create a new project."
        )

    try:
        with open(config_path, "rb") as f:
            data = tomllib.load(f)
    except Exception as e:
        raise ConfigError(f"Failed to parse configuration file: {e}") from e

    # Extract [tool.fastappkit] section
    tool_config: dict[str, Any] = data.get("tool", {}).get("fastappkit", {})

    if not tool_config:
        raise ConfigError("No [tool.fastappkit] section found in configuration file.")

    return tool_config


def find_config_file(start_path: Path | None = None) -> Path | None:
    """
    Find fastappkit.toml at the expected location.

    Args:
        start_path: Project root directory. Defaults to current directory.

    Returns:
        Path to fastappkit.toml if found, None otherwise
    """
    if start_path is None:
        start_path = Path.cwd()

    config_file = Path(start_path).resolve() / "fastappkit.toml"

    if config_file.exists():
        return config_file

    return None


def get_apps_list(config: dict[str, Any] | None = None) -> list[str]:
    """
    Extract apps list from configuration.

    Args:
        config: Configuration dict. If None, loads from fastappkit.toml

    Returns:
        list: List of app entries from apps = []
    """
    if config is None:
        config = load_config()

    apps = config.get("apps", [])

    if not isinstance(apps, list):
        raise ConfigError("'apps' must be a list in fastappkit.toml")

    return apps
