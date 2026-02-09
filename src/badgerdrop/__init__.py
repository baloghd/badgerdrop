from badgerdrop.appimage import AppImageInfo, AppImageParser
from badgerdrop.installed import InstalledAppsManager
from badgerdrop.installer import AppImageInstaller
from badgerdrop.main import debug_main, list_main, main, sound_toggle_main
from badgerdrop.notifications import NotificationManager
from badgerdrop.settings import AppSettings, SettingsManager
from badgerdrop.sound import MockSoundManager, SoundManager

__version__ = "0.1.0"
__all__ = [
    "main",
    "debug_main",
    "list_main",
    "sound_toggle_main",
    "AppImageParser",
    "AppImageInfo",
    "AppImageInstaller",
    "InstalledAppsManager",
    "SettingsManager",
    "AppSettings",
    "SoundManager",
    "MockSoundManager",
    "NotificationManager",
]

if __name__ == "__main__":
    main()
