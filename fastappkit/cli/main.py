"""
Main CLI entry point for fastappkit.
"""

from __future__ import annotations
import typer
from fastappkit import __version__
from fastappkit.cli import core, app as app_commands, migrate
from fastappkit.cli.output import Output, OutputLevel, set_output
from fastappkit.utils.logging import setup_logging_from_output_level

app = typer.Typer(
    name="fastappkit",
    help="FastAppKit - A toolkit for building FastAPI projects with apps",
    invoke_without_command=True,  # allows running CLI with no subcommand
)


def _version_callback(value: bool) -> None:
    if value:
        print(f"fastappkit {__version__}")
        raise typer.Exit()


# ------------------------
# Global options (verbose/debug/quiet)
# ------------------------
@app.callback()
def main_callback(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug output"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress output"),
    version: bool = typer.Option(
        None,
        "--version",
        "-V",
        help="Show fastappkit version",
        # is_eager=True,
        callback=_version_callback,
    ),
) -> None:
    # Set global logging/output level
    if quiet:
        level = OutputLevel.QUIET
    elif debug:
        level = OutputLevel.DEBUG
    elif verbose:
        level = OutputLevel.VERBOSE
    else:
        level = OutputLevel.VERBOSE

    set_output(Output(level=level))
    setup_logging_from_output_level(level)


# ------------------------
# Add subcommands
# ------------------------
app.add_typer(core.app, name="core")
app.add_typer(app_commands.app, name="app")
app.add_typer(migrate.app, name="migrate")


# ------------------------
# Entry point
# ------------------------
def main() -> None:
    app()


if __name__ == "__main__":
    main()
