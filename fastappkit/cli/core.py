"""
CLI commands for project management (core commands).
"""

from __future__ import annotations

import shutil
import sys
import traceback
from pathlib import Path

import typer
import uvicorn

from fastappkit.cli.output import Output, OutputLevel, get_output, set_output
from fastappkit.cli.templates import get_template_engine
from fastappkit.conf import ensure_settings_loaded
from fastappkit.exceptions import ConfigError

app = typer.Typer(name="core", help="Project management commands")


@app.command()
def new(
    name: str = typer.Argument(..., help="Project name"),
    project_root: Path | None = typer.Option(
        None, "--project-root", help="Directory to create project in"
    ),
    description: str | None = typer.Option(None, "--description", help="Project description"),
) -> None:
    """Create a new fastappkit project."""
    output = get_output()
    output.info(f"Creating new project: {name}")

    if project_root is None:
        project_root = Path.cwd()

    project_path = project_root / name

    # Check if directory already exists
    if project_path.exists():
        output.error(f"Directory already exists: {project_path}")
        raise typer.Exit(1)

    try:
        # Create project directory
        project_path.mkdir(parents=True, exist_ok=False)
        output.success(f"Created project directory: {project_path}")

        # Prepare template context
        context = {
            "project_name": name,
            "project_description": description or "A FastAPI project built with fastappkit",
            "use_poetry": True,  # Default to Poetry
        }

        # Get template engine
        template_engine = get_template_engine()

        # Create directory structure
        (project_path / "core" / "db" / "migrations" / "versions").mkdir(
            parents=True, exist_ok=True
        )
        (project_path / "apps").mkdir(parents=True, exist_ok=True)

        # Render templates
        templates = [
            ("project/core/__init__.py.j2", "core/__init__.py"),
            ("project/core/config.py.j2", "core/config.py"),
            ("project/core/app.py.j2", "core/app.py"),
            ("project/core/db/__init__.py.j2", "core/db/__init__.py"),
            ("project/core/db/migrations/env.py.j2", "core/db/migrations/env.py"),
            (
                "project/core/db/migrations/script.py.mako.j2",
                "core/db/migrations/script.py.mako",
            ),
            ("project/fastappkit.toml.j2", "fastappkit.toml"),
            ("project/pyproject.toml.j2", "pyproject.toml"),
            ("project/README.md.j2", "README.md"),
            ("project/main.py.j2", "main.py"),
            ("project/.gitignore.j2", ".gitignore"),
        ]

        for template_path, output_path in templates:
            template_engine.render_to_file(
                template_path,
                project_path / output_path,
                context,
            )
            output.verbose(f"Created {output_path}")

        # Create .env from env.example template
        env_example_content = template_engine.render("project/env.example.j2", context)
        (project_path / ".env").write_text(env_example_content, encoding="utf-8")
        output.verbose("Created .env")

        # Create versions directory placeholder
        (project_path / "core" / "db" / "migrations" / "versions" / ".gitkeep").touch()

        output.success(f"\n✅ Project '{name}' created successfully!")
        output.info("\nNext steps:")
        output.info(f"  cd {name}")
        output.info("  poetry install  # or: pip install -e .")
        output.info("  fastappkit migrate all")
        output.info("  fastappkit core dev")

    except Exception as e:
        output.error(f"Failed to create project: {e}")
        # Cleanup on error
        if project_path.exists():
            shutil.rmtree(project_path)
        raise typer.Exit(1)


@app.command()
def dev(
    host: str = typer.Option("127.0.0.1", "--host", "-h", help="Host to bind to"),
    port: int = typer.Option(8000, "--port", "-p", help="Port to bind to"),
    reload: bool = typer.Option(False, "--reload", help="Enable auto-reload"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug output"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress output"),
) -> None:
    """Run development server. Must be run from project root."""
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
        # Ensure settings are loaded by importing core.app
        # This will execute core.app which initializes FastAppKit with Settings
        ensure_settings_loaded(project_root)

        # Run uvicorn
        output.success(f"Starting development server on http://{host}:{port}")
        if reload:
            output.info("Auto-reload enabled")
            # For reload to work, uvicorn needs an import string, not an app object
            # Ensure project root is on sys.path so Python can import main module
            if str(project_root) not in sys.path:
                sys.path.insert(0, str(project_root))

            # Use import string for reload (main:app imports core.app which sets up app)
            uvicorn.run(
                "main:app",  # Import string: module "main", variable "app"
                host=host,
                port=port,
                reload=reload,
                log_level="info" if output.level.value >= 2 else "warning",
            )
        else:
            # Without reload, import main:app to get the app object
            if str(project_root) not in sys.path:
                sys.path.insert(0, str(project_root))

            from main import app as fastapi_app  # type: ignore[import-not-found]

            uvicorn.run(
                fastapi_app,
                host=host,
                port=port,
                reload=reload,
                log_level="info" if output.level.value >= 2 else "warning",
            )
    except ConfigError as e:
        output.error(f"Configuration error: {e}")
        raise typer.Exit(1)
    except Exception as e:
        output.error(f"Failed to start server: {e}")
        if output.level.value >= 3:  # debug level
            traceback.print_exc()
        raise typer.Exit(1)
