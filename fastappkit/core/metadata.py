"""
Metadata collector - collects SQLAlchemy metadata from apps.
"""

from __future__ import annotations

import importlib

from sqlalchemy import MetaData

from fastappkit.core.registry import AppMetadata, AppRegistry


class MetadataCollector:
    """Collects SQLAlchemy metadata from apps."""

    def collect_metadata(self, app_metadata: AppMetadata) -> MetaData | None:
        """
        Collect SQLAlchemy metadata from an app.

        Args:
            app_metadata: App metadata with manifest

        Returns:
            MetaData object if found, None otherwise

        Raises:
            AppLoadError: If models module cannot be imported
        """
        manifest = app_metadata.manifest
        models_module_path = manifest.get("models_module")

        # If no models_module specified, try common patterns
        if not models_module_path:
            # Try: <import_path>.models
            models_module_path = f"{app_metadata.import_path}.models"

        try:
            models_module = importlib.import_module(models_module_path)
        except ImportError:
            # Models module not found - this is OK, app might not have models
            return None

        # Look for Base or metadata in the module
        metadata = None

        # Try to find Base.declarative_base() metadata
        if hasattr(models_module, "Base"):
            base = getattr(models_module, "Base")
            if hasattr(base, "metadata"):
                metadata = base.metadata

        # Try to find a MetaData instance directly
        if not metadata and hasattr(models_module, "metadata"):
            attr = getattr(models_module, "metadata")
            if isinstance(attr, MetaData):
                metadata = attr

        # Try to find any MetaData instance in module
        if not metadata:
            for attr_name in dir(models_module):
                if attr_name.startswith("_"):
                    continue
                attr = getattr(models_module, attr_name)
                if isinstance(attr, MetaData):
                    metadata = attr
                    break

        return metadata

    def collect_all_metadata(self, registry: AppRegistry) -> dict[str, MetaData]:
        """
        Collect metadata from all apps in registry.

        For internal apps, merges into shared metadata.
        For external apps, keeps isolated.

        Args:
            registry: AppRegistry instance

        Returns:
            Dictionary mapping app names to their MetaData objects
        """
        all_metadata = {}

        for app_metadata in registry.list():
            metadata = self.collect_metadata(app_metadata)
            if metadata:
                all_metadata[app_metadata.name] = metadata

        return all_metadata
