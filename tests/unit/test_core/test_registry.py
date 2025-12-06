"""
Tests for AppRegistry and AppMetadata.

Tests focus on:
- Registering apps (success and duplicate detection)
- Retrieving apps by name and type
- Iteration and containment checks
- Edge cases that would break if implementation changes
"""

import pytest

from fastapi import APIRouter
from fastappkit.core.registry import AppMetadata, AppRegistry
from fastappkit.core.types import AppType


class TestAppMetadata:
    """Tests for AppMetadata dataclass."""

    def test_metadata_creation_with_minimal_fields(self) -> None:
        """AppMetadata can be created with only required fields."""
        metadata = AppMetadata(
            name="test_app",
            app_type=AppType.INTERNAL,
            import_path="apps.test_app",
        )

        assert metadata.name == "test_app"
        assert metadata.app_type == AppType.INTERNAL
        assert metadata.import_path == "apps.test_app"
        assert metadata.filesystem_path is None
        assert metadata.router is None
        assert metadata.migrations_path is None
        assert metadata.prefix == ""

    def test_metadata_creation_with_all_fields(self) -> None:
        """AppMetadata can be created with all optional fields."""
        router = APIRouter()
        metadata = AppMetadata(
            name="test_app",
            app_type=AppType.EXTERNAL,
            import_path="external_app",
            filesystem_path="/path/to/app",
            router=router,
            migrations_path="/path/to/migrations",
            prefix="/api/v1",
            manifest={"version": "1.0.0"},
        )

        assert metadata.name == "test_app"
        assert metadata.app_type == AppType.EXTERNAL
        assert metadata.router is router
        assert metadata.prefix == "/api/v1"
        assert metadata.manifest["version"] == "1.0.0"


class TestAppRegistry:
    """Tests for AppRegistry."""

    def test_empty_registry(self) -> None:
        """Empty registry has no apps."""
        registry = AppRegistry()

        assert len(registry) == 0
        assert list(registry.list()) == []
        assert "test_app" not in registry

    def test_register_single_app(self) -> None:
        """Can register a single app."""
        registry = AppRegistry()
        metadata = AppMetadata(
            name="blog",
            app_type=AppType.INTERNAL,
            import_path="apps.blog",
        )

        registry.register(metadata)

        assert len(registry) == 1
        assert "blog" in registry
        assert registry.get("blog") == metadata

    def test_register_multiple_apps(self) -> None:
        """Can register multiple different apps."""
        registry = AppRegistry()

        blog = AppMetadata(
            name="blog",
            app_type=AppType.INTERNAL,
            import_path="apps.blog",
        )
        shop = AppMetadata(
            name="shop",
            app_type=AppType.INTERNAL,
            import_path="apps.shop",
        )

        registry.register(blog)
        registry.register(shop)

        assert len(registry) == 2
        assert registry.get("blog") == blog
        assert registry.get("shop") == shop

    def test_register_duplicate_app_raises_error(self) -> None:
        """Registering duplicate app name raises ValueError."""
        registry = AppRegistry()
        app1 = AppMetadata(
            name="blog",
            app_type=AppType.INTERNAL,
            import_path="apps.blog",
        )
        app2 = AppMetadata(
            name="blog",  # Same name
            app_type=AppType.EXTERNAL,
            import_path="external_blog",
        )

        registry.register(app1)

        with pytest.raises(ValueError, match="already registered"):
            registry.register(app2)

    def test_get_nonexistent_app_returns_none(self) -> None:
        """Getting non-existent app returns None."""
        registry = AppRegistry()

        assert registry.get("nonexistent") is None

    def test_get_by_type_filters_correctly(self) -> None:
        """get_by_type() returns only apps of specified type."""
        registry = AppRegistry()

        internal1 = AppMetadata(
            name="internal1",
            app_type=AppType.INTERNAL,
            import_path="apps.internal1",
        )
        internal2 = AppMetadata(
            name="internal2",
            app_type=AppType.INTERNAL,
            import_path="apps.internal2",
        )
        external1 = AppMetadata(
            name="external1",
            app_type=AppType.EXTERNAL,
            import_path="external1",
        )

        registry.register(internal1)
        registry.register(internal2)
        registry.register(external1)

        internal_apps = registry.get_by_type(AppType.INTERNAL)
        assert len(internal_apps) == 2
        assert set(app.name for app in internal_apps) == {"internal1", "internal2"}

        external_apps = registry.get_by_type(AppType.EXTERNAL)
        assert len(external_apps) == 1
        assert external_apps[0].name == "external1"

    def test_registry_contains_check(self) -> None:
        """Can check if app is in registry using 'in' operator."""
        registry = AppRegistry()
        app = AppMetadata(
            name="test",
            app_type=AppType.INTERNAL,
            import_path="apps.test",
        )

        assert "test" not in registry

        registry.register(app)

        assert "test" in registry
        assert "other" not in registry
