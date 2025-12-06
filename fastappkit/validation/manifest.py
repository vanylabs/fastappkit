"""
Manifest validator - validates app manifest files.
"""

from __future__ import annotations

from typing import Any


class ValidationResult:
    """Result of a validation check."""

    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.is_valid: bool = True

    def add_error(self, message: str) -> None:
        """Add an error message."""
        self.errors.append(message)
        self.is_valid = False

    def add_warning(self, message: str) -> None:
        """Add a warning message."""
        self.warnings.append(message)

    def __bool__(self) -> bool:
        """Return True if validation passed."""
        return self.is_valid


class ManifestValidator:
    """Validates app manifest files."""

    def validate(self, manifest: dict[str, Any], app_name: str) -> ValidationResult:
        """
        Validate manifest has required fields and correct format.

        Args:
            manifest: Manifest dictionary
            app_name: Name of the app (for error messages)

        Returns:
            ValidationResult: Result with errors and warnings
        """
        result = ValidationResult()

        # Required fields
        required_fields = ["name", "version", "entrypoint"]
        for field in required_fields:
            if field not in manifest:
                result.add_error(f"Missing required field: {field}")

        # Validate version format (basic semver check)
        if "version" in manifest:
            version = manifest["version"]
            if not isinstance(version, str):
                result.add_error("'version' must be a string")
            elif not any(c.isdigit() for c in version):
                result.add_warning(f"Version format may be invalid: {version}")

        # Validate entrypoint format
        if "entrypoint" in manifest:
            entrypoint = manifest["entrypoint"]
            if not isinstance(entrypoint, str):
                result.add_error("'entrypoint' must be a string")
            elif ":" not in entrypoint:
                result.add_error(
                    f"Invalid entrypoint format (expected 'module:function'): {entrypoint}"
                )

        # Check for unknown keys (warn only)
        known_keys = {
            "name",
            "version",
            "entrypoint",
            "migrations",
            "models_module",
            "route_prefix",
            "per_app_migrations",
            "requires_core",
        }
        unknown_keys = set(manifest.keys()) - known_keys
        if unknown_keys:
            result.add_warning(f"Unknown manifest keys: {', '.join(unknown_keys)}")

        return result
