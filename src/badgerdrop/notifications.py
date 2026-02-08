"""System notifications for appimg"""

import gettext

_ = gettext.gettext

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gio


class NotificationManager:
    """Manage desktop notifications for the application"""

    def __init__(self, app_id="badgerdrop", settings_manager=None):
        self.app_id = app_id
        self.settings = settings_manager
        self._application = None

    def set_application(self, application):
        """Set the Gio.Application for notifications"""
        self._application = application

    @property
    def enabled(self):
        """Check if notifications are enabled"""
        if self.settings:
            return getattr(self.settings, "show_notifications", True)
        return True

    def show_install_success(self, app_name: str, app_path: str):
        """Show notification for successful installation"""
        if not self.enabled:
            return

        notification = Gio.Notification.new(
            _("✓ {app_name} installed").format(app_name=app_name)
        )
        notification.set_body(
            _("Successfully installed to {app_path}").format(app_path=app_path)
        )
        notification.set_icon(Gio.ThemedIcon.new("package-installed-symbolic"))
        notification.add_button("Open Folder", "app.open-folder")
        notification.set_default_action("app.open-folder")

        if self._application:
            self._application.send_notification("install-success", notification)

    def show_install_failure(self, app_name: str, error_message: str):
        """Show notification for failed installation"""
        if not self.enabled:
            return

        notification = Gio.Notification.new(
            _("✗ Failed to install {app_name}").format(app_name=app_name)
        )
        notification.set_body(error_message[:200])  # Truncate long messages
        notification.set_icon(Gio.ThemedIcon.new("dialog-error-symbolic"))
        notification.set_urgent(True)

        if self._application:
            self._application.send_notification("install-failed", notification)

    def show_update_available(
        self, app_name: str, current_version: str, new_version: str
    ):
        """Show notification for available update"""
        if not self.enabled:
            return

        notification = Gio.Notification.new(
            _("Update available for {app_name}").format(app_name=app_name)
        )
        notification.set_body(
            _("Version {new_version} is available (current: {current_version})").format(
                new_version=new_version, current_version=current_version
            )
        )
        notification.set_icon(Gio.ThemedIcon.new("software-update-available-symbolic"))

        if self._application:
            self._application.send_notification("update-available", notification)
