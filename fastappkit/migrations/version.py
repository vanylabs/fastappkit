"""
Version table management for migrations.

Handles shared version table for internal apps and per-app version tables for external apps.
"""

from __future__ import annotations

from fastappkit.core.types import AppType


class VersionTableManager:
    """Manages Alembic version table names for different app types."""

    SHARED_VERSION_TABLE = "alembic_version"

    @staticmethod
    def get_version_table(app_type: AppType, app_name: str) -> str:
        """
        Get version table name for an app.

        Args:
            app_type: AppType (INTERNAL or EXTERNAL)
            app_name: App name

        Returns:
            Version table name string
        """
        if app_type == AppType.INTERNAL:
            return VersionTableManager.SHARED_VERSION_TABLE
        else:
            return f"alembic_version_{app_name}"

    @staticmethod
    def validate_version_table(app_type: AppType, app_name: str, expected_table: str) -> bool:
        """
        Validate that an app is using the correct version table.

        Args:
            app_type: AppType (INTERNAL or EXTERNAL)
            app_name: App name
            expected_table: Expected version table name

        Returns:
            True if correct, False otherwise
        """
        correct_table = VersionTableManager.get_version_table(app_type, app_name)
        return expected_table == correct_table
