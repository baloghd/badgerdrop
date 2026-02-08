"""Progress dialog for AppImage installation"""

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, GLib
from gettext import gettext as _


class InstallProgressDialog(Gtk.Dialog):
    """Modal dialog showing installation progress"""

    def __init__(self, parent: Gtk.Window, app_name: str, total_bytes: int):
        super().__init__(
            title=_("Installing {app_name}").format(app_name=app_name),
            transient_for=parent,
            modal=True,
            destroy_with_parent=True,
        )

        self.total_bytes = total_bytes
        self.app_name = app_name

        self.set_default_size(400, 150)
        self.set_deletable(False)

        # Build UI
        self._build_ui()

    def _build_ui(self):
        """Build the dialog UI"""
        content = self.get_content_area()
        content.set_margin_top(24)
        content.set_margin_bottom(24)
        content.set_margin_start(24)
        content.set_margin_end(24)
        content.set_spacing(16)

        # Status label
        self.status_label = Gtk.Label()
        self.status_label.set_text(_("Preparing..."))
        self.status_label.set_halign(Gtk.Align.START)
        self.status_label.add_css_class("title-4")
        content.append(self.status_label)

        # Progress bar
        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.set_show_text(True)
        self.progress_bar.set_text("0%")
        content.append(self.progress_bar)

        # File size info
        self.size_label = Gtk.Label()
        self.size_label.set_text(self._format_size(0, self.total_bytes))
        self.size_label.set_halign(Gtk.Align.START)
        self.size_label.add_css_class("dim-label")
        content.append(self.size_label)

    def update_progress(self, phase: str, current: int, total: int):
        """Update the progress display

        Args:
            phase: Current phase (e.g., "copying")
            current: Current bytes processed
            total: Total bytes to process
        """
        # Schedule update on main thread
        GLib.idle_add(self._do_update, phase, current, total)

    def _do_update(self, phase: str, current: int, total: int) -> bool:
        """Actually update the UI (called via GLib.idle_add)"""
        fraction = current / total if total > 0 else 0
        percentage = int(fraction * 100)

        self.progress_bar.set_fraction(fraction)
        self.progress_bar.set_text(f"{percentage}%")

        phase_text = {
            "copying": _("Copying AppImage..."),
        }.get(phase, f"{phase.capitalize()}...")

        self.status_label.set_text(phase_text)
        self.size_label.set_text(self._format_size(current, total))

        return False  # Don't repeat

    def _format_size(self, current: int, total: int) -> str:
        """Format byte sizes for display"""

        def fmt(n: int) -> str:
            for unit in [_("B"), _("KB"), _("MB"), _("GB")]:
                if n < 1024:
                    return f"{n:.1f} {unit}"
                n /= 1024
            return _("{n:.1f} TB").format(n=n)

        return f"{fmt(current)} / {fmt(total)}"

    def complete(self):
        """Mark installation as complete"""
        GLib.idle_add(self._do_complete)

    def _do_complete(self) -> bool:
        """Complete the dialog"""
        self.progress_bar.set_fraction(1.0)
        self.progress_bar.set_text("100%")
        self.status_label.set_text(_("Installation complete!"))
        # Auto-close after a brief moment
        GLib.timeout_add(500, self.destroy)
        return False

    def error(self, message: str):
        """Show error state"""
        GLib.idle_add(self._do_error, message)

    def _do_error(self, message: str) -> bool:
        """Show error"""
        self.status_label.set_text(_("Error: {message}").format(message=message))
        self.status_label.add_css_class("error")
        self.progress_bar.set_fraction(0)
        return False
