"""
Manifest loader - loads app metadata from fastappkit.toml.
"""

from __future__ import annotations

import importlib
import tomllib
from pathlib import Path
from typing import TYPE_CHECKING, Any

from fastappkit.core.types import AppType
from fastappkit.exceptions import AppLoadError, ValidationError

if TYPE_CHECKING:
    from fastappkit.core.resolver import AppInfo


class ManifestLoader:
    """Loads and validates app manifests."""

    def load_manifest(self, app_info: AppInfo) -> dict[str, Any]:
        """
        Load manifest for an app.

        For external apps:
        - ONLY fastappkit.toml (in package directory - included in pip packages)
        - No fallbacks

        For internal apps:
        - Always return inferred manifest (uses register entrypoint)
        - No manifest file needed

        Args:
            app_info: AppInfo object with app location

        Returns:
            dict: Parsed manifest

        Raises:
            AppLoadError: If manifest is missing or invalid (external apps only)
        """
        # Determine search path
        if app_info.filesystem_path:
            search_path = app_info.filesystem_path
        else:
            # For pip-installed packages, try to find package location
            try:
                module = importlib.import_module(app_info.import_path)
                if hasattr(module, "__file__") and module.__file__:
                    search_path = Path(module.__file__).parent
                else:
                    raise AppLoadError(
                        app_info.name,
                        "manifest",
                        f"Cannot determine package location for {app_info.import_path}",
                    )
            except ImportError as e:
                raise AppLoadError(
                    app_info.name,
                    "manifest",
                    f"Failed to import app module: {e}",
                ) from e

        # For external apps, ONLY use fastappkit.toml (included in package when published)
        if app_info.app_type == AppType.EXTERNAL:
            fastappkit_toml_path = search_path / "fastappkit.toml"
            if fastappkit_toml_path.exists():
                try:
                    with open(fastappkit_toml_path, "rb") as f:
                        data = tomllib.load(f)
                    # Extract [tool.fastappkit] section
                    manifest_data = data.get("tool", {}).get("fastappkit", {})
                    return self._validate_manifest(manifest_data, app_info)
                except Exception as e:
                    raise AppLoadError(
                        app_info.name,
                        "manifest",
                        f"Failed to parse fastappkit.toml: {e}",
                    ) from e

            # External apps must have fastappkit.toml
            raise AppLoadError(
                app_info.name,
                "manifest",
                f"fastappkit.toml not found in {search_path}. "
                f"External apps must have fastappkit.toml in the package directory.",
            )

        # For internal apps, always return inferred manifest (no file needed)
        # Internal apps always use the register entrypoint
        return {
            "name": app_info.name,
            "version": "0.1.0",  # Default version
            "entrypoint": f"{app_info.import_path}:register",
        }

    def _validate_manifest(self, manifest: dict[str, Any], app_info: AppInfo) -> dict[str, Any]:
        """
        Validate manifest has required fields.

        Args:
            manifest: Raw manifest dict
            app_info: AppInfo for context

        Returns:
            dict: Validated manifest

        Raises:
            ValidationError: If manifest is invalid
        """
        errors = []

        # Required fields
        required_fields = ["name", "version", "entrypoint"]
        for field in required_fields:
            if field not in manifest:
                errors.append(f"Missing required field: {field}")

        # Validate version format (basic semver check)
        if "version" in manifest:
            version = manifest["version"]
            if not isinstance(version, str):
                errors.append("'version' must be a string")
            # Basic semver validation (can be enhanced)
            elif not any(c.isdigit() for c in version):
                errors.append(f"Invalid version format: {version}")

        # Validate entrypoint format
        if "entrypoint" in manifest:
            entrypoint = manifest["entrypoint"]
            if not isinstance(entrypoint, str):
                errors.append("'entrypoint' must be a string")
            elif ":" not in entrypoint:
                errors.append(
                    f"Invalid entrypoint format (expected 'module:function'): {entrypoint}"
                )

        if errors:
            raise ValidationError(
                f"Manifest validation failed for app '{app_info.name}': " + "; ".join(errors),
                errors=errors,
            )

        return manifest
