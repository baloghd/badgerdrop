"""File copying service with progress tracking."""

from pathlib import Path
from typing import Optional, Callable


class FileCopierError(Exception):
    """Exception raised for file copy errors."""

    pass


class FileCopier:
    """Service for copying files with optional progress tracking.

    This service handles file copying operations with support for progress
    callbacks, useful for large files like AppImages.
    """

    def __init__(self, debug: bool = False):
        """Initialize the file copier service.

        Args:
            debug: Enable debug output
        """
        self.debug = debug

    def copy_with_progress(
        self,
        src: Path,
        dst: Path,
        progress_callback: Optional[Callable[[str, int, int], None]] = None,
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

        if self.debug:
            print(f"[DEBUG] Copying {src} ({total_size} bytes) to {dst}")

        try:
            with open(src, "rb") as fsrc, open(dst, "wb") as fdst:
                while True:
                    chunk = fsrc.read(chunk_size)
                    if not chunk:
                        break
                    fdst.write(chunk)
                    copied += len(chunk)

                    if progress_callback:
                        progress_callback("copying", copied, total_size)
        except Exception as e:
            raise FileCopierError(f"Failed to copy file: {e}") from e

        if self.debug:
            print(f"[DEBUG] Copy complete: {copied} bytes copied")
