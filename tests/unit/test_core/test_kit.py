"""
Tests for FastAppKit main class.

Tests focus on:
- App creation workflow
- Settings integration
- Error handling during app creation
- Integration with loader and router assembler
"""

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI

from fastappkit.conf import set_settings
from fastappkit.core.kit import FastAppKit
from fastappkit.exceptions import AppLoadError
from tests.conftest import TestSettings
from tests.fixtures import ConfigFactory, ProjectFactory


class TestFastAppKit:
    """Tests for FastAppKit class."""

    def test_init_sets_settings(self, test_settings: TestSettings) -> None:
        """FastAppKit initialization sets global settings."""
        kit = FastAppKit(settings=test_settings)

        assert kit.settings == test_settings
        # Verify settings are set globally
        from fastappkit.conf import get_settings

        assert get_settings() == test_settings

    def test_create_app_creates_fastapi_instance(
        self, test_settings: TestSettings, temp_project: Path
    ) -> None:
        """create_app() returns a FastAPI instance."""
        # Create minimal project
        ProjectFactory.create_minimal(temp_project)
        ConfigFactory.create_minimal(temp_project / "fastappkit.toml")

        original_cwd = os.getcwd()
        try:
            os.chdir(temp_project)
            set_settings(test_settings)

            kit = FastAppKit(settings=test_settings)
            app = kit.create_app()

            assert isinstance(app, FastAPI)
            assert app.title == "FastAppKit Application"
            assert app.debug == test_settings.DEBUG
        finally:
            os.chdir(original_cwd)

    def test_create_app_with_no_config_creates_empty_app(
        self, test_settings: TestSettings, temp_project: Path
    ) -> None:
        """create_app() with no config creates app with no routes."""
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_project)
            set_settings(test_settings)

            kit = FastAppKit(settings=test_settings)
            app = kit.create_app()

            # App should be created but with no app routes
            # (FastAPI automatically adds OpenAPI/docs routes)
            assert isinstance(app, FastAPI)
            # Filter out FastAPI's built-in routes (openapi, docs, redoc)
            app_routes = [
                r
                for r in app.routes
                if hasattr(r, "path")
                and r.path not in ["/openapi.json", "/docs", "/docs/oauth2-redirect", "/redoc"]
            ]
            # No apps loaded, so no custom routes
            assert len(app_routes) == 0
        finally:
            os.chdir(original_cwd)

    def test_create_app_loads_and_mounts_apps(
        self, test_settings: TestSettings, temp_project: Path
    ) -> None:
        """create_app() loads apps and mounts their routers."""
        # Create project with an app
        ProjectFactory.create_with_apps(temp_project, "blog")

        original_cwd = os.getcwd()
        try:
            os.chdir(temp_project)
            set_settings(test_settings)

            kit = FastAppKit(settings=test_settings)
            app = kit.create_app()

            # App should have routes from the blog app
            routes = [r for r in app.routes if hasattr(r, "path")]
            assert len(routes) > 0
            # Should have the hello route from blog app
            paths = [r.path for r in routes if hasattr(r, "path")]
            assert any("/blog" in path or path == "/blog" or path == "/blog/" for path in paths)
        finally:
            os.chdir(original_cwd)

    def test_create_app_fails_fast_on_app_load_error(
        self, test_settings: TestSettings, temp_project: Path
    ) -> None:
        """create_app() raises AppLoadError if any app fails to load."""
        # Create config with invalid app entry
        ConfigFactory.create_fastappkit_toml(
            temp_project / "fastappkit.toml", apps=["apps.nonexistent"]
        )

        original_cwd = os.getcwd()
        try:
            os.chdir(temp_project)
            set_settings(test_settings)

            kit = FastAppKit(settings=test_settings)

            with pytest.raises(AppLoadError):
                kit.create_app()
        finally:
            os.chdir(original_cwd)

    @patch("fastappkit.core.kit.AppLoader")
    @patch("fastappkit.core.kit.RouterAssembler")
    def test_create_app_calls_loader_and_assembler(
        self,
        mock_assembler_class: MagicMock,
        mock_loader_class: MagicMock,
        test_settings: TestSettings,
    ) -> None:
        """create_app() properly orchestrates loader and assembler."""
        # Setup mocks
        mock_loader = MagicMock()
        mock_loader.load_all.return_value = MagicMock()
        mock_loader_class.return_value = mock_loader

        mock_assembler = MagicMock()
        mock_assembler_class.return_value = mock_assembler

        kit = FastAppKit(settings=test_settings)
        app = kit.create_app()

        # Verify loader was called
        mock_loader.load_all.assert_called_once()
        mock_loader.execute_registrations.assert_called_once_with(app)

        # Verify assembler was called
        mock_assembler.assemble.assert_called_once_with(app, mock_loader.load_all.return_value)
