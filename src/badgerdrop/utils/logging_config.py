"""Logging configuration for BadgerDrop."""

import logging
import sys
from datetime import datetime
from pathlib import Path


def setup_logging(
    debug: bool = False,
    log_file: Path | None = None,
    log_to_stderr: bool = True,
) -> logging.Logger:
    """Setup logging configuration for BadgerDrop.

    Configures the root logger with appropriate handlers and formatters.
    In debug mode, logs to both stderr and a file. In normal mode, logs
    warnings and errors only.

    Args:
        debug: Enable debug level logging
        log_file: Optional custom log file path
        log_to_stderr: Whether to log to stderr

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger("badgerdrop")
    logger.setLevel(logging.DEBUG if debug else logging.WARNING)

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%H:%M:%S",
    )

    # Console handler
    if log_to_stderr:
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(logging.DEBUG if debug else logging.WARNING)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # File handler
    if debug:
        if log_file is None:
            config_dir = Path.home() / ".config" / "badgerdrop"
            config_dir.mkdir(parents=True, exist_ok=True)
            log_file = config_dir / "debug.log"

        # Clear previous log
        try:
            with open(log_file, "w") as f:
                f.write(f"BadgerDrop Debug Log - {datetime.now()}\n")
                f.write("=" * 60 + "\n\n")
        except OSError:
            pass  # Can't write to log file, continue without it

        try:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except (OSError, PermissionError):
            pass  # Can't create log file, continue without it

    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger for a specific module.

    Args:
        name: Module name (typically __name__)

    Returns:
        Logger instance for the module
    """
    return logging.getLogger(f"badgerdrop.{name}")
