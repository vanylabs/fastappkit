"""
Tests for MigrationRunner.

Tests focus on:
- Upgrade migrations
- Downgrade migrations
- Getting current revision
- Error handling
- SQLite in-memory database usage
"""

import pytest
from pathlib import Path

from fastappkit.conf import set_settings
from fastappkit.core.registry import AppMetadata
from fastappkit.core.types import AppType
from fastappkit.exceptions import MigrationError
from fastappkit.migrations.runner import MigrationRunner
from tests.conftest import TestSettings


class TestMigrationRunner:
    """Tests for MigrationRunner class."""

    def test_upgrade_requires_valid_migration_path(
        self, temp_project: Path, test_settings: TestSettings
    ) -> None:
        """upgrade() requires valid migration path."""
        test_settings.database_url = "sqlite:///:memory:"
        set_settings(test_settings)

        # Create app metadata without migrations_path
        app_metadata = AppMetadata(
            name="test_app",
            app_type=AppType.EXTERNAL,
            import_path="test_app",
            migrations_path=None,  # No migrations path
        )

        runner = MigrationRunner()

        with pytest.raises((ValueError, MigrationError)):
            runner.upgrade(app_metadata, "head")

    def test_get_current_revision_handles_missing_migrations_path(
        self, temp_project: Path, test_settings: TestSettings
    ) -> None:
        """get_current_revision() handles missing migrations path gracefully."""
        test_settings.database_url = "sqlite:///:memory:"
        set_settings(test_settings)

        # Create app metadata with invalid migrations_path
        app_metadata = AppMetadata(
            name="test_app",
            app_type=AppType.EXTERNAL,
            import_path="test_app",
            migrations_path=str(temp_project / "nonexistent" / "migrations"),
        )

        runner = MigrationRunner()
        # Should return None or raise error gracefully
        current_rev = runner.get_current_revision(app_metadata)
        # When migrations path doesn't exist, should return None
        assert current_rev is None

    def test_upgrade_raises_error_on_invalid_migration(
        self, temp_project: Path, test_settings: TestSettings
    ) -> None:
        """upgrade() raises MigrationError on invalid migration."""
        test_settings.database_url = "sqlite:///:memory:"
        set_settings(test_settings)

        migrations_path = temp_project / "migrations"
        versions_path = migrations_path / "versions"
        versions_path.mkdir(parents=True)

        # Create invalid migration file
        migration_file = versions_path / "001_broken.py"
        migration_file.write_text(
            '''"""Broken migration."""
def upgrade():
    raise RuntimeError("Migration failed")

def downgrade():
    pass
'''
        )

        env_py = migrations_path / "env.py"
        env_py.write_text(
            '''"""Migration environment."""
from alembic import context
from sqlalchemy import engine_from_config
from fastappkit.conf import get_settings

config = context.config
settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.database_url)
config.set_main_option("version_table", "alembic_version")

target_metadata = None

def run_migrations_online():
    connectable = engine_from_config(
        {"sqlalchemy.url": settings.database_url},
        prefix="sqlalchemy.",
        poolclass=None,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            version_table=config.get_main_option("version_table"),
        )
        with context.begin_transaction():
            context.run_migrations()

run_migrations_online()
'''
        )

        script_mako = migrations_path / "script.py.mako"
        script_mako.write_text("""${upgrades if upgrades else "pass"}""")

        app_metadata = AppMetadata(
            name="test_app",
            app_type=AppType.EXTERNAL,
            import_path="test_app",
            migrations_path=str(migrations_path),
        )

        runner = MigrationRunner()

        with pytest.raises(MigrationError) as exc_info:
            runner.upgrade(app_metadata, "head")

        assert "Failed to upgrade" in str(exc_info.value)
        assert "test_app" in str(exc_info.value)
