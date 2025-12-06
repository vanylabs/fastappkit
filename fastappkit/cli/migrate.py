"""
CLI commands for migration management.
"""

from __future__ import annotations

import sys
from pathlib import Path

import typer
from sqlalchemy import MetaData

from fastappkit.conf import ensure_settings_loaded
from fastappkit.core.loader import AppLoader
from fastappkit.core.metadata import MetadataCollector
from fastappkit.core.registry import AppMetadata
from fastappkit.core.types import AppType
from fastappkit.migrations.autogen import Autogenerate
from fastappkit.migrations.order import MigrationOrderer
from fastappkit.migrations.preview import MigrationPreview
from fastappkit.migrations.runner import MigrationRunner

app = typer.Typer(name="migrate", help="Migration management commands")


def _get_app_metadata(app_name: str) -> AppMetadata:
    """Get app metadata by name."""
    project_root = Path.cwd()
    loader = AppLoader(project_root)
    registry = loader.load_all()

    app_metadata = registry.get(app_name)
    if not app_metadata:
        raise typer.BadParameter(f"App '{app_name}' not found in registry")

    return app_metadata


@app.command()
def core(
    message: str = typer.Option(..., "-m", "--message", help="Migration message"),
) -> None:
    """Generate core migrations (for core models). Must be run from project root."""
    project_root = Path.cwd()

    # Ensure settings are loaded
    ensure_settings_loaded(project_root)

    # Core migrations are in core/db/migrations/
    core_migration_path = MigrationOrderer.get_core_migration_path(project_root)

    if not core_migration_path.exists():
        typer.echo(f"❌ Core migrations directory not found: {core_migration_path}", err=True)
        raise typer.Exit(1)

    # Create app metadata for core (core uses shared version table like internal)
    core_metadata = AppMetadata(
        name="core",
        app_type=AppType.INTERNAL,  # Core uses shared version table
        import_path="core",
        migrations_path=str(core_migration_path),
        prefix="",
        manifest={},
    )

    autogen = Autogenerate()

    try:
        # Add project root to sys.path so core module can be imported
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))

        # Try to collect metadata from core module for core migrations
        metadata_collector = MetadataCollector()
        # Try to collect from core.models only
        core_metadata_obj = None
        try:
            test_metadata = AppMetadata(
                name="core",
                app_type=core_metadata.app_type,
                import_path="core",
                migrations_path=str(core_migration_path),
                prefix="",
                manifest={"models_module": "core.models"},
            )
            core_metadata_obj = metadata_collector.collect_metadata(test_metadata)
        except Exception:
            pass

        # If no metadata found, use empty MetaData
        if core_metadata_obj is None:
            core_metadata_obj = MetaData()

        migration_path = autogen.generate(
            core_metadata,
            message,
            core_migration_path,
            target_metadata=core_metadata_obj,
        )
        typer.echo(f"✅ Created migration: {migration_path}")
    except Exception as e:
        typer.echo(f"❌ Failed to create migration: {e}", err=True)
        raise typer.Exit(1)


