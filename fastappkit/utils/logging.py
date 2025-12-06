"""
Logging configuration for fastappkit.
"""

from __future__ import annotations

import logging
import sys

from fastappkit.cli.output import OutputLevel


def setup_logging(
    level: str = "INFO",
    quiet: bool = False,
    verbose: bool = False,
    debug: bool = False,
) -> None:
    """
    Configure logging for fastappkit.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        quiet: If True, suppress most output
        verbose: If True, show more detailed output
        debug: If True, show debug-level output
    """
    # Determine effective log level
    if quiet:
        log_level = logging.CRITICAL
    elif debug:
        log_level = logging.DEBUG
    elif verbose:
        log_level = logging.INFO
    else:
        # Map string level to logging constant
        log_level = getattr(logging, level.upper(), logging.INFO)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers to avoid duplicates
    root_logger.handlers.clear()

    # Create console handler
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(log_level)

    # Create formatter
    if debug:
        # Detailed format for debug mode
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    else:
        # Simpler format for normal use
        formatter = logging.Formatter("%(levelname)s: %(message)s")

    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

    # Set levels for third-party loggers
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("alembic").setLevel(logging.INFO)


def setup_logging_from_output_level(output_level: OutputLevel) -> None:
    """
    Setup logging based on CLI output level.

    Args:
        output_level: OutputLevel from CLI
    """
    if output_level == OutputLevel.QUIET:
        setup_logging(level="CRITICAL", quiet=True)
    elif output_level == OutputLevel.DEBUG:
        setup_logging(level="DEBUG", debug=True)
    elif output_level == OutputLevel.VERBOSE:
        setup_logging(level="INFO", verbose=True)
    else:
        setup_logging(level="INFO")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)
