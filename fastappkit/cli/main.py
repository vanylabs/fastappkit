"""
Main CLI entry point for fastappkit.

Uses Typer for command-line interface.
"""

from __future__ import annotations

import typer

from fastappkit import __version__
from fastappkit.cli.output import Output, OutputLevel, set_output
from fastappkit.utils.logging import setup_logging_from_output_level

app = typer.Typer(
    name="fastappkit",
    help="FastAppKit - A toolkit for building FastAPI projects with apps",
    add_completion=False,
    invoke_without_command=False,
)


@app.callback(invoke_without_command=True)
def main_callback(
    ctx: typer.Context,
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug output"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress output"),
    version: bool = typer.Option(
        False, "--version", "-V", help="Show version and exit", is_eager=True
    ),
) -> None:
    """
    FastAppKit - A toolkit for building FastAPI projects with apps.

    Supports both internal apps (project-specific) and external apps (pluggable packages).
    """
    # Handle version flag (must be checked first)
    if version:
        typer.echo(f"fastappkit {__version__}")
        raise typer.Exit(0)

    # If no command was provided, show help
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit(0)

    # Determine output level (default to VERBOSE)
    if quiet:
        level = OutputLevel.QUIET
    elif debug:
        level = OutputLevel.DEBUG
    elif verbose:
        level = OutputLevel.VERBOSE
    else:
        level = OutputLevel.VERBOSE  # Default to verbose instead of normal

    # Set global output level
    set_output(Output(level=level))

    # Setup logging based on output level
    setup_logging_from_output_level(level)


@app.command()
def version() -> None:
    """Show fastappkit version."""
    typer.echo(f"fastappkit {__version__}")


# Import command groups (after app creation to avoid circular imports)
from fastappkit.cli import app as app_commands, core, migrate  # noqa: E402

# Register command groups
app.add_typer(core.app, name="core")
app.add_typer(app_commands.app, name="app")
app.add_typer(migrate.app, name="migrate")


def main() -> None:
    """Main entry point for fastappkit CLI."""
    app()


if __name__ == "__main__":
    main()
