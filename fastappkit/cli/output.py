"""
Output and logging utilities for CLI commands.

Provides colored output, progress indicators, and different verbosity levels.
"""

from __future__ import annotations

import sys
from enum import Enum
from typing import Any, ContextManager

try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


class OutputLevel(Enum):
    """Output verbosity levels."""

    QUIET = 0
    NORMAL = 1
    VERBOSE = 2
    DEBUG = 3


class DummyProgress:
    def __init__(self, level: OutputLevel, description: str):
        self.level = level
        self.description = description

    def __enter__(self) -> "DummyProgress":
        if self.level.value >= OutputLevel.NORMAL.value:
            print(f"  {self.description}...", end="", flush=True)
        return self

    def __exit__(self, *args: object) -> None:
        if self.level.value >= OutputLevel.NORMAL.value:
            print(" done")

    def __call__(self, *args: object, **kwargs: object) -> None:
        pass


class Output:
    """Output handler with verbosity control and colored output."""

    def __init__(self, level: OutputLevel = OutputLevel.NORMAL):
        """
        Initialize output handler.

        Args:
            level: Output verbosity level
        """
        self.level = level
        self.console = Console() if RICH_AVAILABLE else None

    def _print(self, message: str, style: str | None = None, err: bool = False) -> None:
        """Internal print method."""
        if self.console:
            if style:
                self.console.print(message, style=style)
            else:
                self.console.print(message)
        else:
            print(message, file=sys.stderr if err else sys.stdout)

    def info(self, message: str) -> None:
        """Print info message."""
        if self.level.value >= OutputLevel.NORMAL.value:
            if self.console:
                self._print(f"[blue]ℹ[/blue]  {message}")
            else:
                self._print(f"ℹ  {message}")

    def success(self, message: str) -> None:
        """Print success message."""
        if self.level.value >= OutputLevel.NORMAL.value:
            if self.console:
                self._print(f"[green]✓[/green]  {message}")
            else:
                self._print(f"✓  {message}")

    def error(self, message: str) -> None:
        """Print error message."""
        if self.console:
            self._print(f"[red]✗[/red]  {message}", err=True)
        else:
            self._print(f"✗  {message}", err=True)

    def warning(self, message: str) -> None:
        """Print warning message."""
        if self.level.value >= OutputLevel.NORMAL.value:
            if self.console:
                self._print(f"[yellow]⚠[/yellow]  {message}")
            else:
                self._print(f"⚠  {message}")

    def debug(self, message: str) -> None:
        """Print debug message."""
        if self.level.value >= OutputLevel.DEBUG.value:
            if self.console:
                self._print(f"[dim]DEBUG:[/dim] {message}")
            else:
                self._print(f"DEBUG: {message}")

    def verbose(self, message: str) -> None:
        """Print verbose message."""
        if self.level.value >= OutputLevel.VERBOSE.value:
            self._print(message)

    def echo(self, message: str) -> None:
        """Echo message (always shown, respects quiet mode only)."""
        if self.level.value >= OutputLevel.NORMAL.value:
            self._print(message)

    def progress(self, description: str) -> ContextManager[Any]:
        """Create a progress context manager."""
        if self.console and self.level.value >= OutputLevel.NORMAL.value:
            return Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console,
            )
        else:
            # Fallback: just print the message
            return DummyProgress(self.level, description)


# Global output instance (will be set by CLI)
_output: Output | None = None


def get_output() -> Output:
    """Get the global output instance."""
    global _output
    if _output is None:
        _output = Output()
    return _output


def set_output(output: Output) -> None:
    """Set the global output instance."""
    global _output
    _output = output


# Convenience functions
def info(message: str) -> None:
    """Print info message."""
    get_output().info(message)


def success(message: str) -> None:
    """Print success message."""
    get_output().success(message)


def error(message: str) -> None:
    """Print error message."""
    get_output().error(message)


def warning(message: str) -> None:
    """Print warning message."""
    get_output().warning(message)


def debug(message: str) -> None:
    """Print debug message."""
    get_output().debug(message)


def verbose(message: str) -> None:
    """Print verbose message."""
    get_output().verbose(message)


def echo(message: str) -> None:
    """Echo message."""
    get_output().echo(message)
