"""
Base exception classes for fastappkit.
"""

from __future__ import annotations


class FastAppKitError(Exception):
    """Base exception for all fastappkit errors."""

    pass


class AppLoadError(FastAppKitError):
    """Raised when an app fails to load."""

    def __init__(
        self,
        app_name: str,
        stage: str,
        message: str,
        original_error: Exception | None = None,
    ):
        self.app_name = app_name
        self.stage = stage
        self.original_error = original_error
        super().__init__(f"Failed to load app '{app_name}' at stage '{stage}': {message}")


class ValidationError(FastAppKitError):
    """Raised when validation fails."""

    def __init__(self, message: str, errors: list[str] | None = None):
        self.errors = errors or []
        super().__init__(message)


class MigrationError(FastAppKitError):
    """Raised when migration operations fail."""

    pass


class ConfigError(FastAppKitError):
    """Raised when configuration is invalid or missing."""

    pass
