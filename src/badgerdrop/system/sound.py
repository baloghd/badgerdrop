"""Sound management for BadgerDrop"""

import logging
import shutil
import subprocess

import gi

gi.require_version("Gdk", "4.0")
from gi.repository import Gdk

logger = logging.getLogger(__name__)


class SoundManager:
    """Manage application sounds using canberra-gtk-play"""

    def __init__(self):
        self._available = self._check_canberra()

    def _check_canberra(self) -> bool:
        """Check if canberra-gtk-play is available"""
        return shutil.which("canberra-gtk-play") is not None

    def is_available(self) -> bool:
        """Check if sound playback is available"""
        return self._available

    def play_sound(self, sound_name: str = "message") -> None:
        """Play a sound using canberra-gtk-play"""
        if not self._available:
            logger.debug("Sound playback not available")
            return

        try:
            subprocess.run(
                ["canberra-gtk-play", "--id", sound_name],
                check=False,
                capture_output=True,
                timeout=5,
            )
            logger.debug("Played sound: %s", sound_name)
        except Exception as e:
            logger.warning("Failed to play sound: %s", e)


class MockSoundManager:
    """Mock sound manager for when real sound is unavailable"""

    def is_available(self) -> bool:
        return False

    def play_sound(self, sound_name: str = "message") -> None:
        logger.debug("Mock sound manager: would play %s", sound_name)
