"""File copying utilities with progress tracking."""

import logging
import time
from collections.abc import Callable
from pathlib import Path

logger = logging.getLogger(__name__)


class FileCopierError(Exception):
    """Exception raised for file copy errors."""

    pass


class FileCopier:
    """Utility for copying files with optional progress tracking.

    This utility handles file copying operations with support for progress
    callbacks, useful for large files like AppImages.
    """

    # Minimum time between progress updates (seconds)
    _MIN_UPDATE_INTERVAL = 0.05  # 50ms = 20 updates per second max
    # Minimum progress change percentage to trigger update
    _MIN_PROGRESS_DELTA = 0.01  # 1%

    def copy_with_progress(
        self,
        src: Path,
        dst: Path,
        progress_callback: Callable[[str, int, int], None] | None = None,
        chunk_size: int = 8192,
    ) -> None:
        """Copy a file with optional progress callback.

        Args:
            src: Source file path
            dst: Destination file path
            progress_callback: Called with (phase, current_bytes, total_bytes)
            chunk_size: Size of chunks to read/write at a time

        Raises:
            FileCopierError: If the source file doesn't exist or copy fails
        """
        if not src.exists():
            raise FileCopierError(f"Source file does not exist: {src}")

        total_size = src.stat().st_size
        copied = 0
        last_reported_copied = 0
        last_update_time = 0.0

        logger.debug("Copying %s (%d bytes) to %s", src, total_size, dst)

        try:
            with open(src, "rb") as fsrc, open(dst, "wb") as fdst:
                while True:
                    chunk = fsrc.read(chunk_size)
                    if not chunk:
                        break
                    fdst.write(chunk)
                    copied += len(chunk)

                    if progress_callback:
                        current_time = time.monotonic()
                        progress_fraction = (
                            copied / total_size if total_size > 0 else 1.0
                        )
                        last_progress_fraction = (
                            last_reported_copied / total_size if total_size > 0 else 0
                        )

                        # Throttle updates by time or progress
                        time_since_update = current_time - last_update_time
                        progress_delta = progress_fraction - last_progress_fraction

                        if (
                            time_since_update >= self._MIN_UPDATE_INTERVAL
                            or progress_delta >= self._MIN_PROGRESS_DELTA
                            or copied == total_size  # Always report completion
                        ):
                            progress_callback("copying", copied, total_size)
                            last_reported_copied = copied
                            last_update_time = current_time
        except Exception as e:
            raise FileCopierError(f"Failed to copy file: {e}") from e

        logger.debug("Copy complete: %d bytes copied", copied)
