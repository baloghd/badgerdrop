"""Settings management for BadgerDrop"""

import json
from pathlib import Path

from badgerdrop.config.paths import get_config_dir, get_settings_file
from badgerdrop.core.models import AppSettings


class SettingsManager:
    """Manage application settings using Pydantic models"""

    def __init__(self) -> None:
        self.config_dir = get_config_dir()
        self.settings_file = get_settings_file()
        self._settings = self._load()

    def _load(self) -> AppSettings:
        """Load settings from file"""
        if self.settings_file.exists():
            try:
                with open(self.settings_file) as f:
                    data = json.load(f)
                return AppSettings.model_validate(data)
            except (json.JSONDecodeError, TypeError, ValueError):
                pass
        return AppSettings()

    def save(self) -> None:
        """Save settings to file"""
        with open(self.settings_file, "w") as f:
            json.dump(self._settings.model_dump(), f, indent=2)

    @property
    def play_sound(self) -> bool:
        return self._settings.play_sound_on_install

    @play_sound.setter
    def play_sound(self, value: bool) -> None:
        self._settings.play_sound_on_install = value
        self.save()

    @property
    def sound_theme(self) -> str:
        return self._settings.sound_theme

    @sound_theme.setter
    def sound_theme(self, value: str) -> None:
        self._settings.sound_theme = value
        self.save()

    @property
    def auto_make_executable(self) -> bool:
        return self._settings.auto_make_executable

    @auto_make_executable.setter
    def auto_make_executable(self, value: bool) -> None:
        self._settings.auto_make_executable = value
        self.save()

    @property
    def show_notifications(self) -> bool:
        return self._settings.show_notifications

    @show_notifications.setter
    def show_notifications(self, value: bool) -> None:
        self._settings.show_notifications = value
        self.save()

    @property
    def install_directory(self) -> str:
        return self._settings.install_directory

    @install_directory.setter
    def install_directory(self, value: str) -> None:
        self._settings.install_directory = value
        self.save()

    def get_install_directory_path(self) -> Path:
        """Get install directory as expanded Path"""
        return Path(self._settings.install_directory).expanduser()
