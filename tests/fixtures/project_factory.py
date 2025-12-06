"""
Project factory for creating test project structures.

Provides structured builders for creating complete test projects.
"""

from __future__ import annotations

from pathlib import Path

from tests.fixtures.app_factory import InternalAppFactory
from tests.fixtures.config_factory import ConfigFactory


class ProjectFactory:
    """Factory for creating test project structures."""

    @staticmethod
    def create_minimal(project_path: Path) -> Path:
        """
        Create minimal project structure.

        Args:
            project_path: Path where to create project

        Returns:
            Path to created project
        """
        project_path.mkdir(parents=True, exist_ok=True)

        # Create core structure
        (project_path / "core").mkdir(exist_ok=True)
        (project_path / "core" / "db").mkdir(exist_ok=True)
        (project_path / "core" / "db" / "migrations").mkdir(exist_ok=True)
        (project_path / "core" / "db" / "migrations" / "versions").mkdir(exist_ok=True)

        # Create apps directory
        (project_path / "apps").mkdir(exist_ok=True)

        # Create minimal fastappkit.toml
        ConfigFactory.create_minimal(project_path / "fastappkit.toml")

        return project_path

    @staticmethod
    def create_with_apps(project_path: Path, *app_names: str) -> Path:
        """
        Create project with internal apps.

        Args:
            project_path: Path where to create project
            *app_names: Names of apps to create

        Returns:
            Path to created project
        """
        project_path = ProjectFactory.create_minimal(project_path)

        # Create apps
        app_entries = []
        for app_name in app_names:
            InternalAppFactory.create_minimal(project_path, app_name)
            app_entries.append(f"apps.{app_name}")

        # Update config with apps
        ConfigFactory.create_with_apps(project_path / "fastappkit.toml", *app_entries)

        return project_path
