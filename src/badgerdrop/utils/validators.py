"""Validation utilities for BadgerDrop.

This module provides validation functions and classes for validating
user input such as directory paths.
"""

import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import gi

    gi.require_version("Gtk", "4.0")

logger = logging.getLogger(__name__)


class DirectoryValidationError(Exception):
    """Exception raised when directory validation fails."""

    pass


def validate_directory(
    path: str | Path,
) -> Path:
    """Validate a directory path for AppImage installation.

    Checks:
    - Path is absolute
    - Path is a directory (or parent exists and is writable)
    - Directory is writable

    Args:
        path: Directory path to validate (can contain ~ for home)

    Returns:
        The validated Path object

    Raises:
        DirectoryValidationError: If validation fails with error message
    """
    path_obj = Path(path).expanduser()

    # Check if path is absolute
    if not path_obj.is_absolute():
        raise DirectoryValidationError("Please select an absolute path")

    # Check if path exists and is a directory
    if path_obj.exists() and not path_obj.is_dir():
        raise DirectoryValidationError("Selected path is not a directory")

    # Check if parent directory is writable (if path doesn't exist)
    if not path_obj.exists():
        parent = path_obj.parent
        if not parent.exists() or not os.access(str(parent), os.W_OK):
            raise DirectoryValidationError("Parent directory is not writable")
    elif not os.access(str(path_obj), os.W_OK):
        raise DirectoryValidationError("Directory is not writable")

    logger.debug("Directory validation passed: %s", path_obj)
    return path_obj
