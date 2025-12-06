"""
App loader - orchestrates app discovery, loading, and registration.
"""

from __future__ import annotations

import sys
from pathlib import Path

from fastapi import APIRouter, FastAPI

from fastappkit.conf.config import find_config_file, get_apps_list, load_config
from fastappkit.core.entrypoint import EntrypointLoader
from fastappkit.core.manifest import ManifestLoader
from fastappkit.core.registry import AppMetadata, AppRegistry
from fastappkit.core.resolver import AppResolver
from fastappkit.core.types import AppType
from fastappkit.exceptions import AppLoadError
from fastappkit.utils.errors import ErrorFormatter


class AppLoader:
    """Loads and registers apps from configuration."""

    def __init__(self, project_root: Path | None = None):
        """
        Initialize app loader.

        Args:
            project_root: Root directory of the project. If None, uses current directory.
        """
        self.project_root = project_root or Path.cwd()
        self.resolver = AppResolver()
        self.manifest_loader = ManifestLoader()
        self.entrypoint_loader = EntrypointLoader()
        self.registry = AppRegistry()

    def load_all(self, config_path: Path | None = None) -> AppRegistry:
        """
        Load all apps from configuration.

        Args:
            config_path: Path to fastappkit.toml. If None, searches for it.

        Returns:
            AppRegistry: Registry with all loaded apps

        Raises:
            AppLoadError: If any app fails to load (fail-fast)
        """
        # Find and load config
        if config_path is None:
            config_path = find_config_file(self.project_root)

        if not config_path:
            # No config file - return empty registry
            return self.registry

        config = load_config(config_path)
        apps_list = get_apps_list(config)

        # Load each app in order
        for entry in apps_list:
            try:
                self._load_app(entry)
            except AppLoadError as e:
                # Format detailed error message
                error_msg = self._format_load_error(e, entry)
                raise AppLoadError(
                    entry,
                    e.stage,
                    error_msg,
                    original_error=e.original_error,
                ) from e

        return self.registry

    def _load_app(self, entry: str) -> None:
        """
        Load a single app.

        Args:
            entry: App entry from config

        Raises:
            AppLoadError: If app fails to load
        """
        # Step 1: Resolve app
        try:
            app_info = self.resolver.resolve(entry, self.project_root)
        except AppLoadError as e:
            raise AppLoadError(
                entry,
                "resolve",
                f"Failed to resolve app: {e}",
                original_error=e,
            ) from e

        # Step 2: Load manifest
        try:
            manifest = self.manifest_loader.load_manifest(app_info)
        except AppLoadError as e:
            raise AppLoadError(
                entry,
                "manifest",
                f"Failed to load manifest: {e}",
                original_error=e,
            ) from e

        # Step 3: Validate entrypoint exists (but don't execute yet)
        entrypoint_str = manifest.get("entrypoint", f"{app_info.import_path}:register")
        try:
            # For internal apps, ensure project root is in sys.path
            if app_info.app_type == AppType.INTERNAL and str(self.project_root) not in sys.path:
                sys.path.insert(0, str(self.project_root))

            # Just validate it can be loaded, don't store it yet
            self.entrypoint_loader.load_entrypoint(
                entrypoint_str,
                app_info.import_path,
            )
        except AppLoadError as e:
            raise AppLoadError(
                entry,
                "entrypoint",
                f"Failed to load entrypoint: {e}",
                original_error=e,
            ) from e

        # Step 4: Determine route prefix
        prefix = manifest.get("route_prefix", f"/{app_info.name}")

        # Step 5: Determine migrations path
        migrations_path = None
        if manifest.get("migrations"):
            if app_info.filesystem_path:
                # Migrations are inside the package directory (standard Python package structure)
                # manifest["migrations"] is relative to package root (e.g., "migrations")
                migrations_path = str(app_info.filesystem_path / manifest["migrations"])
            else:
                # For pip-installed packages, migrations path is relative to package
                # We'll need to resolve it at runtime using importlib.resources or package location
                migrations_path = manifest["migrations"]
        elif app_info.filesystem_path:
            # For internal apps, default to apps/<name>/migrations/ if it exists
            # For external apps, migrations are required in manifest
            if app_info.app_type == AppType.INTERNAL:
                default_migrations_path = app_info.filesystem_path / "migrations"
                if default_migrations_path.exists():
                    migrations_path = str(default_migrations_path)
                # Even if it doesn't exist, set it so migrations can be created
                else:
                    migrations_path = str(default_migrations_path)

        # Step 6: Create app metadata
        app_metadata = AppMetadata(
            name=app_info.name,
            app_type=app_info.app_type,
            import_path=app_info.import_path,
            filesystem_path=(str(app_info.filesystem_path) if app_info.filesystem_path else None),
            migrations_path=migrations_path,
            prefix=prefix,
            manifest=manifest,
        )

        # Step 7: Register in registry
        self.registry.register(app_metadata)

    def _format_load_error(self, error: AppLoadError, entry: str) -> str:
        """
        Format detailed error message for app loading failure.

        Args:
            error: The AppLoadError
            entry: Original entry string

        Returns:
            Formatted error message
        """
        # Try to get manifest if available
        manifest = None
        if hasattr(error, "manifest"):
            manifest = error.manifest

        formatter = ErrorFormatter()
        return formatter.format_app_load_error(
            entry,
            error.stage,
            error,
            manifest=manifest,
            original_error=error.original_error,
        )

    def execute_registrations(self, app: FastAPI) -> None:
        """
        Execute all app registration functions.

        This should be called after all apps are loaded and metadata collected.

        Apps can either:
        1. Return an APIRouter from register() - RouterAssembler will mount it with prefix
        2. Mount routers themselves via app.include_router() - RouterAssembler will skip

        Args:
            app: FastAPI application instance
        """
        for app_metadata in self.registry.list():
            # For internal apps, ensure project root is in sys.path
            if app_metadata.app_type.value == "internal" and str(self.project_root) not in sys.path:
                sys.path.insert(0, str(self.project_root))

            # Get entrypoint function
            entrypoint_str = app_metadata.manifest.get(
                "entrypoint",
                f"{app_metadata.import_path}:register",
            )
            entrypoint_func = self.entrypoint_loader.load_entrypoint(
                entrypoint_str,
                app_metadata.import_path,
            )

            # Execute registration
            try:
                result = entrypoint_func(app)

                # If register() returns an APIRouter, store it in registry
                # RouterAssembler will mount it with the appropriate prefix
                if isinstance(result, APIRouter):
                    app_metadata.router = result
            except Exception as e:
                raise AppLoadError(
                    app_metadata.name,
                    "register",
                    f"Failed to execute registration: {e}",
                    original_error=e,
                ) from e
