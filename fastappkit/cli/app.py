"""
CLI commands for app management.
"""

from __future__ import annotations

import json
import shutil
import traceback
from pathlib import Path
from typing import Any, List

import typer
from tomlkit import dumps, parse

from fastappkit.cli.output import Output, OutputLevel, get_output, set_output
from fastappkit.cli.templates import get_template_engine
from fastappkit.conf.config import find_config_file, get_apps_list, load_config
from fastappkit.core.loader import AppLoader
from fastappkit.core.manifest import ManifestLoader
from fastappkit.core.resolver import AppResolver
from fastappkit.validation.isolation import IsolationValidator
from fastappkit.validation.manifest import ManifestValidator, ValidationResult
from fastappkit.validation.migrations import MigrationValidator

app = typer.Typer(name="app", help="App management commands")


def _update_fastappkit_toml(project_root: Path, app_entry: str) -> None:
    """
    Add app entry to fastappkit.toml while preserving formatting.

    Uses tomlkit (required dependency) for style-preserving TOML editing.
    """
    config_path = find_config_file(project_root)
    if not config_path:
        raise typer.BadParameter(
            "fastappkit.toml not found. Make sure you're in a fastappkit project."
        )

    # Use tomlkit for style-preserving updates (required dependency)
    # Read file as text to preserve formatting
    content = config_path.read_text(encoding="utf-8")
    toml_data: dict[str, Any] = parse(content)

    # Get or create tool.fastappkit section
    if "tool" not in toml_data:
        toml_data["tool"] = {}

    if "fastappkit" not in toml_data["tool"]:
        toml_data["tool"]["fastappkit"] = {}

    # Get apps list
    fastappkit_section = toml_data["tool"]["fastappkit"]
    if "apps" not in fastappkit_section:
        fastappkit_section["apps"] = []

    apps_list = fastappkit_section["apps"]

    # Check if app already exists
    if app_entry in apps_list:
        return  # Already added

    # Add new entry
    apps_list.append(app_entry)

    # Write back with preserved formatting
    config_path.write_text(dumps(toml_data), encoding="utf-8")


