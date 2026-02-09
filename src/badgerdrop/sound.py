"""Sound effects for appimg using libcanberra"""

import gi

gi.require_version("Gtk", "4.0")

import contextlib
import shutil
import subprocess


class SoundManager:
    """Manage sound effects for the application"""

    def __init__(self, settings_manager=None):
        self.settings = settings_manager
        self._canberra_available = self._check_canberra()

    @property
    def enabled(self):
        """Check if sounds are enabled based on settings"""
        if self.settings:
            return self.settings.play_sound
        return True

    def _check_canberra(self) -> bool:
        """Check if canberra-gtk-play is available"""
        return shutil.which("canberra-gtk-play") is not None

    def play_success(self):
        """Play success sound"""
        if not self.enabled or not self._canberra_available:
            return

        with contextlib.suppress(subprocess.TimeoutExpired, Exception):
            subprocess.run(
                ["canberra-gtk-play", "-i", "message"],
                capture_output=True,
                timeout=2,
            )

    def play_error(self):
        """Play error sound"""
        if not self.enabled or not self._canberra_available:
            return

        with contextlib.suppress(subprocess.TimeoutExpired, Exception):
            subprocess.run(
                ["canberra-gtk-play", "-i", "dialog-error"],
                capture_output=True,
                timeout=2,
            )


class MockSoundManager:
    """Mock sound manager when sounds are disabled or unavailable"""

    def __init__(self):
        pass

    def play_success(self):
        pass

    def play_error(self):
        pass
