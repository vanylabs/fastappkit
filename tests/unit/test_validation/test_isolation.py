"""
Tests for IsolationValidator.

Tests focus on:
- Detecting internal app imports in external apps
- Detecting core imports (excluding fastappkit)
- Skipping internal apps (no validation needed)
- Edge cases that would break if implementation changes
"""

from pathlib import Path
from fastappkit.core.types import AppType
from fastappkit.validation.isolation import IsolationValidator
from tests.fixtures import ExternalAppFactory


class TestIsolationValidator:
    """Tests for IsolationValidator class."""

    def test_validate_internal_app_skips_validation(self, temp_project: Path) -> None:
        """validate() skips validation for internal apps."""
        validator = IsolationValidator()
        app_path = temp_project / "apps" / "blog"
        app_path.mkdir(parents=True)

        result = validator.validate(app_path, AppType.INTERNAL, None, temp_project)

        assert result.is_valid is True
        assert len(result.errors) == 0
        assert len(result.warnings) == 0

    def test_validate_external_app_with_no_files_warns(self, temp_project: Path) -> None:
        """validate() warns if external app has no Python files."""
        validator = IsolationValidator()
        app_path = temp_project.parent / "external_app"
        app_path.mkdir()

        result = validator.validate(app_path, AppType.EXTERNAL, None, temp_project)

        assert result.is_valid is True
        assert len(result.warnings) > 0
        assert any("no python files" in warning.lower() for warning in result.warnings)

    def test_validate_external_app_with_valid_imports_passes(self, temp_project: Path) -> None:
        """validate() passes for external app with only valid imports."""
        validator = IsolationValidator()
        app_path = ExternalAppFactory.create(
            temp_project.parent, "external_app", with_migrations=False
        )

        # Create a file with only valid imports
        (app_path / "router.py").write_text(
            '''"""Router with valid imports."""
from fastapi import APIRouter
from typing import Dict

router = APIRouter()
'''
        )

        result = validator.validate(app_path, AppType.EXTERNAL, None, temp_project)

        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_external_app_imports_internal_app_fails(self, temp_project: Path) -> None:
        """validate() fails when external app imports from internal app."""
        validator = IsolationValidator()

        # Create internal app structure that can be detected
        apps_dir = temp_project / "apps"
        apps_dir.mkdir(parents=True, exist_ok=True)
        (apps_dir / "__init__.py").write_text('"""Apps package."""')
        internal_app = apps_dir / "blog"
        internal_app.mkdir(exist_ok=True)
        (internal_app / "__init__.py").write_text('"""Internal app."""')

        # Create external app that imports internal app using project-specific import
        app_path = ExternalAppFactory.create(
            temp_project.parent, "external_app", with_migrations=False
        )
        project_name = temp_project.name
        (app_path / "router.py").write_text(
            f'''"""Router importing internal app."""
from {project_name}.apps.blog import something  # Should fail
from fastapi import APIRouter

router = APIRouter()
'''
        )

        result = validator.validate(app_path, AppType.EXTERNAL, None, temp_project)

        assert result.is_valid is False
        assert len(result.errors) > 0
        assert any("internal app" in error.lower() for error in result.errors)

    def test_validate_external_app_imports_project_specific_internal_app_fails(
        self, temp_project: Path
    ) -> None:
        """validate() fails when external app imports project-specific internal app."""
        validator = IsolationValidator()

        # Create external app that imports project-specific internal app
        app_path = ExternalAppFactory.create(
            temp_project.parent, "external_app", with_migrations=False
        )
        project_name = temp_project.name
        (app_path / "router.py").write_text(
            f'''"""Router importing project-specific internal app."""
from {project_name}.apps.blog import something  # Should fail
from fastapi import APIRouter

router = APIRouter()
'''
        )

        result = validator.validate(app_path, AppType.EXTERNAL, None, temp_project)

        assert result.is_valid is False
        assert len(result.errors) > 0
        assert any("internal app" in error.lower() for error in result.errors)

    def test_validate_external_app_imports_fastappkit_allowed(self, temp_project: Path) -> None:
        """validate() allows fastappkit imports in external apps."""
        validator = IsolationValidator()

        app_path = ExternalAppFactory.create(
            temp_project.parent, "external_app", with_migrations=False
        )
        (app_path / "router.py").write_text(
            '''"""Router importing fastappkit."""
from fastappkit.core.types import AppType  # Should be allowed
from fastapi import APIRouter

router = APIRouter()
'''
        )

        result = validator.validate(app_path, AppType.EXTERNAL, None, temp_project)

        assert result.is_valid is True
        # Should not error on fastappkit imports
        assert not any("fastappkit" in error.lower() for error in result.errors)

    def test_validate_skips_migrations_env_py(self, temp_project: Path) -> None:
        """validate() skips migrations/env.py (allowed to import from fastappkit)."""
        validator = IsolationValidator()

        app_path = ExternalAppFactory.create(
            temp_project.parent, "external_app", with_migrations=True
        )

        # Create env.py with internal app import (should be skipped)
        migrations_path = app_path / "migrations"
        env_py = migrations_path / "env.py"
        env_py.write_text(
            '''"""Migrations env.py - allowed to import."""
from apps.blog import something  # Should be skipped
from fastappkit.migrations.context import get_context
'''
        )

        result = validator.validate(app_path, AppType.EXTERNAL, None, temp_project)

        # Should not error because env.py is skipped
        assert result.is_valid is True
        assert not any("internal app" in error.lower() for error in result.errors)

    def test_validate_handles_syntax_errors_gracefully(self, temp_project: Path) -> None:
        """validate() handles syntax errors in Python files gracefully."""
        validator = IsolationValidator()

        app_path = ExternalAppFactory.create(
            temp_project.parent, "external_app", with_migrations=False
        )
        # Create file with syntax error
        (app_path / "broken.py").write_text(
            '''"""File with syntax error."""
def broken(
    # Missing closing parenthesis
'''
        )

        result = validator.validate(app_path, AppType.EXTERNAL, None, temp_project)

        # Should warn but not fail
        assert result.is_valid is True
        assert len(result.warnings) > 0
        assert any(
            "syntax error" in warning.lower() or "parse" in warning.lower()
            for warning in result.warnings
        )

    def test_validate_third_party_imports_allowed(self, temp_project: Path) -> None:
        """validate() allows third-party library imports (e.g., django.apps)."""
        validator = IsolationValidator()

        app_path = ExternalAppFactory.create(
            temp_project.parent, "external_app", with_migrations=False
        )
        (app_path / "router.py").write_text(
            '''"""Router with third-party imports."""
from django.apps import AppConfig  # Should be allowed
from flask.app import Flask  # Should be allowed
from fastapi import APIRouter

router = APIRouter()
'''
        )

        result = validator.validate(app_path, AppType.EXTERNAL, None, temp_project)

        assert result.is_valid is True
        # Should not error on third-party imports
        assert not any("django" in error.lower() for error in result.errors)
        assert not any("flask" in error.lower() for error in result.errors)

    def test_validate_import_from_statement(self, temp_project: Path) -> None:
        """validate() detects imports from 'from X import Y' statements."""
        validator = IsolationValidator()

        # Create internal app structure that can be detected
        apps_dir = temp_project / "apps"
        apps_dir.mkdir(parents=True, exist_ok=True)
        (apps_dir / "__init__.py").write_text('"""Apps package."""')
        internal_app = apps_dir / "blog"
        internal_app.mkdir(exist_ok=True)
        (internal_app / "__init__.py").write_text('"""Internal app."""')

        # Create external app with 'from' import using project-specific import
        app_path = ExternalAppFactory.create(
            temp_project.parent, "external_app", with_migrations=False
        )
        project_name = temp_project.name
        (app_path / "router.py").write_text(
            f'''"""Router with from import."""
from {project_name}.apps.blog import router  # Should fail
from fastapi import APIRouter
'''
        )

        result = validator.validate(app_path, AppType.EXTERNAL, None, temp_project)

        assert result.is_valid is False
        assert len(result.errors) > 0
        assert any("internal app" in error.lower() for error in result.errors)
