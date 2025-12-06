"""
Autogenerate migrations - creates migration files from model changes.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from alembic import command
from sqlalchemy import MetaData

from fastappkit.core.metadata import MetadataCollector
from fastappkit.core.registry import AppMetadata
from fastappkit.core.types import AppType
from fastappkit.migrations.context import MigrationContextBuilder

if TYPE_CHECKING:
    from fastappkit.core.registry import AppRegistry


class Autogenerate:
    """Generates migration files automatically from model changes."""

    def __init__(self) -> None:
        """Initialize autogenerate."""
        self.context_builder = MigrationContextBuilder()
        self.metadata_collector = MetadataCollector()

    def generate(
        self,
        app_metadata: AppMetadata,
        message: str,
        migration_path: Path | None = None,
        target_metadata: MetaData | None = None,
        registry: AppRegistry | None = None,
    ) -> Path:
        """
        Generate a migration file for an app.

        Args:
            app_metadata: App metadata
            message: Migration message
            migration_path: Path to migration directory
            target_metadata: Target metadata (if None, collects from app)
            registry: Optional registry (for internal apps to see full metadata)

        Returns:
            Path to generated migration file

        Raises:
            ValueError: If migration cannot be generated
        """
        # For internal apps, use core's migration directory (passed as migration_path)
        # For external apps, use their own migrations_path
        if migration_path is None:
            if app_metadata.app_type == AppType.INTERNAL:
                # Internal apps use core migrations - migration_path must be passed from CLI
                raise ValueError(
                    f"Internal app '{app_metadata.name}' requires migration_path (should be core/db/migrations)"
                )
            else:
                # External apps must have migrations_path
                if not app_metadata.migrations_path:
                    raise ValueError(f"App '{app_metadata.name}' has no migrations_path")
                migration_path = Path(app_metadata.migrations_path)

        # Determine target metadata
        if target_metadata is None:
            # For internal apps, use full project metadata
            # For external apps, use only app's metadata
            if app_metadata.app_type == AppType.INTERNAL and registry:
                # Collect metadata from all internal apps
                all_metadata = self.metadata_collector.collect_all_metadata(registry)
                # Merge internal app metadata (simplified - in practice might need more logic)
                if all_metadata:
                    target_metadata = list(all_metadata.values())[0]  # Use first, or merge
            else:
                # External app or no registry - use only app's metadata
                target_metadata = self.metadata_collector.collect_metadata(app_metadata)

        # Build Alembic config
        # For internal apps, migration_path is core/db/migrations (no special handling needed)
        alembic_cfg = self.context_builder.build_alembic_config(
            app_metadata,
            migration_path,
        )

        # Set target metadata in config (for autogenerate)
        if target_metadata:
            alembic_cfg.attributes["target_metadata"] = target_metadata

        # Generate migration
        try:
            # Alembic revision command doesn't return path directly
            # We need to find the generated file after creation
            command.revision(
                alembic_cfg,
                autogenerate=True,
                message=message,
            )

            # Find the latest migration file (should be the one we just created)
            versions_dir = migration_path / "versions"
            if not versions_dir.exists():
                versions_dir.mkdir(parents=True, exist_ok=True)

            migration_files = sorted(
                versions_dir.glob("*.py"),
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )

            if migration_files:
                return migration_files[0]  # Most recently created
            else:
                raise ValueError("Migration file was not created")
        except Exception as e:
            raise ValueError(f"Failed to generate migration: {e}") from e
