"""
Configuration factory for creating test fastappkit.toml files.

Provides structured builders for creating test configurations.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


class ConfigFactory:
    """Factory for creating test configuration files."""

    @staticmethod
    def create_fastappkit_toml(
        config_path: Path,
        apps: list[str] | None = None,
        **extra_fields: Any,
    ) -> None:
        """
        Create a fastappkit.toml configuration file.

        Args:
            config_path: Path where to create the file
            apps: List of app entries
            **extra_fields: Additional fields to add to config
        """
        if apps is None:
            apps = []

        content = "[tool.fastappkit]\n"
        content += f"apps = {apps}\n"

        # Add extra fields
        for key, value in extra_fields.items():
            if isinstance(value, str):
                content += f'{key} = "{value}"\n'
            elif isinstance(value, bool):
                content += f"{key} = {str(value).lower()}\n"
            elif isinstance(value, (int, float)):
                content += f"{key} = {value}\n"
            elif isinstance(value, list):
                content += f"{key} = {value}\n"
            else:
                content += f'{key} = "{value}"\n'

        config_path.write_text(content)

    @staticmethod
    def create_minimal(config_path: Path) -> None:
        """Create minimal fastappkit.toml with empty apps list."""
        ConfigFactory.create_fastappkit_toml(config_path, apps=[])

    @staticmethod
    def create_with_apps(config_path: Path, *app_entries: str) -> None:
        """Create fastappkit.toml with specified app entries."""
        ConfigFactory.create_fastappkit_toml(config_path, apps=list(app_entries))
