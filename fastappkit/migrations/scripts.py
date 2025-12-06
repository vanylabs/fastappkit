"""
Script directory management for Alembic migrations.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from alembic.script import ScriptDirectory

from fastappkit.core.types import AppType
from fastappkit.migrations.order import MigrationOrderer

if TYPE_CHECKING:
    from fastappkit.core.registry import AppRegistry


def build_script_directory(migration_path: Path) -> ScriptDirectory:
    """
    Build Alembic ScriptDirectory for a migration folder.

    Args:
        migration_path: Path to migration directory (should contain versions/ subdirectory)

    Returns:
        ScriptDirectory instance

    Raises:
        ValueError: If migration path is invalid
    """
    if not migration_path.exists():
        raise ValueError(f"Migration path does not exist: {migration_path}")

    if not migration_path.is_dir():
        raise ValueError(f"Migration path is not a directory: {migration_path}")

    # Alembic expects the migration directory (not versions/)
    try:
        script_dir = ScriptDirectory(str(migration_path))
        return script_dir
    except Exception as e:
        raise ValueError(f"Failed to create ScriptDirectory from {migration_path}: {e}") from e


def get_shared_migration_directories(
    project_root: Path, registry: "AppRegistry" | None = None
) -> list[Path]:
    """
    Get all migration directories that share the version table (core + internal apps).

    Args:
        project_root: Root directory of the project
        registry: Optional AppRegistry to get internal app migration paths

    Returns:
        List of migration directory paths (core first, then internal apps)
    """
    directories: list[Path] = []

    # Add core migrations directory
    core_path = MigrationOrderer.get_core_migration_path(project_root)
    if core_path.exists():
        directories.append(core_path)

    # Add internal app migration directories
    if registry:
        for app_metadata in registry.list():
            if app_metadata.app_type == AppType.INTERNAL and app_metadata.migrations_path:
                app_path = Path(app_metadata.migrations_path)
                if app_path.exists():
                    directories.append(app_path)

    return directories
