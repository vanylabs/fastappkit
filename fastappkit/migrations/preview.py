"""
Migration preview - shows SQL without executing.
"""

from __future__ import annotations

import io
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from alembic import command

from fastappkit.core.registry import AppMetadata
from fastappkit.migrations.context import MigrationContextBuilder

if TYPE_CHECKING:
    from fastappkit.core.registry import AppRegistry


class MigrationPreview:
    """Preview SQL for migrations without executing."""

    def __init__(self) -> None:
        """Initialize preview."""
        self.context_builder = MigrationContextBuilder()

    def preview(
        self,
        app_metadata: AppMetadata,
        revision: str = "head",
        migration_path: Path | None = None,
        project_root: Path | None = None,
        registry: "AppRegistry" | None = None,
    ) -> str:
        """
        Preview SQL for pending migrations.

        Args:
            app_metadata: App metadata
            revision: Target revision (default: "head")
            migration_path: Path to migration directory
            project_root: Root directory of the project (needed for internal apps)
            registry: Optional AppRegistry (needed for internal apps)

        Returns:
            SQL string that would be executed
        """
        alembic_cfg = self.context_builder.build_alembic_config(
            app_metadata, migration_path, project_root, registry
        )

        # Use Alembic's --sql mode to generate SQL without executing
        # We'll capture stdout
        old_stdout = sys.stdout
        sys.stdout = buffer = io.StringIO()

        try:
            command.upgrade(alembic_cfg, revision, sql=True)
            sql_output = buffer.getvalue()
        finally:
            sys.stdout = old_stdout

        return sql_output
