"""
Tests for MigrationValidator.

Tests focus on:
- Validating migration setup for external apps
- Checking migrations folder and env.py existence
- Validating version table configuration
- Edge cases that would break if implementation changes
"""

from pathlib import Path
from fastappkit.core.types import AppType
from fastappkit.validation.migrations import MigrationValidator
from tests.fixtures import ExternalAppFactory


class TestMigrationValidator:
    """Tests for MigrationValidator class."""

    def test_validate_internal_app_without_migrations_passes(self, temp_project: Path) -> None:
        """validate() passes for internal app without migrations in manifest."""
        validator = MigrationValidator()
        app_path = temp_project / "apps" / "blog"
        app_path.mkdir(parents=True)

        manifest = {
            "name": "blog",
            "version": "1.0.0",
            "entrypoint": "apps.blog:register",
        }

        result = validator.validate(app_path, AppType.INTERNAL, manifest)

        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_external_app_without_migrations_fails(self, temp_project: Path) -> None:
        """validate() fails for external app without migrations in manifest."""
        validator = MigrationValidator()
        app_path = ExternalAppFactory.create(
            temp_project.parent, "external_app", with_migrations=False
        )

        manifest = {
            "name": "external_app",
            "version": "1.0.0",
            "entrypoint": "external_app:register",
        }

        result = validator.validate(app_path, AppType.EXTERNAL, manifest)

        assert result.is_valid is False
        assert len(result.errors) > 0
        assert any("migrations" in error.lower() for error in result.errors)

    def test_validate_external_app_with_missing_migrations_folder_fails(
        self, temp_project: Path
    ) -> None:
        """validate() fails if migrations folder doesn't exist."""
        validator = MigrationValidator()
        app_path = ExternalAppFactory.create(
            temp_project.parent, "external_app", with_migrations=False
        )

        manifest = {
            "name": "external_app",
            "version": "1.0.0",
            "entrypoint": "external_app:register",
            "migrations": "migrations",
        }

        result = validator.validate(app_path, AppType.EXTERNAL, manifest)

        assert result.is_valid is False
        assert len(result.errors) > 0
        assert any("not found" in error.lower() for error in result.errors)

    def test_validate_external_app_with_missing_env_py_fails(self, temp_project: Path) -> None:
        """validate() fails if migrations/env.py doesn't exist for external app."""
        validator = MigrationValidator()
        app_path = ExternalAppFactory.create(
            temp_project.parent, "external_app", with_migrations=False
        )

        # Create migrations folder but no env.py
        migrations_path = app_path / "migrations"
        migrations_path.mkdir()

        manifest = {
            "name": "external_app",
            "version": "1.0.0",
            "entrypoint": "external_app:register",
            "migrations": "migrations",
        }

        result = validator.validate(app_path, AppType.EXTERNAL, manifest)

        assert result.is_valid is False
        assert len(result.errors) > 0
        assert any("env.py" in error.lower() for error in result.errors)

    def test_validate_external_app_with_correct_version_table_passes(
        self, temp_project: Path
    ) -> None:
        """validate() passes for external app with correct version table."""
        validator = MigrationValidator()
        app_path = ExternalAppFactory.create(
            temp_project.parent, "external_app", with_migrations=True
        )

        # Create env.py with correct version table
        migrations_path = app_path / "migrations"
        env_py = migrations_path / "env.py"
        env_py.write_text(
            '''"""Migrations env.py."""
from fastappkit.migrations.context import get_context

context = get_context()
context.config.set_main_option("version_table", "alembic_version_external_app")
'''
        )

        manifest = {
            "name": "external_app",
            "version": "1.0.0",
            "entrypoint": "external_app:register",
            "migrations": "migrations",
        }

        result = validator.validate(app_path, AppType.EXTERNAL, manifest)

        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_external_app_with_shared_version_table_fails(
        self, temp_project: Path
    ) -> None:
        """validate() fails if external app uses shared version table."""
        validator = MigrationValidator()
        app_path = ExternalAppFactory.create(
            temp_project.parent, "external_app", with_migrations=True
        )

        # Create env.py with shared version table (should fail)
        migrations_path = app_path / "migrations"
        env_py = migrations_path / "env.py"
        env_py.write_text(
            '''"""Migrations env.py with shared table."""
from fastappkit.migrations.context import get_context

context = get_context()
context.config.set_main_option("version_table", "alembic_version")
'''
        )

        manifest = {
            "name": "external_app",
            "version": "1.0.0",
            "entrypoint": "external_app:register",
            "migrations": "migrations",
        }

        result = validator.validate(app_path, AppType.EXTERNAL, manifest)

        assert result.is_valid is False
        assert len(result.errors) > 0
        assert any(
            "shared" in error.lower() or "alembic_version" in error.lower()
            for error in result.errors
        )

    def test_validate_external_app_with_unverifiable_version_table_warns(
        self, temp_project: Path
    ) -> None:
        """validate() warns if version table cannot be verified."""
        validator = MigrationValidator()
        app_path = ExternalAppFactory.create(
            temp_project.parent, "external_app", with_migrations=True
        )

        # Create env.py without version table setting
        migrations_path = app_path / "migrations"
        env_py = migrations_path / "env.py"
        env_py.write_text(
            '''"""Migrations env.py without version table."""
from fastappkit.migrations.context import get_context

context = get_context()
# No version_table setting
'''
        )

        manifest = {
            "name": "external_app",
            "version": "1.0.0",
            "entrypoint": "external_app:register",
            "migrations": "migrations",
        }

        result = validator.validate(app_path, AppType.EXTERNAL, manifest)

        # Should warn but not fail (env.py exists)
        assert result.is_valid is True
        assert len(result.warnings) > 0
        assert any("version table" in warning.lower() for warning in result.warnings)

    def test_validate_warns_if_versions_directory_missing(self, temp_project: Path) -> None:
        """validate() warns if migrations/versions directory doesn't exist."""
        validator = MigrationValidator()
        app_path = ExternalAppFactory.create(
            temp_project.parent, "external_app", with_migrations=True
        )

        # Remove versions directory if it exists
        migrations_path = app_path / "migrations"
        versions_dir = migrations_path / "versions"
        if versions_dir.exists():
            versions_dir.rmdir()

        manifest = {
            "name": "external_app",
            "version": "1.0.0",
            "entrypoint": "external_app:register",
            "migrations": "migrations",
        }

        result = validator.validate(app_path, AppType.EXTERNAL, manifest)

        assert len(result.warnings) > 0
        assert any("versions" in warning.lower() for warning in result.warnings)
