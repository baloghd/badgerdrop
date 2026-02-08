"""Settings dialog for appimg"""

import os
from pathlib import Path

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gio

from badgerdrop.settings import SettingsManager


class SettingsDialog(Gtk.Dialog):
    """Settings dialog for configuring appimg"""

    def __init__(self, parent=None):
        super().__init__(
            title="Settings",
            transient_for=parent,
            modal=True,
            destroy_with_parent=True,
            default_width=400,
            default_height=300,
        )

        self.settings = SettingsManager()

        # Add action buttons
        self.add_button("Close", Gtk.ResponseType.CLOSE)

        # Get content area
        content_area = self.get_content_area()
        content_area.set_margin_start(24)
        content_area.set_margin_end(24)
        content_area.set_margin_top(24)
        content_area.set_margin_bottom(24)
        content_area.set_spacing(16)

        # Create settings box
        settings_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        content_area.append(settings_box)

        # Section: Notifications
        # section_label = Gtk.Label(label="Notifications")
        # section_label.add_css_class("title-2")
        # section_label.set_halign(Gtk.Align.START)
        # settings_box.append(section_label)
        sound_section = Gtk.Label(label="Notifications")
        sound_section.add_css_class("title-2")
        sound_section.set_halign(Gtk.Align.START)
        settings_box.append(sound_section)

        # Play sound toggle
        self._create_switch_row(
            settings_box,
            "Play Sound on Install",
            "Play a sound effect after successful installation",
            self.settings.play_sound,
            self._on_sound_toggled,
        )

        # System notifications toggle
        self._create_switch_row(
            settings_box,
            "System Notifications",
            "Show desktop notifications for install status",
            self.settings.show_notifications,
            self._on_notifications_toggled,
        )

        # Section: Installation
        install_section = Gtk.Label(label="Installation")
        install_section.add_css_class("title-2")
        install_section.set_halign(Gtk.Align.START)
        install_section.set_margin_top(16)
        settings_box.append(install_section)

        # Install directory row
        self._create_directory_row(settings_box)

        # Show current status
        status_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        status_box.set_margin_top(8)
        settings_box.append(status_box)

        status_icon = Gtk.Image.new_from_icon_name("emblem-system-symbolic")
        status_icon.set_pixel_size(16)
        status_box.append(status_icon)

        status_label = Gtk.Label(label="Settings are saved automatically")
        status_label.add_css_class("caption")
        status_box.append(status_label)

        self.connect("response", self._on_response)

    def _create_switch_row(self, parent, title, subtitle, active, callback):
        """Create a row with a switch"""
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        row.set_margin_top(8)
        row.set_margin_bottom(8)

        # Text container
        text_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        text_box.set_hexpand(True)
        row.append(text_box)

        # Title
        title_label = Gtk.Label(label=title)
        title_label.set_halign(Gtk.Align.START)
        title_label.add_css_class("heading")
        text_box.append(title_label)

        # Subtitle
        subtitle_label = Gtk.Label(label=subtitle)
        subtitle_label.set_halign(Gtk.Align.START)
        subtitle_label.add_css_class("caption")
        subtitle_label.add_css_class("dim-label")
        text_box.append(subtitle_label)

        # Switch
        switch = Gtk.Switch()
        switch.set_active(active)
        switch.set_valign(Gtk.Align.CENTER)
        switch.connect("state-set", callback)
        row.append(switch)

        parent.append(row)

    def _on_sound_toggled(self, switch, state):
        """Handle sound toggle"""
        self.settings.play_sound = state
        return False

    def _on_notifications_toggled(self, switch, state):
        """Handle notifications toggle"""
        self.settings.show_notifications = state
        return False

    def _create_directory_row(self, parent):
        """Create a row for selecting install directory"""
        row = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        row.set_margin_top(8)
        row.set_margin_bottom(8)

        # Label and path container
        label_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        label_box.set_halign(Gtk.Align.START)
        row.append(label_box)

        # Title
        title_label = Gtk.Label(label="Install Directory")
        title_label.add_css_class("heading")
        label_box.append(title_label)

        # Path display
        self.path_label = Gtk.Label(label=self.settings.install_directory)
        self.path_label.add_css_class("caption")
        self.path_label.set_max_width_chars(40)
        self.path_label.set_ellipsize(3)  # Pango.EllipsizeMode.END
        label_box.append(self.path_label)

        # Subtitle
        subtitle_label = Gtk.Label(label="Directory where AppImages will be installed")
        subtitle_label.add_css_class("caption")
        subtitle_label.add_css_class("dim-label")
        subtitle_label.set_halign(Gtk.Align.START)
        row.append(subtitle_label)

        # Browse button
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        button_box.set_halign(Gtk.Align.START)
        row.append(button_box)

        browse_button = Gtk.Button(label="Browse...")
        browse_button.connect("clicked", self._on_browse_clicked)
        button_box.append(browse_button)

        parent.append(row)

    def _on_browse_clicked(self, button):
        """Handle browse button click"""
        dialog = Gtk.FileDialog()
        dialog.set_title("Select Install Directory")
        dialog.set_modal(True)

        # Create initial folder from current setting
        current_path = self.settings.get_install_directory_path()
        if current_path.exists():
            dialog.set_initial_folder(Gio.File.new_for_path(str(current_path)))
        else:
            dialog.set_initial_folder(Gio.File.new_for_path(str(Path.home())))

        dialog.select_folder(self, None, self._on_folder_selected, None)

    def _on_folder_selected(self, dialog, result, user_data):
        """Handle folder selection result"""
        try:
            file = dialog.select_folder_finish(result)
            if file:
                path = file.get_path()
                if self._validate_directory(path):
                    self.settings.install_directory = path
                    self.path_label.set_label(path)
        except Exception as e:
            print(f"Error selecting folder: {e}")

    def _validate_directory(self, path: str) -> bool:
        """Validate that the directory path is valid and writable"""
        from pathlib import Path

        path_obj = Path(path).expanduser()

        # Check if path is absolute
        if not path_obj.is_absolute():
            self._show_error("Please select an absolute path")
            return False

        # Check if path exists and is a directory
        if path_obj.exists() and not path_obj.is_dir():
            self._show_error("Selected path is not a directory")
            return False

        # Check if parent directory is writable (if path doesn't exist)
        if not path_obj.exists():
            parent = path_obj.parent
            if not parent.exists() or not os.access(str(parent), os.W_OK):
                self._show_error("Parent directory is not writable")
                return False
        elif not os.access(str(path_obj), os.W_OK):
            self._show_error("Directory is not writable")
            return False

        return True

    def _show_error(self, message: str):
        """Show an error dialog"""
        error_dialog = Gtk.MessageDialog(
            transient_for=self,
            modal=True,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text="Invalid Directory",
        )
        error_dialog.set_secondary_text(message)
        error_dialog.connect("response", lambda d, r: d.destroy())
        error_dialog.show()

    def _on_response(self, dialog, response_id):
        """Handle dialog response"""
        self.destroy()