@app.command(name="app")
def app_command(
    app_name: str = typer.Argument(..., help="App name"),
    action: str = typer.Argument(
        ...,
        help="Action: makemigrations (internal only), upgrade, downgrade, preview (external only)",
    ),
    revision: str | None = typer.Option(None, "--revision", "-r", help="Specific revision"),
    message: str | None = typer.Option(None, "-m", "--message", help="Migration message"),
) -> None:
    """Manage app migrations. Must be run from project root."""
    project_root = Path.cwd()

    # Ensure settings are loaded
    ensure_settings_loaded(project_root)

    try:
        app_metadata = _get_app_metadata(app_name)
    except Exception as e:
        typer.echo(f"❌ {e}", err=True)
        raise typer.Exit(1)

    # Internal apps use core's migration directory
    # External apps use their own migrations_path from manifest
    if app_metadata.app_type == AppType.INTERNAL:
        # Use core's migration directory for internal apps
        migration_path = MigrationOrderer.get_core_migration_path(project_root)
        if not migration_path.exists():
            typer.echo(f"❌ Core migrations directory not found: {migration_path}", err=True)
            raise typer.Exit(1)
    else:
        # External apps must have migrations_path configured
        if not app_metadata.migrations_path:
            typer.echo(f"❌ App '{app_name}' has no migrations_path configured", err=True)
            raise typer.Exit(1)
        migration_path = Path(app_metadata.migrations_path)
        if not migration_path.exists():
            typer.echo(f"❌ Migration path does not exist: {migration_path}", err=True)
            raise typer.Exit(1)

    # Internal apps: only makemigrations is supported (preview/upgrade/downgrade use unified commands)
    if app_metadata.app_type == AppType.INTERNAL:
        if action != "makemigrations":
            typer.echo(
                "❌ For internal apps, use unified commands: 'fastappkit migrate preview/upgrade/downgrade'",
                err=True,
            )
            typer.echo(
                "   Internal app migrations are shared with core migrations.",
                err=True,
            )
            raise typer.Exit(1)

    # Only create MigrationRunner and related objects for actions that need database access
    # makemigrations doesn't need them and doesn't need settings initialized
    runner = None
    preview = None
    autogen = Autogenerate()

    if action in ["upgrade", "downgrade", "preview"]:
        # Settings will be auto-loaded from .env when needed (via get_settings())
        runner = MigrationRunner()
        preview = MigrationPreview()

    if action == "makemigrations":
        # External apps cannot have migrations created from core project
        # They are developed independently and migrations are created in their own project
        if app_metadata.app_type == AppType.EXTERNAL:
            typer.echo(
                f"❌ Cannot create migrations for external app '{app_name}' from core project.",
                err=True,
            )
            typer.echo(
                "   External apps are developed independently.",
                err=True,
            )
            typer.echo(
                "   Create migrations in the external app's own project.",
                err=True,
            )
            raise typer.Exit(1)

        if not message:
            message = typer.prompt("Migration message")
        try:
            # Load registry for metadata collection (for internal apps)
            loader = AppLoader(project_root)
            registry = loader.load_all()

            if not message:
                typer.echo("❌ Migration message is required", err=True)
                raise typer.Exit(1)

            # Add project root to sys.path so modules can be imported
            if str(project_root) not in sys.path:
                sys.path.insert(0, str(project_root))

            migration_path_result = autogen.generate(
                app_metadata,
                message,  # Now guaranteed to be str
                migration_path,
                registry=registry,  # Internal apps use registry for full metadata
            )
            typer.echo(f"✅ Created migration: {migration_path_result}")
        except Exception as e:
            typer.echo(f"❌ Failed to create migration: {e}", err=True)
            raise typer.Exit(1)

    elif action == "upgrade":
        # These are guaranteed to be set in the if block above
        assert runner is not None

        target_rev = revision or "head"

        # Check if external app has migrations in its directory
        if app_metadata.app_type == AppType.EXTERNAL:
            versions_dir = migration_path / "versions"
            if versions_dir.exists():
                migration_files = list(versions_dir.glob("*.py"))
                # Filter out __init__.py and __pycache__
                migration_files = [
                    f
                    for f in migration_files
                    if f.name != "__init__.py" and not f.name.startswith("__")
                ]
                if not migration_files:
                    typer.echo(
                        f"❌ External app '{app_name}' has no migration files in {versions_dir}",
                        err=True,
                    )
                    typer.echo(
                        "\nExternal apps must be developed independently with their own migrations.",
                        err=True,
                    )
                    typer.echo(
                        "Navigate to the external app directory and run:",
                        err=True,
                    )
                    typer.echo(f"  cd {app_metadata.filesystem_path}", err=True)
                    typer.echo(
                        '  alembic revision --autogenerate -m "your message"',
                        err=True,
                    )
                    typer.echo(
                        "  alembic upgrade head",
                        err=True,
                    )
                    typer.echo(
                        "\nThen return to the core project to link and use the app.",
                        err=True,
                    )
                    raise typer.Exit(1)

        # Load registry for internal apps (needed for multi-directory support)
        registry = None
        if app_metadata.app_type == AppType.INTERNAL:
            loader = AppLoader(project_root)
            registry = loader.load_all()

        try:
            runner.upgrade(app_metadata, target_rev, migration_path, project_root, registry)
            typer.echo(f"✅ Upgraded {app_name} migrations to {target_rev}")
        except Exception as e:
            typer.echo(f"❌ Failed to upgrade: {e}", err=True)
            # Provide additional context for external apps
            if app_metadata.app_type == AppType.EXTERNAL and "Can't locate revision" in str(e):
                typer.echo(
                    "\n💡 Tip: External apps must have their own migrations created independently.",
                    err=True,
                )
                typer.echo(
                    f"   Navigate to {app_metadata.filesystem_path} and use 'alembic' CLI directly.",
                    err=True,
                )
            raise typer.Exit(1)

    elif action == "downgrade":
        assert runner is not None

        if not revision:
            typer.echo("❌ Downgrade requires --revision", err=True)
            raise typer.Exit(1)

        # Load registry for internal apps (needed for multi-directory support)
        registry = None
        if app_metadata.app_type == AppType.INTERNAL:
            loader = AppLoader(project_root)
            registry = loader.load_all()

        try:
            runner.downgrade(app_metadata, revision, migration_path, project_root, registry)
            typer.echo(f"✅ Downgraded {app_name} migrations to {revision}")
        except Exception as e:
            typer.echo(f"❌ Failed to downgrade: {e}", err=True)
            raise typer.Exit(1)

    elif action == "preview":
        assert preview is not None

        # Load registry for internal apps (needed for multi-directory support)
        registry = None
        if app_metadata.app_type == AppType.INTERNAL:
            loader = AppLoader(project_root)
            registry = loader.load_all()

        target_rev = revision or "head"
        try:
            sql = preview.preview(app_metadata, target_rev, migration_path, project_root, registry)
            typer.echo("SQL to be executed:")
            typer.echo(sql)
        except Exception as e:
            typer.echo(f"❌ Failed to preview: {e}", err=True)
            raise typer.Exit(1)

    else:
        typer.echo(f"❌ Unknown action: {action}", err=True)
        typer.echo("Valid actions: makemigrations, upgrade, downgrade, preview", err=True)
        raise typer.Exit(1)


