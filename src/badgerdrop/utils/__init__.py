"""Utilities module for BadgerDrop.

This module provides various utility functions and helpers for AppImage operations.
"""

from badgerdrop.utils.desktop import DesktopIntegration, DesktopIntegrationError
from badgerdrop.utils.desktop_manager import DesktopManager, DesktopManagerError
from badgerdrop.utils.file_copier import FileCopier, FileCopierError
from badgerdrop.utils.icon_installer import IconInstaller, IconInstallerError
from badgerdrop.utils.logging_config import get_logger, setup_logging
from badgerdrop.utils.validators import DirectoryValidationError, validate_directory

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
