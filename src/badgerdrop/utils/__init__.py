"""Utilities module for BadgerDrop.

This module provides various utility functions and helpers for AppImage operations.
"""

from .desktop import DesktopIntegration, DesktopIntegrationError
from .desktop_manager import DesktopManager, DesktopManagerError
from .file_copier import FileCopier, FileCopierError
from .icon_installer import IconInstaller, IconInstallerError
from .logging_config import get_logger, setup_logging
from .validators import DirectoryValidationError, validate_directory

__all__ = [
    # Desktop integration
    "DesktopIntegration",
    "DesktopIntegrationError",
    # Desktop manager
    "DesktopManager",
    "DesktopManagerError",
    # File operations
    "FileCopier",
    "FileCopierError",
    # Icon operations
    "IconInstaller",
    "IconInstallerError",
    # Logging
    "get_logger",
    "setup_logging",
    # Validation
    "DirectoryValidationError",
    "validate_directory",
]
