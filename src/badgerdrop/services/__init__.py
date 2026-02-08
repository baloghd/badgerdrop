"""Services module for BadgerDrop.

This module provides various services for AppImage operations.
"""

from .appimage_service import AppImageService, AppImageServiceError
from .desktop_manager import DesktopManager, DesktopManagerError
from .file_copier import FileCopier, FileCopierError
from .icon_installer import IconInstaller, IconInstallerError
from .installation_service import InstallationService, InstallationServiceError

__all__ = [
    "AppImageService",
    "AppImageServiceError",
    "DesktopManager",
    "DesktopManagerError",
    "FileCopier",
    "FileCopierError",
    "IconInstaller",
    "IconInstallerError",
    "InstallationService",
    "InstallationServiceError",
]
