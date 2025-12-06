"""
App type definitions and detection.
"""

from __future__ import annotations

from enum import Enum
from pathlib import Path


class AppType(Enum):
    """App type enumeration."""

    INTERNAL = "internal"
    EXTERNAL = "external"


def detect_app_type(entry: str, resolved_path: Path | None = None) -> AppType:
    """
    Detect if an app is internal or external based on entry string and path.

    Args:
        entry: App entry string from config (e.g., "apps.blog", "fastapi_blog")
        resolved_path: Optional resolved filesystem path (from imported module)

    Returns:
        AppType: INTERNAL or EXTERNAL
    """
    # Check if entry matches internal app pattern
    if entry.startswith("apps."):
        return AppType.INTERNAL

    # If we have a resolved path, check if it's under apps/ directory
    if resolved_path:
        try:
            # Check if path is under an "apps" directory
            parts = resolved_path.parts
            if "apps" in parts:
                # Check if it's directly under apps/ (apps/<name>)
                apps_index = parts.index("apps")
                if apps_index + 1 < len(parts):
                    return AppType.INTERNAL
        except (ValueError, AttributeError):
            pass

    # Default to external
    return AppType.EXTERNAL
