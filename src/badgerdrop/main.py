"""AppImage installer - drag and drop installation for Linux"""

import sys
import os
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw, Gio
from pathlib import Path

# Initialize gettext for i18n
import gettext
_ = gettext.gettext

from .appimage import AppImageParser
from .ui.window import MainWindow


class AppImgApp(Adw.Application):
    def __init__(self):
        super().__init__(
            application_id="dev.badgerdrop.Installer",
            flags=Gio.ApplicationFlags.HANDLES_OPEN,
        )
        self.window = None
        self.connect('activate', self._on_activate)
        self.connect('open', self._on_open)
        
    def _on_activate(self, app):
        if not self.window:
            self.window = MainWindow(application=self)
        self.window.present()
        
    def _on_open(self, app, files, n_files, hint):
        self.activate()
        if self.window and n_files > 0:
            file_path = files[0].get_path()
            if file_path:
                self.window.load_appimage(file_path)


def main():
    app = AppImgApp()
    return app.run(sys.argv)


def debug_main():
    """Debug mode - parse and display AppImage info without GUI"""
    import argparse
    
    parser = argparse.ArgumentParser(description=_("Debug AppImage parsing"))
    parser.add_argument("--appimage", "-a", required=True, help="Path to AppImage file")
    args = parser.parse_args()
    
    
    print("\n=== AppImage Debug Analysis ===\n")
    print(f"File: {args.appimage}\n")
    
    try:
        parser = AppImageParser(args.appimage, debug=True)
        info = parser.parse()
        
        print("\n\nSummary:")
        print(f"  Name: {info.name}")
        print(f"  Icon: {info.icon_name} ({info.icon_path})")
        print(f"  Categories: {', '.join(info.categories) if info.categories else 'None'}")
        print(f"  Comment: {info.comment}")
        
        # Cleanup temp files
        info.cleanup()
        print("\nCleanup complete.\n")
        
    except Exception as e:
        print(f"ERROR: {e}")
        return 1
    
    return 0


def list_main():
    """List all installed AppImages"""
    from .installed import InstalledAppsManager
    
    manager = InstalledAppsManager()
    apps = manager.get_all()
    
    if not apps:
        print("No AppImages installed.")
        print(f"\nInstall location: {Path.home() / 'Applications'}")
        return 0
    
    print(f"\n=== Installed AppImages ({len(apps)}) ===\n")
    
    for app in apps:
        print(f"📦 {app.name}")
        if app.version:
            print(f"   Version: {app.version}")
        print(f"   Source: {app.source_path}")
        print(f"   Installed: {app.install_path}")
        print(f"   Date: {app.install_date}")
        if app.categories:
            print(f"   Categories: {', '.join(app.categories)}")
        print()
    
    print(f"Registry: {manager.registry_file}")
    print(f"Apps folder: {Path.home() / 'Applications'}")
    return 0


def sound_toggle_main():
    """Toggle sound notifications on/off"""
    from .settings import SettingsManager
    
    settings = SettingsManager()
    
    # Toggle current value
    new_value = not settings.play_sound
    settings.play_sound = new_value
    
    status = "ON" if new_value else "OFF"
    print(f"Sound notifications: {status}")
    print(f"Settings saved to: {settings.settings_file}")
    
    return 0