@app.command()
def new(
    name: str = typer.Argument(..., help="App name"),
    as_package: bool = typer.Option(False, "--as-package", help="Create as external package"),
) -> None:
    """Create a new app (internal or external). Must be run from project root."""
    output = get_output()
    project_root = Path.cwd()

    # Validate app name
    if not name.replace("_", "").replace("-", "").isalnum():
        output.error("App name must contain only letters, numbers, hyphens, and underscores")
        raise typer.Exit(1)

    # Determine app location
    if as_package:
        # External app: create in current directory
        app_path = project_root / name
        app_entry = name  # Will be added to fastappkit.toml as package name
        output.info(f"Creating external package: {name}")
    else:
        # Internal app: create in apps/ directory
        apps_dir = project_root / "apps"
        app_path = apps_dir / name
        app_entry = f"apps.{name}"
        output.info(f"Creating internal app: {name}")

    # Check if app already exists
    if app_path.exists():
        output.error(f"App already exists: {app_path}")
        raise typer.Exit(1)

    try:
        # Create directory structure
        app_path.mkdir(parents=True, exist_ok=False)
        output.verbose(f"Created directory: {app_path}")

        # Prepare template context
        context = {
            "app_name": name,
            "project_name": project_root.name,
            "app_description": f"{name} app for fastappkit",
        }

        # Get template engine
        template_engine = get_template_engine()

        # Render templates
        if as_package:
            # External app: Use nested package structure (standard Python package layout)
            # Structure: payments/payments/__init__.py (package in subdirectory)
            package_dir = app_path / name
            package_dir.mkdir(parents=True, exist_ok=True)

            templates = [
                ("app/external/__init__.py.j2", f"{name}/{name}/__init__.py"),
                ("app/external/models.py.j2", f"{name}/{name}/models.py"),
                ("app/external/router.py.j2", f"{name}/{name}/router.py"),
                ("app/external/pyproject.toml.j2", f"{name}/pyproject.toml"),
                ("app/external/README.md.j2", f"{name}/README.md"),
            ]

            # Create fastappkit.toml INSIDE package directory (included in package when published)
            template_engine.render_to_file(
                "app/external/fastappkit.toml.j2",
                package_dir / "fastappkit.toml",
                context,
            )

            # Create migrations directory INSIDE package directory (standard Python package structure)
            # This ensures migrations are included when package is published to PyPI
            migrations_dir = package_dir / "migrations"
            migrations_dir.mkdir(parents=True, exist_ok=True)
            (migrations_dir / "versions").mkdir(parents=True, exist_ok=True)
            (migrations_dir / "versions" / ".gitkeep").touch()

            # Render migrations/env.py
            template_engine.render_to_file(
                "app/external/migrations/env.py.j2",
                migrations_dir / "env.py",
                context,
            )

            # Create script.py.mako template
            template_engine.render_to_file(
                "app/external/migrations/script.py.mako.j2",
                migrations_dir / "script.py.mako",
                context,
            )

            # Create alembic.ini for independent development
            template_engine.render_to_file(
                "app/external/alembic.ini.j2",
                app_path / "alembic.ini",
                context,
            )

            # Create .gitignore for external package
            template_engine.render_to_file(
                "app/external/.gitignore.j2",
                app_path / ".gitignore",
                context,
            )
            output.verbose("Created .gitignore")
        else:
            # Internal app templates
            # Internal apps don't have their own migrations - they use core's migrations
            templates = [
                ("app/internal/__init__.py.j2", f"apps/{name}/__init__.py"),
                ("app/internal/models.py.j2", f"apps/{name}/models.py"),
                ("app/internal/router.py.j2", f"apps/{name}/router.py"),
            ]

        # Render all templates
        for template_path, output_path in templates:
            full_output_path = project_root / output_path
            template_engine.render_to_file(
                template_path,
                full_output_path,
                context,
            )
            output.verbose(f"Created {output_path}")

        # Update fastappkit.toml for internal apps
        if not as_package:
            try:
                _update_fastappkit_toml(project_root, app_entry)
                output.verbose(f"Added '{app_entry}' to fastappkit.toml")
            except Exception as e:
                output.warning(f"Could not update fastappkit.toml: {e}")
                output.info(f"Please manually add '{app_entry}' to fastappkit.toml")

        output.success(f"\n✅ App '{name}' created successfully!")
        if as_package:
            output.info("\nNext steps:")
            output.info(f"  cd {name}")
            output.info("  pip install -e .  # Install the package")
            output.info(f"  # Add '{name}' to fastappkit.toml apps list")
            output.info(f"  fastappkit migrate app {name} makemigrations")
        else:
            output.info("\nNext steps:")
            output.info(f"  # App '{app_entry}' has been added to fastappkit.toml")
            output.info(f"  fastappkit migrate app {name} makemigrations")
            output.info(f"  fastappkit migrate app {name} upgrade")
            output.info("  fastappkit core dev")

    except Exception as e:
        output.error(f"Failed to create app: {e}")
        # Cleanup on error
        if app_path.exists():
            shutil.rmtree(app_path)
        if output.level.value >= 3:  # debug level
            traceback.print_exc()
        raise typer.Exit(1)


@app.command()
def list(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug output"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress output"),
) -> None:
    """List all apps in the project. Must be run from project root."""
    # Override output level if flags are provided at command level
    if quiet or verbose or debug:
        if quiet:
            level = OutputLevel.QUIET
        elif debug:
            level = OutputLevel.DEBUG
        elif verbose:
            level = OutputLevel.VERBOSE
        else:
            level = OutputLevel.VERBOSE  # Default to verbose
        set_output(Output(level=level))

    output = get_output()
    project_root = Path.cwd()

    try:
        output.debug(f"Loading apps from project root: {project_root}")
        loader = AppLoader(project_root)
        registry = loader.load_all()

        if not registry:
            output.info("No apps found in project")
            return

        apps_list = registry.list()
        output.debug(f"Found {len(apps_list)} app(s)")

        output.info("Apps in project:")
        for app_metadata in apps_list:
            app_type = "internal" if app_metadata.app_type.value == "internal" else "external"
            prefix = app_metadata.prefix or "(no prefix)"

            # Normal output: basic info
            output.info(f"  - {app_metadata.name} ({app_type}) - prefix: {prefix}")

            # Verbose output: additional details
            output.verbose(f"    Import path: {app_metadata.import_path}")
            if app_metadata.filesystem_path:
                output.verbose(f"    Filesystem path: {app_metadata.filesystem_path}")
            if app_metadata.migrations_path:
                output.verbose(f"    Migrations path: {app_metadata.migrations_path}")

            # Debug output: full metadata
            output.debug(f"    Full metadata: {app_metadata}")
    except Exception as e:
        output.error(f"Failed to list apps: {e}")
        if output.level.value >= 3:  # debug level
            traceback.print_exc()
        raise typer.Exit(1)


