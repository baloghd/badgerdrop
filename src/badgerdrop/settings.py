"""Settings management for appimg"""

import json
from dataclasses import dataclass, asdict
from pathlib import Path

from .paths import get_config_dir, get_settings_file
from .constants import (
    DEFAULT_PLAY_SOUND,
    DEFAULT_SOUND_THEME,
    DEFAULT_AUTO_MAKE_EXECUTABLE,
    DEFAULT_SHOW_NOTIFICATIONS,
    DEFAULT_INSTALL_DIR,
)


@dataclass
class AppSettings:
    """Application settings"""

    play_sound_on_install: bool = DEFAULT_PLAY_SOUND
    sound_theme: str = DEFAULT_SOUND_THEME
    auto_make_executable: bool = DEFAULT_AUTO_MAKE_EXECUTABLE
    show_notifications: bool = DEFAULT_SHOW_NOTIFICATIONS
    install_directory: str = DEFAULT_INSTALL_DIR


class SettingsManager:
    """Manage application settings"""

    def __init__(self):
        self.config_dir = get_config_dir()
        self.settings_file = get_settings_file()
        self._settings = self._load()

    def _load(self) -> AppSettings:
        """Load settings from file"""
        if self.settings_file.exists():
            try:
                with open(self.settings_file, "r") as f:
                    data = json.load(f)
                return AppSettings(**data)
            except (json.JSONDecodeError, TypeError):
                pass
        return AppSettings()

    def save(self):
        """Save settings to file"""
        with open(self.settings_file, "w") as f:
            json.dump(asdict(self._settings), f, indent=2)

    @property
    def play_sound(self) -> bool:
        return self._settings.play_sound_on_install

    @play_sound.setter
    def play_sound(self, value: bool):
        self._settings.play_sound_on_install = value
        self.save()

    @property
    def sound_theme(self) -> str:
        return self._settings.sound_theme

    @sound_theme.setter
    def sound_theme(self, value: str):
        self._settings.sound_theme = value
        self.save()

    @property
    def auto_make_executable(self) -> bool:
        return self._settings.auto_make_executable

    @auto_make_executable.setter
    def auto_make_executable(self, value: bool):
        self._settings.auto_make_executable = value
        self.save()

    @property
    def show_notifications(self) -> bool:
        return self._settings.show_notifications

    @show_notifications.setter
    def show_notifications(self, value: bool):
        self._settings.show_notifications = value
        self.save()

    @property
    def install_directory(self) -> str:
        return self._settings.install_directory

    @install_directory.setter
    def install_directory(self, value: str):
        self._settings.install_directory = value
        self.save()

    def get_install_directory_path(self) -> Path:
        """Get install directory as expanded Path"""
        return Path(self._settings.install_directory).expanduser()
