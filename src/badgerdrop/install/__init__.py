"""Installation management for BadgerDrop"""

from badgerdrop.install.installer import AppImageInstaller
from badgerdrop.install.registry import InstalledAppRegistry

__all__ = ["AppImageInstaller", "InstalledAppRegistry"]