@app.command()
def validate(
    name: str = typer.Argument(..., help="App name to validate"),
    json_output: bool = typer.Option(False, "--json", help="Output results as JSON"),
) -> None:
    """Validate an app. Must be run from project root."""
    output = get_output()
    project_root = Path.cwd()

    try:
        # Read config to find app entry (without loading/importing)
        config_path = find_config_file(project_root)
        if not config_path:
            output.error("fastappkit.toml not found. Make sure you're in a fastappkit project.")
            raise typer.Exit(1)

        config = load_config(config_path)
        apps_list = get_apps_list(config)

        # First, resolve all apps to check for duplicate names
        resolver = AppResolver()
        app_names_map: dict[str, List[str]] = {}  # name -> list of entries
        for entry in apps_list:
            try:
                app_info = resolver.resolve(entry, project_root)
                app_name = app_info.name
                if app_name not in app_names_map:
                    app_names_map[app_name] = []
                app_names_map[app_name].append(entry)
            except Exception:
                # Skip entries that can't be resolved (will be caught later)
                pass

        # Check for duplicate names
        duplicates = {name: entries for name, entries in app_names_map.items() if len(entries) > 1}
        if duplicates:
            output.warning("Duplicate app names detected:")
            for dup_name, entries in duplicates.items():
                output.warning(f"  '{dup_name}' appears in: {', '.join(entries)}")
            output.warning("This may cause conflicts. Consider renaming one of the apps.")

        # Find the app entry that matches the name
        app_entry = None
        matching_entries = []
        for entry in apps_list:
            # Check exact match
            if entry == name:
                matching_entries.append(entry)
                continue
            # Check if entry ends with name (for paths or dotted imports)
            if entry.endswith(f".{name}") or entry.endswith(f"/{name}"):
                matching_entries.append(entry)
                continue
            # Check if it's an internal app pattern (apps.name)
            if entry.startswith("apps."):
                app_name = entry.split(".", 1)[1]
                if app_name == name:
                    matching_entries.append(entry)
                    continue

        if not matching_entries:
            output.error(f"App '{name}' not found in fastappkit.toml")
            output.info(f"Available apps: {', '.join(apps_list) if apps_list else 'none'}")
            raise typer.Exit(1)

        if len(matching_entries) > 1:
            output.error(f"Multiple entries match '{name}': {', '.join(matching_entries)}")
            output.error("Please specify the exact entry (e.g., 'apps.app1' or the full path)")
            raise typer.Exit(1)

        app_entry = matching_entries[0]

        # Resolve app (without importing/executing)
        app_info = resolver.resolve(app_entry, project_root)

        # Load manifest (without executing entrypoint)
        manifest_loader = ManifestLoader()
        manifest = manifest_loader.load_manifest(app_info)

        output.info(f"Validating app: {app_info.name} ({app_info.app_type.value})")

        # Run all validators
        manifest_validator = ManifestValidator()
        isolation_validator = IsolationValidator()
        migration_validator = MigrationValidator()

        # Manifest validation
        manifest_result = manifest_validator.validate(manifest, app_info.name)

        # Isolation validation (for external apps)
        isolation_result: ValidationResult = ValidationResult()
        if app_info.filesystem_path:
            app_path = app_info.filesystem_path
            isolation_result = isolation_validator.validate(
                app_path,
                app_info.app_type,
                None,  # Don't need registry for isolation check
                project_root=project_root,  # Pass project root for detecting project-specific imports
            )

        # Migration validation
        migration_result: ValidationResult = ValidationResult()
        if app_info.filesystem_path:
            app_path = app_info.filesystem_path
            migration_result = migration_validator.validate(app_path, app_info.app_type, manifest)

        # Combine results
        all_errors = manifest_result.errors + isolation_result.errors + migration_result.errors
        all_warnings = (
            manifest_result.warnings + isolation_result.warnings + migration_result.warnings
        )
        is_valid = len(all_errors) == 0

        # Output results
        if json_output:
            result_dict = {
                "app": app_info.name,
                "type": app_info.app_type.value,
                "valid": is_valid,
                "errors": all_errors,
                "warnings": all_warnings,
            }
            output.info(json.dumps(result_dict, indent=2))
        else:
            # Human-readable output
            if is_valid:
                output.success(f"✅ App '{app_info.name}' is valid!")
            else:
                output.error(f"❌ App '{app_info.name}' has validation errors:")

            if all_errors:
                output.info("\nErrors:")
                for error in all_errors:
                    output.error(f"  • {error}")

            if all_warnings:
                output.info("\nWarnings:")
                for warning in all_warnings:
                    output.warning(f"  • {warning}")

            if is_valid and not all_warnings:
                output.info("\nNo issues found.")

        # Exit with appropriate code
        if not is_valid:
            raise typer.Exit(1)

    except Exception as e:
        output.error(f"Failed to validate app: {e}")
        if output.level.value >= 3:  # debug level
            traceback.print_exc()
        raise typer.Exit(1)
