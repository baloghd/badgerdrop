"""Desktop notification management for BadgerDrop"""

import gettext
import logging

import gi

gi.require_version("Gio", "2.0")
from gi.repository import Gio

_ = gettext.gettext("badgerdrop")
logger = logging.getLogger(__name__)


class NotificationManager:
    """Manage desktop notifications"""

    def __init__(self):
        self._app_id = "dev.badgerdrop"
        self._available = self._check_availability()

    def _check_availability(self) -> bool:
        """Check if notifications are available"""
        try:
            Gio.DBusProxy.new_for_bus_sync(
                Gio.BusType.SESSION,
                Gio.DBusProxyFlags.NONE,
                None,
                "org.freedesktop.Notifications",
                "/org/freedesktop/Notifications",
                "org.freedesktop.Notifications",
                None,
            )
            return True
        except Exception:
            return False

    def is_available(self) -> bool:
        """Check if notifications are available"""
        return self._available

    def show_notification(
        self,
        title: str,
        body: str,
        icon_name: str = "application-x-executable",
    ) -> None:
        """Show a desktop notification"""
        if not self._available:
            logger.debug("Notifications not available")
            return

        try:
            proxy = Gio.DBusProxy.new_for_bus_sync(
                Gio.BusType.SESSION,
                Gio.DBusProxyFlags.NONE,
                None,
                "org.freedesktop.Notifications",
                "/org/freedesktop/Notifications",
                "org.freedesktop.Notifications",
                None,
            )

            proxy.Notify(
                "(susssasa{sv}i)",
                self._app_id,
                0,
                icon_name,
                title,
                body,
                [],
                {},
                5000,
            )

            logger.debug("Showed notification: %s", title)

        except Exception as e:
            logger.warning("Failed to show notification: %s", e)

    def show_install_success(self, app_name: str) -> None:
        """Show installation success notification"""
        self.show_notification(
            title=_("Installation Complete"),
            body=_("{app_name} has been installed successfully").format(
                app_name=app_name
            ),
            icon_name="emblem-ok",
        )

    def show_install_error(self, app_name: str, error_message: str) -> None:
        """Show installation error notification"""
        self.show_notification(
            title=_("Installation Failed"),
            body=_("Failed to install {app_name}: {error}").format(
                app_name=app_name, error=error_message
            ),
            icon_name="dialog-error",
        )
