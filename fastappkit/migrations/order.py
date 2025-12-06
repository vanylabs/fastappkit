"""
Migration ordering - ensures core → internal → external execution order.
"""

from __future__ import annotations

from pathlib import Path

from fastappkit.core.registry import AppMetadata, AppRegistry
from fastappkit.core.types import AppType


class MigrationOrderer:
    """Orders apps for migration execution."""

    @staticmethod
    def order_apps(registry: AppRegistry) -> list[AppMetadata]:
        """
        Order apps for migration execution.

        Order: core → internal apps (config order) → external apps (config order)

        Args:
            registry: AppRegistry with loaded apps

        Returns:
            Ordered list of AppMetadata objects
        """
        # Separate apps by type
        internal_apps = []
        external_apps = []

        for app_metadata in registry.list():
            if app_metadata.app_type == AppType.INTERNAL:
                internal_apps.append(app_metadata)
            else:
                external_apps.append(app_metadata)

        # Order: internal first (they're already in config order from registry),
        # then external (also in config order)
        # Note: Core migrations are handled separately, not through registry
        return internal_apps + external_apps

    @staticmethod
    def get_core_migration_path(project_root: Path) -> Path:
        """
        Get path to core migrations directory.

        Args:
            project_root: Root directory of the project

        Returns:
            Path to core/db/migrations/
        """
        return project_root / "core" / "db" / "migrations"
