"""Main application window with drag and drop installation"""

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

import gettext  # noqa: E402
import logging  # noqa: E402
from pathlib import Path  # noqa: E402

from gi.repository import Adw, Gdk, GdkPixbuf, Gio, GLib, Gtk  # noqa: E402

from badgerdrop.config.settings import SettingsManager  # noqa: E402
from badgerdrop.core.models import AppImageInfo  # noqa: E402
from badgerdrop.services import AppImageService, InstallationService  # noqa: E402
from badgerdrop.system.sound import SoundManager  # noqa: E402
from badgerdrop.ui.drag_content import AppImageDragContent  # noqa: E402
from badgerdrop.ui.helpers import load_css_styles  # noqa: E402
from badgerdrop.ui.progress_dialog import InstallProgressDialog  # noqa: E402
from badgerdrop.ui.settings_dialog import SettingsDialog  # noqa: E402
from badgerdrop.utils import DesktopIntegration  # noqa: E402

_ = gettext.gettext

logger = logging.getLogger(__name__)


# Load CSS from external file
CSS_STYLES = load_css_styles()


class MainWindow(Adw.ApplicationWindow):
    """Main window with drag and drop installation"""

    def __init__(self, **kwargs: object) -> None:
        super().__init__(**kwargs)

        self.set_default_size(800, 500)
        self.set_title("BadgerDrop")
        self.set_icon_name("badgerdrop")

        self.current_appimage: Path | None = None
        self.current_info: AppImageInfo | None = None
        self.installed_app: object | None = (
            None  # Track installed app for reveal button
        )
        self.debug_mode: bool = True  # Always enable debug for now

        # Initialize settings and sound
        self.settings = SettingsManager()
        self.sound = SoundManager()

        self._setup_css()
        self._build_ui()

    def _setup_css(self) -> None:
        """Load custom CSS styles"""
        provider = Gtk.CssProvider()
        css_bytes = CSS_STYLES.encode()
        provider.load_from_data(css_bytes)

        display = Gdk.Display.get_default()
        if display:
            Gtk.StyleContext.add_provider_for_display(
                display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )

    def _build_ui(self) -> None:
        """Build the main UI"""
        # Main container
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_content(box)

        # Header bar
        header = Adw.HeaderBar()
        header.set_title_widget(Gtk.Label(label="BadgerDrop"))

        # Settings button
        settings_button = Gtk.Button.new_from_icon_name("preferences-system-symbolic")
        settings_button.set_tooltip_text(_("Settings"))
        settings_button.connect("clicked", self._on_settings_clicked)
        header.pack_end(settings_button)

        box.append(header)

        # Main content area with toast overlay
        self.toast_overlay = Adw.ToastOverlay()
        box.append(self.toast_overlay)

        content = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=0,
            vexpand=True,
            hexpand=True,
            margin_top=24,
            margin_bottom=24,
            margin_start=24,
            margin_end=24,
        )
        self.toast_overlay.set_child(content)

        # Drop area container
        self.drop_area = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=24,
            vexpand=True,
            hexpand=True,
            halign=Gtk.Align.CENTER,
            valign=Gtk.Align.CENTER,
        )
        self.drop_area.add_css_class("drop-area")
        content.append(self.drop_area)

        # Setup initial drag and drop (for loading AppImages)
        self._setup_file_drop()

        # Build the interface
        self._build_drop_interface()

    def _build_drop_interface(self) -> None:
        """Build the drag interface"""
        # Horizontal layout: App Icon -> Arrow -> Applications Folder
        hbox = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=32,
            halign=Gtk.Align.CENTER,
            valign=Gtk.Align.CENTER,
        )
        self.drop_area.append(hbox)

        # Left side: App Icon placeholder
        self.app_icon_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=12, halign=Gtk.Align.CENTER
        )
        self.app_icon_box.add_css_class("app-icon-container")
        hbox.append(self.app_icon_box)

        # Default icon
        self.app_image = Gtk.Image.new_from_icon_name("application-x-executable")
        self.app_image.set_pixel_size(128)
        self.app_icon_box.append(self.app_image)

        self.app_name_label = Gtk.Label(label=_("Drop AppImage here"))
        self.app_name_label.add_css_class("title-label")
        self.app_icon_box.append(self.app_name_label)

        # Arrow
        arrow = Gtk.Label(label="→")
        arrow.add_css_class("arrow-label")
        hbox.append(arrow)

        # Right side: Applications folder target
        self.target_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=12, halign=Gtk.Align.CENTER
        )
        self.target_box.add_css_class("target-container")
        hbox.append(self.target_box)

        # Folder icon
        folder_icon = Gtk.Image.new_from_icon_name("folder")
        folder_icon.set_pixel_size(96)
        self.target_box.append(folder_icon)

        target_label = Gtk.Label(label=_("Applications"))
        target_label.add_css_class("title-label")
        self.target_box.append(target_label)

        # Instructions
        self.instructions = Gtk.Label(label=_("Drag an AppImage here to load it"))
        self.instructions.add_css_class("subtitle-label")
        self.instructions.set_margin_top(24)
        self.drop_area.append(self.instructions)

        # Debug output area (expandable)
        self.debug_expander = Gtk.Expander(label=_("Debug Output"))
        self.debug_expander.set_margin_top(24)
        self.drop_area.append(self.debug_expander)

        self.debug_text = Gtk.TextView()
        self.debug_text.set_editable(False)
        self.debug_text.set_monospace(True)
        self.debug_text.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)

        debug_scroll = Gtk.ScrolledWindow()
        debug_scroll.set_min_content_height(150)
        debug_scroll.set_child(self.debug_text)
        self.debug_expander.set_child(debug_scroll)

        self.debug_buffer = self.debug_text.get_buffer()

        # Footer with settings
        footer = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=12,
            halign=Gtk.Align.CENTER,
            margin_top=12,
        )
        self.drop_area.append(footer)

        # Make executable toggle
        self.make_exec_switch = Gtk.Switch()
        self.make_exec_switch.set_active(self.settings.auto_make_executable)
        self.make_exec_switch.connect("state-set", self._on_make_exec_toggled)

        make_exec_label = Gtk.Label(label=_("Make executable"))
        make_exec_label.set_margin_end(8)

        footer.append(make_exec_label)
        footer.append(self.make_exec_switch)

    def _on_make_exec_toggled(self, switch: Gtk.Switch, state: bool) -> bool:
        """Handle make executable toggle change"""
        self.settings.auto_make_executable = state
        self._debug_print(f"Make executable: {'ON' if state else 'OFF'}")
        return False

    def _setup_file_drop(self) -> None:
        """Setup drag and drop for loading AppImage files"""
        # Create drop target for files (external drops)
        drop_target = Gtk.DropTarget.new(Gio.File, Gdk.DragAction.COPY)
        drop_target.connect("enter", self._on_file_drag_enter)
        drop_target.connect("leave", self._on_file_drag_leave)
        drop_target.connect("drop", self._on_file_drop)
        self.drop_area.add_controller(drop_target)

    def _setup_internal_drag(self) -> None:
        """Setup drag source on app icon and drop target on Applications folder"""
        if not self.current_appimage:
            return

        # Make app icon a drag source - use text/uri-list format
        drag_source = Gtk.DragSource()
        drag_source.set_actions(Gdk.DragAction.COPY)
        drag_source.connect("prepare", self._on_drag_prepare)
        drag_source.connect("drag-begin", self._on_app_drag_begin)
        drag_source.connect("drag-end", self._on_app_drag_end)
        self.app_icon_box.add_controller(drag_source)

        # Make target a drop target for custom drag content
        drop_target = Gtk.DropTarget()
        drop_target.set_gtypes([AppImageDragContent])
        drop_target.set_actions(Gdk.DragAction.COPY)
        drop_target.connect("enter", self._on_target_drag_enter)
        drop_target.connect("leave", self._on_target_drag_leave)
        drop_target.connect("drop", self._on_target_drop)
        self.target_box.add_controller(drop_target)

        self._debug_print("Drag setup complete - drag app icon to Applications folder")

    def _on_drag_prepare(
        self, source: Gtk.DragSource, x: float, y: float
    ) -> Gdk.ContentProvider | None:
        """Prepare drag content when user starts dragging"""
        if not self.current_appimage:
            return None

        # Create content provider with custom type (prevents desktop auto-launch)
        drag_content = AppImageDragContent(str(self.current_appimage))
        content = Gdk.ContentProvider.new_for_value(drag_content)
        return content

    def _on_file_drag_enter(
        self, target: Gtk.DropTarget, x: float, y: float
    ) -> Gdk.DragAction:
        """Handle drag enter for file drops"""
        self.drop_area.add_css_class("drag-over")
        return Gdk.DragAction.COPY

    def _on_file_drag_leave(self, target: Gtk.DropTarget) -> None:
        """Handle drag leave for file drops"""
        self.drop_area.remove_css_class("drag-over")

    def _on_file_drop(
        self, target: Gtk.DropTarget, file: Gio.File, x: float, y: float
    ) -> bool:
        """Handle file drop (load AppImage)"""
        self.drop_area.remove_css_class("drag-over")

        file_path = file.get_path()
        if file_path:
            self.load_appimage(file_path)

        return True

    def _on_app_drag_begin(self, source: Gtk.DragSource, drag: Gdk.Drag) -> None:
        """Handle start of dragging the app icon"""
        self.app_icon_box.add_css_class("dragging")
        self.target_box.add_css_class("highlight")

        # Set the actual app icon as drag icon (not generic file icon)
        paintable = self.app_image.get_paintable()
        if paintable:
            source.set_icon(paintable, 64, 64)

        self._debug_print("Started dragging app icon")

    def _on_app_drag_end(
        self, source: Gtk.DragSource, drag: Gdk.Drag, delete_data: bool
    ) -> None:
        """Handle end of dragging the app icon"""
        self.app_icon_box.remove_css_class("dragging")
        self.target_box.remove_css_class("highlight")
        self.target_box.remove_css_class("drop-ready")

    def _on_target_drag_enter(
        self, target: Gtk.DropTarget, x: float, y: float
    ) -> Gdk.DragAction:
        """Handle drag enter on target (app being dragged to it)"""
        self.target_box.add_css_class("drop-ready")
        self._debug_print("Dragging over Applications folder...")
        return Gdk.DragAction.COPY

    def _on_target_drag_leave(self, target: Gtk.DropTarget) -> None:
        """Handle drag leave from target"""
        self.target_box.remove_css_class("drop-ready")

    def _on_target_drop(
        self,
        target: Gtk.DropTarget,
        drag_content: AppImageDragContent,
        x: float,
        y: float,
    ) -> bool:
        """Handle drop on target (install!)"""
        self._debug_print("=== DROP START ===")
        self.target_box.remove_css_class("drop-ready")

        # Get file path from custom drag content
        if not drag_content or not hasattr(drag_content, "file_path"):
            self._debug_print("DROP: No drag content or file_path")
            return False

        file_path = drag_content.file_path
        self._debug_print(f"DROP: file_path={file_path}")

        # Verify it's the same AppImage we loaded
        if file_path and Path(file_path) == self.current_appimage:
            self._debug_print("DROP: Match confirmed, starting install...")
            self._install_appimage()
            self._debug_print("DROP: Install completed")
            self._debug_print("=== DROP END ===")
            return True

        self._debug_print("DROP: No match")
        return False

    def load_appimage(self, file_path: str):
        """Load and parse an AppImage file (shows info, doesn't install yet)"""
        self._debug_print(f"Loading: {file_path}")

        path = Path(file_path)
        service = AppImageService(debug=self.debug_mode)
        if not service.validate_appimage(str(path)):
            self._show_error(_("Not an AppImage file"))
            return

        try:
            # Parse the AppImage
            info = service.parse_appimage(file_path)

            self.current_appimage = path
            self.current_info = info

            # Update UI with app info
            self._update_app_display(info)

            # Setup internal drag
            self._setup_internal_drag()

            # Update instructions
            self.instructions.set_text(
                _("Drag the app icon to the Applications folder to install")
            )

        except Exception as e:
            self._show_error(_("Failed to parse AppImage: {}").format(e))
            if self.debug_mode:
                import traceback

                self._debug_print(traceback.format_exc())

    def _update_app_display(self, info: AppImageInfo):
        """Update the UI to show the loaded app"""
        self.app_name_label.set_text(info.name)

        # Try to load the actual icon
        if info.icon_path:
            try:
                if info.icon_path.suffix == ".svg":
                    # Handle SVG - create FileIcon from the file
                    file = Gio.File.new_for_path(str(info.icon_path))
                    icon = Gio.FileIcon.new(file)
                    self.app_image.set_from_gicon(icon)
                else:
                    # Handle PNG
                    pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                        str(info.icon_path), 128, 128, True
                    )
                    self.app_image.set_from_pixbuf(pixbuf)
            except Exception as e:
                self._debug_print(f"Failed to load icon: {e}")

        self._debug_print(f"Loaded: {info.name}")
        self._debug_print("Now drag the app icon to the Applications folder")

    def _install_appimage(self) -> None:
        """Install the current AppImage with progress dialog"""
        if not self.current_appimage or not self.current_info:
            return

        # Get file size for progress tracking
        total_size = self.current_appimage.stat().st_size

        # Show progress dialog
        dialog = InstallProgressDialog(
            parent=self, app_name=self.current_info.name, total_bytes=total_size
        )
        dialog.present()
        self._debug_print(
            f"Installing {self.current_appimage.name} ({total_size / 1024 / 1024:.1f} MB)"
        )

        def progress_callback(description: str, bytes_copied: int, total_bytes: int):
            """Update progress dialog from worker thread"""
            GLib.idle_add(
                dialog.update_progress, description, bytes_copied, total_bytes
            )

        def on_install_complete(installed_app):
            """Called on UI thread when installation succeeds"""
            dialog.close()
            if installed_app:
                self.installed_app = installed_app
                self._show_success(_("Installed {}").format(self.current_info.name))
                self.sound.play_sound("success")
                self._debug_print(f"Successfully installed {self.current_info.name}")
                self._debug_print(f"Source: {self.current_appimage}")
                self._debug_print(f"Installed to: {installed_app.install_path}")
                source_name = self.current_appimage.name
                self.instructions.set_text(
                    f"✓ {self.current_info.name} installed\nFrom: {source_name}"
                )
                self._add_reveal_button()
            return False

        def on_install_error(error):
            """Called on UI thread when installation fails"""
            dialog.close()
            self._show_error(_("Installation failed: {}").format(error))
            if self.debug_mode:
                import traceback

                self._debug_print(traceback.format_exc())
            return False

        def cleanup_callback():
            """Cleanup mount point in any case"""
            self.current_info.cleanup()

        # Start installation using service
        service = InstallationService(debug=self.debug_mode)
        service.install_async(
            appimage_path=self.current_appimage,
            info=self.current_info,
            make_executable=self.settings.auto_make_executable,
            progress_callback=progress_callback,
            success_callback=lambda app: GLib.idle_add(on_install_complete, app),
            error_callback=lambda err: GLib.idle_add(on_install_error, err),
            cleanup_callback=lambda: GLib.idle_add(cleanup_callback),
        )

    def _add_reveal_button(self) -> None:
        """Add a button to reveal the installed app in file manager"""
        # Check if button already exists
        for child in self.drop_area.observe_children():
            if isinstance(child, Gtk.Button) and child.get_label() == _(
                "Show in Folder"
            ):
                return

        reveal_btn = Gtk.Button(label=_("Show in Folder"))
        reveal_btn.add_css_class("suggested-action")
        reveal_btn.add_css_class("pill")
        reveal_btn.set_margin_top(12)
        reveal_btn.connect("clicked", self._on_reveal_clicked)
        self.drop_area.append(reveal_btn)
        reveal_btn.grab_focus()

    def _on_reveal_clicked(self, button: Gtk.Button) -> None:
        """Open file manager to show the installed AppImage"""
        if not self.installed_app:
            return

        install_path = Path(self.installed_app.install_path)
        if install_path.exists():
            try:
                DesktopIntegration.reveal_in_file_manager(install_path)
                logger.debug("Opened folder: %s", install_path.parent)
            except Exception as e:
                logger.error("Failed to open folder: %s", e)

    def _reset_ui(self) -> bool:
        """Reset the UI to initial state"""
        self.current_appimage = None
        self.current_info = None

        self.app_name_label.set_text(_("Drop AppImage here"))
        self.app_image.set_from_icon_name("application-x-executable")

        # Remove drag source from app icon
        for controller in list(self.app_icon_box.observe_controllers()):
            if isinstance(controller, Gtk.DragSource):
                self.app_icon_box.remove_controller(controller)

        # Remove drop target from target
        for controller in list(self.target_box.observe_controllers()):
            if isinstance(controller, Gtk.DropTarget):
                self.target_box.remove_controller(controller)

        self.instructions.set_text("Drag an AppImage here to load it")
        self.debug_buffer.set_text("")

        return False  # Don't repeat

    def _debug_print(self, message: str):
        """Print to debug output"""
        if not self.debug_mode:
            return

        end_iter = self.debug_buffer.get_end_iter()
        self.debug_buffer.insert(end_iter, message + "\n")

        # Auto-scroll
        self.debug_text.scroll_to_iter(self.debug_buffer.get_end_iter(), 0, False, 0, 0)

        # Log at debug level
        logger.debug(message)

    def _show_success(self, message: str):
        """Show a success toast"""
        toast = Adw.Toast(title=message, timeout=3)
        self.toast_overlay.add_toast(toast)

    def _show_error(self, message: str):
        """Show an error toast"""
        toast = Adw.Toast(title=message, timeout=5)
        self.toast_overlay.add_toast(toast)
        self._debug_print(f"ERROR: {message}")

    def _on_settings_clicked(self, button: Gtk.Button) -> None:
        """Open settings dialog"""
        dialog = SettingsDialog(parent=self)
        dialog.present()
