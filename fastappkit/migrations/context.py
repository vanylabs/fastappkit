"""
Migration context builder - creates Alembic EnvironmentContext for each app.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from sqlalchemy import Connection, MetaData

from fastappkit.conf import get_settings
from fastappkit.core.registry import AppMetadata
from fastappkit.migrations.version import VersionTableManager
from fastappkit.migrations.scripts import build_script_directory

if TYPE_CHECKING:
    from fastappkit.core.registry import AppRegistry


class MigrationContextBuilder:
    """Builds Alembic migration contexts for apps."""

    def build_context(
        self,
        app_metadata: AppMetadata,
        connection: Connection,
        target_metadata: MetaData | None = None,
        migration_path: Path | None = None,
    ) -> MigrationContext:
        """
        Build Alembic MigrationContext for an app.

        Args:
            app_metadata: App metadata
            connection: SQLAlchemy connection
            target_metadata: Target SQLAlchemy metadata (for autogenerate)
            migration_path: Path to migration directory (if None, uses app's migrations_path)

        Returns:
            MigrationContext instance
        """
        if migration_path is None:
            if not app_metadata.migrations_path:
                raise ValueError(f"App '{app_metadata.name}' has no migrations_path")
            migration_path = Path(app_metadata.migrations_path)

        # Get version table name
        version_table = VersionTableManager.get_version_table(
            app_metadata.app_type,
            app_metadata.name,
        )

        # Build script directory
        script_dir = build_script_directory(migration_path)

        # Create migration context
        context = MigrationContext.configure(
            connection=connection,
            opts={
                "script": script_dir,
                "version_table": version_table,
                "target_metadata": target_metadata,
            },
        )

        return context

    def build_alembic_config(
        self,
        app_metadata: AppMetadata,
        migration_path: Path | None = None,
        project_root: Path | None = None,
        registry: "AppRegistry" | None = None,
    ) -> Config:
        """
        Build Alembic Config object for an app.

        This is used for command-line operations (upgrade, downgrade, etc.).

        Args:
            app_metadata: App metadata
            migration_path: Path to migration directory
            project_root: Root directory of the project (for internal apps, uses core migrations)
            registry: Optional AppRegistry (not used in simplified approach)

        Returns:
            Alembic Config instance
        """
        if migration_path is None:
            if not app_metadata.migrations_path:
                raise ValueError(f"App '{app_metadata.name}' has no migrations_path")
            migration_path = Path(app_metadata.migrations_path)

        # Create Alembic config
        # For external apps, set config_file_name to None to prevent reading alembic.ini
        # We want to use the database URL from settings, not from alembic.ini
        alembic_cfg = Config()

        # For external apps, don't use alembic.ini (it has the wrong database URL)
        # Instead, use the database URL from core project settings
        if app_metadata.app_type.value == "external":
            # Set config_file_name to None to prevent Alembic from reading alembic.ini
            # This ensures we use the database URL from settings
            alembic_cfg.config_file_name = None

        # Set script location (primary directory for this app)
        alembic_cfg.set_main_option("script_location", str(migration_path))

        # Set version table
        version_table = VersionTableManager.get_version_table(
            app_metadata.app_type,
            app_metadata.name,
        )
        alembic_cfg.set_main_option("version_table", version_table)

        # Internal apps use core's migration directory - no special handling needed
        # External apps have their own isolated migration directories

        # Set database URL from settings (core project's database)
        settings = get_settings()
        alembic_cfg.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

        return alembic_cfg
