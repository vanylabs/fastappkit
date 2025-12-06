"""
Migration validator - validates app migration setup.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastappkit.core.types import AppType
from fastappkit.validation.manifest import ValidationResult


class MigrationValidator:
    """Validates app migration configuration."""

    def validate(
        self,
        app_path: Path,
        app_type: AppType,
        manifest: dict[str, Any],
    ) -> ValidationResult:
        """
        Validate migration setup for an app.

        For external apps:
        - Check migrations/ folder exists
        - Check migrations/env.py exists
        - Verify version table in env.py matches expected

        Args:
            app_path: Path to app directory
            app_type: Type of app (internal or external)
            manifest: App manifest dictionary

        Returns:
            ValidationResult: Result with errors and warnings
        """
        result = ValidationResult()

        migrations_path_str = manifest.get("migrations")
        if not migrations_path_str:
            if app_type == AppType.EXTERNAL:
                result.add_error("External apps must specify 'migrations' in manifest")
            return result

        migrations_path = app_path / migrations_path_str
        if not migrations_path.exists():
            result.add_error(f"Migrations folder not found: {migrations_path}")
            return result

        # For external apps, check env.py exists
        if app_type == AppType.EXTERNAL:
            env_py = migrations_path / "env.py"
            if not env_py.exists():
                result.add_error(
                    f"migrations/env.py not found (required for external apps): {env_py}"
                )

            # Check version table in env.py
            if env_py.exists():
                try:
                    content = env_py.read_text(encoding="utf-8")
                    app_name = manifest.get("name", "unknown")

                    # Check if version_table is set correctly
                    expected_table = f"alembic_version_{app_name}"
                    if (
                        f'version_table", "{expected_table}' in content
                        or f"version_table', '{expected_table}" in content
                    ):
                        # Correct version table
                        pass
                    elif (
                        'version_table", "alembic_version"' in content
                        or "version_table', 'alembic_version'" in content
                    ):
                        result.add_error(
                            f"External app uses shared version table 'alembic_version'. "
                            f"Should use '{expected_table}'"
                        )
                    else:
                        result.add_warning(
                            f"Could not verify version table in env.py. "
                            f"External apps should use '{expected_table}'"
                        )
                except Exception as e:
                    result.add_warning(f"Could not read migrations/env.py: {e}")

        # Check versions directory exists
        versions_dir = migrations_path / "versions"
        if not versions_dir.exists():
            result.add_warning(f"Migrations versions directory not found: {versions_dir}")

        return result
