"""Core domain models and AppImage parsing"""

from badgerdrop.core.appimage import AppImageParser
from badgerdrop.core.models import AppImageInfo, AppSettings, InstalledApp

__all__ = ["AppImageParser", "AppImageInfo", "AppSettings", "InstalledApp"]