@app.command()
def preview(
    revision: str | None = typer.Option(
        None, "--revision", "-r", help="Specific revision (default: head)"
    ),
) -> None:
    """Preview SQL for core + internal app migrations. Must be run from project root."""
    project_root = Path.cwd()

    # Ensure settings are loaded
    ensure_settings_loaded(project_root)

    core_migration_path = MigrationOrderer.get_core_migration_path(project_root)
    if not core_migration_path.exists():
        typer.echo(f"❌ Core migrations directory not found: {core_migration_path}", err=True)
        raise typer.Exit(1)

    core_metadata = AppMetadata(
        name="core",
        app_type=AppType.INTERNAL,
        import_path="core",
        migrations_path=str(core_migration_path),
        prefix="",
        manifest={},
    )

    loader = AppLoader(project_root)
    registry = loader.load_all()

    preview = MigrationPreview()
    target_rev = revision or "head"

    try:
        sql = preview.preview(
            core_metadata, target_rev, core_migration_path, project_root, registry
        )
        typer.echo("SQL to be executed:")
        typer.echo(sql)
    except Exception as e:
        typer.echo(f"❌ Failed to preview: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def upgrade(
    revision: str | None = typer.Option(
        None, "--revision", "-r", help="Specific revision (default: head)"
    ),
) -> None:
    """Apply core + internal app migrations. Must be run from project root."""
    project_root = Path.cwd()

    # Ensure settings are loaded
    ensure_settings_loaded(project_root)

    core_migration_path = MigrationOrderer.get_core_migration_path(project_root)
    if not core_migration_path.exists():
        typer.echo(f"❌ Core migrations directory not found: {core_migration_path}", err=True)
        raise typer.Exit(1)

    core_metadata = AppMetadata(
        name="core",
        app_type=AppType.INTERNAL,
        import_path="core",
        migrations_path=str(core_migration_path),
        prefix="",
        manifest={},
    )

    loader = AppLoader(project_root)
    registry = loader.load_all()

    runner = MigrationRunner()
    target_rev = revision or "head"

    try:
        runner.upgrade(core_metadata, target_rev, core_migration_path, project_root, registry)
        typer.echo(f"✅ Upgraded migrations to {target_rev}")
    except Exception as e:
        typer.echo(f"❌ Failed to upgrade: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def downgrade(
    revision: str = typer.Argument(..., help="Revision to downgrade to"),
) -> None:
    """Downgrade core + internal app migrations. Must be run from project root."""
    project_root = Path.cwd()

    # Ensure settings are loaded
    ensure_settings_loaded(project_root)

    core_migration_path = MigrationOrderer.get_core_migration_path(project_root)
    if not core_migration_path.exists():
        typer.echo(f"❌ Core migrations directory not found: {core_migration_path}", err=True)
        raise typer.Exit(1)

    core_metadata = AppMetadata(
        name="core",
        app_type=AppType.INTERNAL,
        import_path="core",
        migrations_path=str(core_migration_path),
        prefix="",
        manifest={},
    )

    loader = AppLoader(project_root)
    registry = loader.load_all()

    runner = MigrationRunner()

    try:
        runner.downgrade(core_metadata, revision, core_migration_path, project_root, registry)
        typer.echo(f"✅ Downgraded migrations to {revision}")
    except Exception as e:
        typer.echo(f"❌ Failed to downgrade: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def all() -> None:
    """Run all migrations in order: core + internal apps → external apps. Must be run from project root."""
    project_root = Path.cwd()

    # Ensure settings are loaded
    ensure_settings_loaded(project_root)

    typer.echo("🔄 Running all migrations...")

    loader = AppLoader(project_root)
    registry = loader.load_all()

    runner = MigrationRunner()
    orderer = MigrationOrderer()

    # Step 1: Core migrations
    typer.echo("\n📦 Core migrations...")
    core_migration_path = orderer.get_core_migration_path(project_root)
    if core_migration_path.exists():
        core_metadata = AppMetadata(
            name="core",
            app_type=AppType.INTERNAL,
            import_path="core",
            migrations_path=str(core_migration_path),
            prefix="",
            manifest={},
        )

        try:
            runner.upgrade(core_metadata, "head", core_migration_path)
            typer.echo("✅ Core migrations upgraded")
        except Exception as e:
            typer.echo(f"❌ Failed to upgrade core: {e}", err=True)
            raise typer.Exit(1)
    else:
        typer.echo("⚠️  Core migrations directory not found, skipping")

    # Step 2: App migrations (internal then external)
    # Note: Internal apps' migrations are already included in core migrations
    # (they share the same migration directory and version table)
    # So we only need to run migrations for external apps
    ordered_apps = orderer.order_apps(registry)

    for app_metadata in ordered_apps:
        # Skip internal apps - their migrations are already handled by core migrations
        if app_metadata.app_type == AppType.INTERNAL:
            typer.echo(f"\n📦 {app_metadata.name} migrations...")
            typer.echo("ℹ️  Internal app migrations are included in core migrations, skipping")
            continue

        # External apps must have migrations_path configured
        typer.echo(f"\n📦 {app_metadata.name} migrations...")

        if not app_metadata.migrations_path:
            typer.echo("⚠️  No migrations_path, skipping")
            continue

        migration_path = Path(app_metadata.migrations_path)
        if not migration_path.exists():
            typer.echo("⚠️  Migration path not found, skipping")
            continue

        try:
            runner.upgrade(app_metadata, "head", migration_path)
            typer.echo(f"✅ {app_metadata.name} migrations upgraded")
        except Exception as e:
            typer.echo(f"❌ Failed to upgrade {app_metadata.name}: {e}", err=True)
            raise typer.Exit(1)

    typer.echo("\n✅ All migrations completed!")
