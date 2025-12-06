"""
App resolver - resolves app entries from config to actual app locations.
"""

from __future__ import annotations

import importlib
from dataclasses import dataclass
from pathlib import Path

from fastappkit.core.types import AppType, detect_app_type
from fastappkit.exceptions import AppLoadError


@dataclass
class AppInfo:
    """Information about a resolved app."""

    name: str
    entry: str  # Original entry from config
    app_type: AppType
    import_path: str  # Python import path (e.g., "apps.blog" or "fastapi_blog")
    filesystem_path: Path | None = None  # Filesystem path if applicable
    package_name: str | None = None  # Package name for pip-installed apps


class AppResolver:
    """Resolves app entries from config to app locations."""

    def resolve(self, entry: str, project_root: Path | None = None) -> AppInfo:
        """
        Resolve an app entry to AppInfo.

        Resolution order:
        1. Check if entry matches internal app pattern (apps.*)
        2. Try as dotted import (Python package name)

        Args:
            entry: App entry from config (e.g., "apps.blog", "fastapi_blog")
            project_root: Root directory of the project (for internal apps)

        Returns:
            AppInfo: Resolved app information

        Raises:
            AppLoadError: If app cannot be resolved

        Note:
            External apps must be installed via pip (use "pip install -e /path/to/app"
            for local development). Filesystem paths are not supported.
        """
        if project_root is None:
            project_root = Path.cwd()

        # Step 1: Check internal app pattern (apps.*)
        # If entry matches apps.* pattern, it must be an internal app - handle it here
        if entry.startswith("apps."):
            app_name = entry.split(".", 1)[1]  # Get part after "apps."
            apps_dir = project_root / "apps" / app_name

            if not apps_dir.exists():
                raise AppLoadError(
                    entry,
                    "resolve",
                    f"Internal app directory not found: {apps_dir}",
                )

            if not (apps_dir / "__init__.py").exists():
                raise AppLoadError(
                    entry,
                    "resolve",
                    f"App directory is not a Python package (missing __init__.py): {apps_dir}",
                )

            return AppInfo(
                name=app_name,
                entry=entry,
                app_type=AppType.INTERNAL,
                import_path=entry,
                filesystem_path=apps_dir,
            )

        # Step 2: Try as dotted import (Python package)
        try:
            module = importlib.import_module(entry)
            module_path: Path | None = None
            if hasattr(module, "__file__") and module.__file__:
                module_path = Path(module.__file__).parent

            # Determine app type
            app_type = detect_app_type(entry, module_path)

            return AppInfo(
                name=entry.split(".")[-1],  # Use last part as name
                entry=entry,
                app_type=app_type,
                import_path=entry,
                filesystem_path=module_path,
                package_name=entry if app_type == AppType.EXTERNAL else None,
            )
        except ImportError:
            pass  # Continue to error handling

        # If we get here, couldn't resolve
        raise AppLoadError(
            entry,
            "resolve",
            f"Could not resolve app entry: {entry}. "
            "It should be either a Python package name (pip-installed) or apps.<name> pattern. "
            "For local development, use 'pip install -e /path/to/app' to install the package.",
        )
