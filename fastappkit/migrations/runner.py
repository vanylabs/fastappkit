"""
Migration runner - executes Alembic migrations for apps.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from alembic import command
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from fastappkit.conf import get_settings
from fastappkit.core.registry import AppMetadata
from fastappkit.exceptions import MigrationError
from fastappkit.migrations.context import MigrationContextBuilder

if TYPE_CHECKING:
    from fastappkit.core.registry import AppRegistry


class MigrationRunner:
    """Runs migrations for apps."""

    def __init__(self) -> None:
        """Initialize migration runner."""
        self.context_builder = MigrationContextBuilder()
        self.settings = get_settings()

    def _get_engine(self) -> Engine:
        """Get SQLAlchemy engine from settings."""
        return create_engine(self.settings.DATABASE_URL)

    def upgrade(
        self,
        app_metadata: AppMetadata,
        revision: str = "head",
        migration_path: Path | None = None,
        project_root: Path | None = None,
        registry: "AppRegistry" | None = None,
    ) -> None:
        """
        Upgrade app migrations to a specific revision.

        Args:
            app_metadata: App metadata
            revision: Target revision (default: "head")
            migration_path: Path to migration directory (if None, uses app's migrations_path)
            project_root: Root directory of the project (needed for internal apps)
            registry: Optional AppRegistry (needed for internal apps)

        Raises:
            MigrationError: If migration fails
        """
        try:
            alembic_cfg = self.context_builder.build_alembic_config(
                app_metadata, migration_path, project_root, registry
            )

            # Run upgrade (connection is managed internally by Alembic)
            command.upgrade(alembic_cfg, revision)
        except Exception as e:
            raise MigrationError(
                f"Failed to upgrade migrations for app '{app_metadata.name}': {e}"
            ) from e

    def downgrade(
        self,
        app_metadata: AppMetadata,
        revision: str,
        migration_path: Path | None = None,
        project_root: Path | None = None,
        registry: "AppRegistry" | None = None,
    ) -> None:
        """
        Downgrade app migrations to a specific revision.

        Args:
            app_metadata: App metadata
            revision: Target revision
            migration_path: Path to migration directory
            project_root: Root directory of the project (needed for internal apps)
            registry: Optional AppRegistry (needed for internal apps)

        Raises:
            MigrationError: If migration fails
        """
        try:
            alembic_cfg = self.context_builder.build_alembic_config(
                app_metadata, migration_path, project_root, registry
            )

            # Run downgrade (connection is managed internally by Alembic)
            command.downgrade(alembic_cfg, revision)
        except Exception as e:
            raise MigrationError(
                f"Failed to downgrade migrations for app '{app_metadata.name}': {e}"
            ) from e

    def get_current_revision(
        self,
        app_metadata: AppMetadata,
        migration_path: Path | None = None,
    ) -> str | None:
        """
        Get current migration revision for an app.

        Args:
            app_metadata: App metadata
            migration_path: Path to migration directory

        Returns:
            Current revision string, or None if no migrations applied
        """
        try:
            with self._get_engine().connect() as connection:
                context = self.context_builder.build_context(
                    app_metadata,
                    connection,
                    migration_path=migration_path,
                )
                current_rev = context.get_current_revision()
                return current_rev
        except Exception:
            # If version table doesn't exist or other error, return None
            return None
