from badgerdrop.config.settings import SettingsManager
from badgerdrop.core.appimage import AppImageParser
from badgerdrop.core.models import AppImageInfo, AppSettings, InstalledApp
from badgerdrop.install.installer import AppImageInstaller
from badgerdrop.install.registry import InstalledAppRegistry
from badgerdrop.main import debug_main, list_main, main, sound_toggle_main
from badgerdrop.system.notifications import NotificationManager
from badgerdrop.system.sound import MockSoundManager, SoundManager

__version__ = "0.1.0"
__all__ = [
    "main",
    "debug_main",
    "list_main",
    "sound_toggle_main",
    "AppImageParser",
    "AppImageInfo",
    "InstalledApp",
    "AppImageInstaller",
    "InstalledAppRegistry",
    "SettingsManager",
    "AppSettings",
    "SoundManager",
    "MockSoundManager",
    "NotificationManager",
]

if __name__ == "__main__":
    main()
