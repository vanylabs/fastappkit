"""
Tests for AppLoader.

Tests focus on:
- Loading apps from configuration
- Handling internal vs external apps
- Error handling at each stage (resolve, manifest, entrypoint)
- Registration execution
- Edge cases that would break if implementation changes
"""

from pathlib import Path

import pytest

from fastappkit.core.loader import AppLoader
from fastappkit.core.registry import AppRegistry
from fastappkit.exceptions import AppLoadError
from tests.fixtures import ConfigFactory, InternalAppFactory, ProjectFactory


class TestAppLoader:
    """Tests for AppLoader class."""

    def test_init_sets_project_root(self, temp_project: Path) -> None:
        """AppLoader initialization sets project root."""
        loader = AppLoader(project_root=temp_project)

        assert loader.project_root == temp_project

    def test_init_defaults_to_current_directory(self) -> None:
        """AppLoader initialization defaults to current directory."""
        loader = AppLoader()

        assert loader.project_root == Path.cwd()

    def test_load_all_with_no_config_returns_empty_registry(self, temp_project: Path) -> None:
        """load_all() with no config file returns empty registry."""
        # Don't create fastappkit.toml
        loader = AppLoader(project_root=temp_project)
        registry = loader.load_all()

        assert isinstance(registry, AppRegistry)
        assert len(registry) == 0

    def test_load_all_loads_single_internal_app(self, temp_project: Path) -> None:
        """load_all() successfully loads a single internal app."""
        # Create project with app
        ProjectFactory.create_with_apps(temp_project, "blog")

        loader = AppLoader(project_root=temp_project)
        registry = loader.load_all()

        assert len(registry) == 1
        app_metadata = registry.get("blog")
        assert app_metadata is not None
        assert app_metadata.name == "blog"
        assert app_metadata.import_path == "apps.blog"

    def test_load_all_loads_multiple_apps(self, temp_project: Path) -> None:
        """load_all() successfully loads multiple apps."""
        ProjectFactory.create_with_apps(temp_project, "blog", "shop")

        loader = AppLoader(project_root=temp_project)
        registry = loader.load_all()

        assert len(registry) == 2
        assert "blog" in registry
        assert "shop" in registry

    def test_load_all_fails_fast_on_first_error(self, temp_project: Path) -> None:
        """load_all() raises AppLoadError on first app failure."""
        # Create config with one valid and one invalid app
        ConfigFactory.create_fastappkit_toml(
            temp_project / "fastappkit.toml", apps=["apps.blog", "apps.nonexistent"]
        )
        # Create only the first app
        InternalAppFactory.create_minimal(temp_project, "blog")

        loader = AppLoader(project_root=temp_project)

        with pytest.raises(AppLoadError) as exc_info:
            loader.load_all()

        # Should fail on the second app
        assert exc_info.value.app_name == "apps.nonexistent"

    def test_execute_registrations_calls_register_functions(
        self, temp_project: Path, fastapi_app: object
    ) -> None:
        """execute_registrations() calls register() for each app."""
        from fastapi import FastAPI

        ProjectFactory.create_with_apps(temp_project, "blog")

        loader = AppLoader(project_root=temp_project)
        registry = loader.load_all()

        app = FastAPI()
        loader.execute_registrations(app)

        # Verify router was created and stored
        blog_metadata = registry.get("blog")
        assert blog_metadata is not None
        # Router should be set after registration
        assert blog_metadata.router is not None

    def test_execute_registrations_raises_error_on_registration_failure(
        self, temp_project: Path
    ) -> None:
        """execute_registrations() raises AppLoadError if registration fails."""
        from fastapi import FastAPI

        # Create app with broken register function
        app_path = InternalAppFactory.create_minimal(temp_project, "blog")

        # Create broken register function
        init_content = '''"""Broken app."""
from fastapi import FastAPI

def register(app: FastAPI):
    """Broken register function."""
    raise RuntimeError("Registration failed")
'''
        (app_path / "__init__.py").write_text(init_content)

        ConfigFactory.create_with_apps(temp_project / "fastappkit.toml", "apps.blog")

        # Add project to sys.path so the app can be imported
        import sys

        project_path_str = str(temp_project)
        if project_path_str not in sys.path:
            sys.path.insert(0, project_path_str)

        try:
            # Clear any cached modules for this app
            module_name = "apps.blog"
            if module_name in sys.modules:
                del sys.modules[module_name]

            loader = AppLoader(project_root=temp_project)
            registry = loader.load_all()

            # Verify app was loaded
            assert len(registry) == 1
            assert "blog" in registry

            app = FastAPI()

            with pytest.raises(AppLoadError) as exc_info:
                loader.execute_registrations(app)

            assert exc_info.value.stage == "register"
            assert "blog" in str(exc_info.value)
        finally:
            # Clean up sys.path and modules
            if project_path_str in sys.path:
                sys.path.remove(project_path_str)
            # Clean up cached module
            if "apps.blog" in sys.modules:
                del sys.modules["apps.blog"]
