"""AppImage installer - drag and drop installation for Linux"""

import sys
import gi
import logging

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw, Gio
from pathlib import Path
import gettext

_ = gettext.gettext

from .appimage import AppImageParser
from .ui.window import MainWindow

# Setup logging
logger = logging.getLogger("badgerdrop")


class AppImgApp(Adw.Application):
    def __init__(self):
        super().__init__(
            application_id="dev.badgerdrop.Installer",
            flags=Gio.ApplicationFlags.HANDLES_OPEN,
        )
        self.window = None
        self._activation_count = 0
        self.connect("activate", self._on_activate)
        self.connect("open", self._on_open)
        self.connect("startup", self._on_startup)

    def _on_activate(self, app):
        self._activation_count += 1
        if not self.window:
            self.window = MainWindow(application=self)
        self.window.present()

    def _on_startup(self, app):
        self.hold()
        if self._activation_count == 0:
            self.activate()

    def _on_open(self, app, files, n_files, hint):
        self.activate()
        if self.window and n_files > 0:
            file_path = files[0].get_path()
            if file_path:
                self.window.load_appimage(file_path)


def main():
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    app = AppImgApp()
    return app.run(sys.argv)


def debug_main():
    """Debug mode - parse and display AppImage info without GUI"""
    import argparse

    parser = argparse.ArgumentParser(description=_("Debug AppImage parsing"))
    parser.add_argument("--appimage", "-a", required=True, help="Path to AppImage file")
    args = parser.parse_args()

    logger.info("=== AppImage Debug Analysis ===")
    logger.info("File: %s", args.appimage)

    try:
        parser = AppImageParser(args.appimage)
        info = parser.parse()

        logger.info("Summary:")
        logger.info("  Name: %s", info.name)
        logger.info("  Icon: %s (%s)", info.icon_name, info.icon_path)
        logger.info(
            "  Categories: %s",
            ", ".join(info.categories) if info.categories else "None",
        )
        logger.info("  Comment: %s", info.comment)

        info.cleanup()
        logger.info("Cleanup complete.")

    except Exception as e:
        logger.error("ERROR: %s", e)
        return 1

    return 0


def list_main():
    """List all installed AppImages"""
    from .installed import InstalledAppsManager

    manager = InstalledAppsManager()
    apps = manager.get_all()

    if not apps:
        logger.info("No AppImages installed.")
        logger.info("Install location: %s", Path.home() / "Applications")
        return 0

    logger.info("=== Installed AppImages (%d) ===", len(apps))

    for app in apps:
        logger.info("📦 %s", app.name)
        if app.version:
            logger.info("   Version: %s", app.version)
        logger.info("   Source: %s", app.source_path)
        logger.info("   Installed: %s", app.install_path)
        logger.info("   Date: %s", app.install_date)
        if app.categories:
            logger.info("   Categories: %s", ", ".join(app.categories))
        logger.info("")

    logger.info("Registry: %s", manager.registry_file)
    logger.info("Apps folder: %s", Path.home() / "Applications")
    return 0


def sound_toggle_main():
    """Toggle sound notifications on/off"""
    from .settings import SettingsManager

    settings = SettingsManager()

    new_value = not settings.play_sound
    settings.play_sound = new_value

    status = "ON" if new_value else "OFF"
    logger.info("Sound notifications: %s", status)
    logger.info("Settings saved to: %s", settings.settings_file)

    return 0
