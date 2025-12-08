"""
Project factory for creating test project structures.

Provides structured builders for creating complete test projects.
Uses the same templates as the actual CLI commands to ensure consistency.
"""

from __future__ import annotations

from pathlib import Path

from fastappkit.cli.templates import get_template_engine

from tests.fixtures.app_factory import InternalAppFactory
from tests.fixtures.config_factory import ConfigFactory


class ProjectFactory:
    """Factory for creating test project structures."""

    @staticmethod
    def create_minimal(project_path: Path) -> Path:
        """
        Create minimal project structure using actual templates.

        This matches what 'fastappkit core new' creates, ensuring tests
        use the same files as production.

        Args:
            project_path: Path where to create project

        Returns:
            Path to created project
        """
        project_path.mkdir(parents=True, exist_ok=True)

        # Create directory structure
        (project_path / "core" / "db" / "migrations" / "versions").mkdir(
            parents=True, exist_ok=True
        )
        (project_path / "apps").mkdir(parents=True, exist_ok=True)

        # Prepare template context (same as core new command)
        context = {
            "project_name": project_path.name,
            "project_description": "A FastAPI project built with fastappkit",
            "use_poetry": True,
        }

        # Get template engine (same one used by CLI)
        template_engine = get_template_engine()

        # Render core files using actual templates
        templates = [
            ("project/core/__init__.py.j2", "core/__init__.py"),
            ("project/core/config.py.j2", "core/config.py"),
            ("project/core/app.py.j2", "core/app.py"),
            ("project/core/db/__init__.py.j2", "core/db/__init__.py"),
            ("project/core/db/migrations/env.py.j2", "core/db/migrations/env.py"),
            (
                "project/core/db/migrations/script.py.mako.j2",
                "core/db/migrations/script.py.mako",
            ),
        ]

        for template_path, output_path in templates:
            template_engine.render_to_file(
                template_path,
                project_path / output_path,
                context,
                overwrite=True,  # Allow overwrite for tests
            )

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
