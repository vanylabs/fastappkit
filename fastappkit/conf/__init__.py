"""Configuration module for settings and config file parsing."""

from __future__ import annotations

import importlib
import sys
import threading
from pathlib import Path

from fastappkit.conf.protocol import SettingsProtocol

# Thread-safe singleton for settings instance
_settings_lock = threading.Lock()
_settings_instance: SettingsProtocol | None = None


def ensure_settings_loaded(project_root: Path) -> None:
    """
    Ensure project settings are loaded by importing core.app.

    This will execute core.app which should initialize FastAppKit
    with project's Settings, setting them globally via set_settings().

    Args:
        project_root: Root directory of the project

    Raises:
        RuntimeError: If core.app cannot be imported or settings not initialized
    """
    # If already loaded, skip
    if _settings_instance is not None:
        return

    # Add project root to path
    project_root_str = str(project_root)
    if project_root_str not in sys.path:
        sys.path.insert(0, project_root_str)

    try:
        # Import core.app - this executes the module
        # which should contain: kit = FastAppKit(settings=Settings())
        importlib.import_module("core.app")
    except ImportError as e:
        raise RuntimeError(
            f"Failed to import core.app from {project_root}. "
            "Make sure you're in a fastappkit project with core/app.py that initializes FastAppKit."
        ) from e
    except Exception as e:
        raise RuntimeError(
            f"Error loading settings from core.app: {e}. "
            "Make sure core/app.py initializes FastAppKit with Settings."
        ) from e

    # Verify settings were actually set
    if _settings_instance is None:
        raise RuntimeError(
            "Settings not initialized after importing core.app. "
            "Make sure core/app.py contains: kit = FastAppKit(settings=Settings())"
        )


def get_settings() -> SettingsProtocol:
    """
    Get the current settings instance.

    Settings must be initialized first by:
    - Calling ensure_settings_loaded(project_root) (for CLI/migrations)
    - Or importing core.app (which initializes FastAppKit)
    - Or calling set_settings() directly

    Returns:
        SettingsProtocol: The current settings instance

    Raises:
        RuntimeError: If settings not initialized
    """
    global _settings_instance

    if _settings_instance is None:
        raise RuntimeError(
            "Settings not initialized. "
            "Call ensure_settings_loaded(project_root) or import core.app first."
        )

    return _settings_instance


def set_settings(settings: SettingsProtocol) -> None:
    """
    Set the global settings instance.

    This should be called once during application initialization,
    typically by FastAppKit.__init__().

    Args:
        settings: The Settings instance to use globally
    """
    global _settings_instance

    with _settings_lock:
        _settings_instance = settings


def reset_settings() -> None:
    """
    Reset the global settings instance (useful for testing).
    """
    global _settings_instance

    with _settings_lock:
        _settings_instance = None


__all__ = [
    "SettingsProtocol",
    "get_settings",
    "set_settings",
    "reset_settings",
    "ensure_settings_loaded",
]
