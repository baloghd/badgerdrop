"""Debug logging utilities for BadgerDrop.

Provides comprehensive tracing to both stderr and log file.
"""

import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Any


class DebugLogger:
    """Centralized debug logging to stderr and file."""

    def __init__(self):
        self.enabled = "--debug" in sys.argv or "BADGERDROP_DEBUG" in os.environ
        self.log_file: Path | None = None
        self._initialized = False

    def _init_log_file(self) -> None:
        """Initialize log file path (deferred until first write)."""
        if self._initialized:
            return

        try:
            config_dir = Path.home() / ".config" / "badgerdrop"
            config_dir.mkdir(parents=True, exist_ok=True)
            self.log_file = config_dir / "debug.log"

            # Clear previous log
            with open(self.log_file, "w") as f:
                f.write(f"BadgerDrop Debug Log - {datetime.now()}\n")
                f.write("=" * 60 + "\n\n")
        except Exception as e:
            self._write_stderr(f"[DEBUG] Failed to create log file: {e}")

        self._initialized = True

    def _write_stderr(self, message: str) -> None:
        """Write message to stderr."""
        try:
            sys.stderr.write(message + "\n")
            sys.stderr.flush()
        except Exception:
            pass  # Silent fail for stderr

    def _write_file(self, message: str) -> None:
        """Write message to log file."""
        if self.log_file is None:
            return

        try:
            with open(self.log_file, "a") as f:
                f.write(message + "\n")
        except Exception:
            pass  # Silent fail for file

    def log(self, message: str, *args: Any) -> None:
        """Log a message to both stderr and log file.

        Args:
            message: Message to log (supports % formatting)
            *args: Format arguments
        """
        if not self.enabled:
            return

        self._init_log_file()

        # Format message
        if args:
            try:
                formatted = message % args
            except Exception:
                formatted = f"{message} {' '.join(str(a) for a in args)}"
        else:
            formatted = message

        # Add timestamp and prefix
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        full_message = f"[{timestamp}] {formatted}"

        self._write_stderr(full_message)
        self._write_file(full_message)

    def trace(self, func_or_msg: Any, *args: Any) -> Any:
        """Trace function calls or log messages.

        Usage as decorator:
            @debug_logger.trace
            def my_func():
                ...

        Usage as function:
            debug_logger.trace("message %s", value)
        """
        if callable(func_or_msg):
            # Used as decorator
            func = func_or_msg

            def wrapper(*fargs: Any, **kwargs: Any) -> Any:
                self.log(f"→ ENTER: {func.__qualname__}")
                try:
                    result = func(*fargs, **kwargs)
                    self.log(f"← EXIT: {func.__qualname__}")
                    return result
                except Exception as e:
                    self.log(f"✗ ERROR in {func.__qualname__}: {e}")
                    raise

            return wrapper
        else:
            # Used as regular log function
            self.log(func_or_msg, *args)
            return None


# Global debug logger instance
debug_logger = DebugLogger()


def is_debug_enabled() -> bool:
    """Check if debug mode is enabled."""
    return debug_logger.enabled


def setup_exception_hook() -> None:
    """Setup global exception hook to log all unhandled exceptions."""
    original_hook = sys.excepthook

    def exception_hook(exc_type, exc_value, exc_traceback):
        debug_logger.log("=" * 60)
        debug_logger.log("UNHANDLED EXCEPTION")
        debug_logger.log("Type: %s", exc_type.__name__)
        debug_logger.log("Value: %s", exc_value)

        import traceback

        tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        for line in tb_lines:
            debug_logger.log(line.rstrip())

        debug_logger.log("=" * 60)
        original_hook(exc_type, exc_value, exc_traceback)

    sys.excepthook = exception_hook
