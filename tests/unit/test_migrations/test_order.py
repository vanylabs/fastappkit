"""
Tests for MigrationOrderer.

Tests focus on:
- Ordering apps correctly (core → internal → external)
- Getting core migration path
- Edge cases that would break if implementation changes
"""

from pathlib import Path

from fastappkit.core.registry import AppMetadata, AppRegistry
from fastappkit.core.types import AppType
from fastappkit.migrations.order import MigrationOrderer


class TestMigrationOrderer:
    """Tests for MigrationOrderer class."""

    def test_order_apps_separates_internal_and_external(self) -> None:
        """order_apps() separates internal and external apps."""
        registry = AppRegistry()

        internal1 = AppMetadata(
            name="blog",
            app_type=AppType.INTERNAL,
            import_path="apps.blog",
        )
        internal2 = AppMetadata(
            name="shop",
            app_type=AppType.INTERNAL,
            import_path="apps.shop",
        )
        external1 = AppMetadata(
            name="payments",
            app_type=AppType.EXTERNAL,
            import_path="payments",
        )

        registry.register(internal1)
        registry.register(internal2)
        registry.register(external1)

        ordered = MigrationOrderer.order_apps(registry)

        # Internal apps should come before external apps
        assert len(ordered) == 3
        assert ordered[0].app_type == AppType.INTERNAL
        assert ordered[1].app_type == AppType.INTERNAL
        assert ordered[2].app_type == AppType.EXTERNAL

    def test_order_apps_preserves_config_order(self) -> None:
        """order_apps() preserves order from registry (config order)."""
        registry = AppRegistry()

        # Register in specific order
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
        payments = AppMetadata(
            name="payments",
            app_type=AppType.EXTERNAL,
            import_path="payments",
        )
        auth = AppMetadata(
            name="auth",
            app_type=AppType.EXTERNAL,
            import_path="auth",
        )

        registry.register(blog)
        registry.register(shop)
        registry.register(payments)
        registry.register(auth)

        ordered = MigrationOrderer.order_apps(registry)

        # Internal apps should be in registration order
        internal_apps = [app for app in ordered if app.app_type == AppType.INTERNAL]
        assert internal_apps[0].name == "blog"
        assert internal_apps[1].name == "shop"

        # External apps should be in registration order
        external_apps = [app for app in ordered if app.app_type == AppType.EXTERNAL]
        assert external_apps[0].name == "payments"
        assert external_apps[1].name == "auth"

    def test_order_apps_with_empty_registry(self) -> None:
        """order_apps() handles empty registry."""
        registry = AppRegistry()

        ordered = MigrationOrderer.order_apps(registry)

        assert len(ordered) == 0

    def test_get_core_migration_path(self, temp_project: Path) -> None:
        """get_core_migration_path() returns correct path."""
        path = MigrationOrderer.get_core_migration_path(temp_project)

        assert path == temp_project / "core" / "db" / "migrations"
