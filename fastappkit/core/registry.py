"""
App registry - stores metadata about loaded apps.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterator, List

from fastapi import APIRouter
from sqlalchemy import MetaData

from fastappkit.core.types import AppType


@dataclass
class AppMetadata:
    """Metadata for a registered app."""

    name: str
    app_type: AppType
    import_path: str
    filesystem_path: str | None = None
    router: APIRouter | None = None
    metadata: MetaData | None = None  # SQLAlchemy metadata
    migrations_path: str | None = None
    prefix: str = ""  # Route prefix (defaults to /<appname>)
    manifest: dict[str, Any] = field(default_factory=dict)  # Full manifest dict


class AppRegistry:
    """Registry for storing app metadata."""

    def __init__(self) -> None:
        """Initialize empty registry."""
        self._apps: dict[str, AppMetadata] = {}

    def register(self, app_metadata: AppMetadata) -> None:
        """
        Register an app in the registry.

        Args:
            app_metadata: App metadata to register

        Raises:
            ValueError: If app with same name already registered
        """
        if app_metadata.name in self._apps:
            raise ValueError(f"App '{app_metadata.name}' is already registered")

        self._apps[app_metadata.name] = app_metadata

    def get(self, name: str) -> AppMetadata | None:
        """
        Get app metadata by name.

        Args:
            name: App name

        Returns:
            AppMetadata if found, None otherwise
        """
        return self._apps.get(name)

    def list(self) -> list[AppMetadata]:
        """
        List all registered apps.

        Returns:
            List of AppMetadata objects
        """
        return list(self._apps.values())

    def get_by_type(self, app_type: AppType) -> List[AppMetadata]:
        """
        Get all apps of a specific type.

        Args:
            app_type: AppType to filter by

        Returns:
            List of AppMetadata objects
        """
        return [app for app in self._apps.values() if app.app_type == app_type]

    def __contains__(self, name: str) -> bool:
        """Check if app is registered."""
        return name in self._apps

    def __iter__(self) -> Iterator[AppMetadata]:
        """Iterate over registered apps."""
        return iter(self._apps.values())

    def __len__(self) -> int:
        """Get number of registered apps."""
        return len(self._apps)
