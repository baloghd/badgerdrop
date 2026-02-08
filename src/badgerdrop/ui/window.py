"""Main application window with drag and drop installation"""

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw, Gdk, GdkPixbuf, GLib, Gio, GObject

from .drag_content import AppImageDragContent
from pathlib import Path

from ..appimage import AppImageParser, AppImageInfo
from ..installer import AppImageInstaller
from ..settings import SettingsManager
from ..sound import SoundManager, MockSoundManager
from .settings_dialog import SettingsDialog
from .progress_dialog import InstallProgressDialog
from ..main import _


# CSS for the application appearance
CSS_STYLES = """
.drop-area {
    border-radius: 24px;
    border: 3px dashed alpha(@accent_color, 0.3);
    padding: 48px;
    transition: all 400ms cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.drop-area.drag-over {
    border-color: @accent_color;
    border-style: solid;
    transform: scale(1.02);
}

.app-icon-container {
    background: @card_bg_color;
    border-radius: 20px;
    padding: 24px;
    box-shadow: 0 8px 32px alpha(black, 0.15);
    transition: all 350ms cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.app-icon-container:hover {
    box-shadow: 0 12px 40px alpha(black, 0.2);
    transform: translateY(-2px);
}

.app-icon-container.dragging {
    background: alpha(@accent_bg_color, 0.2);
    box-shadow: 0 16px 56px alpha(black, 0.3);
    transform: scale(1.05) translateY(-4px);
}

.target-container {
    background: @card_bg_color;
    border-radius: 16px;
    padding: 32px;
    border: 2px solid alpha(@borders, 0.5);
    transition: all 400ms cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.target-container:hover {
    box-shadow: 0 4px 20px alpha(black, 0.1);
}

.target-container.highlight {
    background: alpha(@accent_bg_color, 0.15);
    border-color: @accent_color;
    border-style: dashed;
    border-width: 3px;
    box-shadow: 0 8px 32px alpha(@accent_color, 0.2);
}

.target-container.drop-ready {
    background: alpha(@accent_bg_color, 0.3);
    border-color: @accent_color;
    border-style: solid;
    transform: scale(1.08);
    box-shadow: 0 16px 64px alpha(@accent_color, 0.4);
}

.title-label {
    font-size: 24px;
    font-weight: 700;
}

.subtitle-label {
    font-size: 14px;
    opacity: 0.7;
}

.arrow-label {
    font-size: 48px;
    opacity: 0.5;
    font-weight: 200;
    transition: opacity 300ms ease;
}

.arrow-label.active {
    opacity: 0.8;
}

.success-toast {
    background: @accent_bg_color;
    color: @accent_fg_color;
    border-radius: 12px;
    padding: 16px 24px;
    font-weight: 600;
}

.success-toast label {
    font-size: 16px;
}
"""


class MainWindow(Adw.ApplicationWindow):
    """Main window with drag and drop installation"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.set_default_size(800, 500)
        self.set_title("BadgerDrop")
        self.set_icon_name("badgerdrop")

        self.current_appimage: Path = None
        self.current_info: AppImageInfo = None
        self.installed_app = None  # Track installed app for reveal button
        self.debug_mode = True  # Always enable debug for now

        # Initialize settings and sound
        self.settings = SettingsManager()
        self.sound = SoundManager(self.settings)

        self._setup_css()
        self._build_ui()

    def _setup_css(self):
        """Load custom CSS styles"""
        provider = Gtk.CssProvider()
        provider.load_from_data(CSS_STYLES.encode())

        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def _build_ui(self):
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

    def _build_drop_interface(self):
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

    def _on_make_exec_toggled(self, switch, state):
        """Handle make executable toggle change"""
        self.settings.auto_make_executable = state
        self._debug_print(f"Make executable: {'ON' if state else 'OFF'}")
        return False

    def _setup_file_drop(self):
        """Setup drag and drop for loading AppImage files"""
        # Create drop target for files (external drops)
        drop_target = Gtk.DropTarget.new(Gio.File, Gdk.DragAction.COPY)
        drop_target.connect("enter", self._on_file_drag_enter)
        drop_target.connect("leave", self._on_file_drag_leave)
        drop_target.connect("drop", self._on_file_drop)
        self.drop_area.add_controller(drop_target)

    def _setup_internal_drag(self):
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

    def _on_drag_prepare(self, source, x, y):
        """Prepare drag content when user starts dragging"""
        if not self.current_appimage:
            return None

        # Create content provider with custom type (prevents desktop auto-launch)
        drag_content = AppImageDragContent(str(self.current_appimage))
        content = Gdk.ContentProvider.new_for_value(drag_content)
        return content

    def _on_file_drag_enter(self, target, x, y):
        """Handle drag enter for file drops"""
        self.drop_area.add_css_class("drag-over")
        return Gdk.DragAction.COPY

    def _on_file_drag_leave(self, target):
        """Handle drag leave for file drops"""
        self.drop_area.remove_css_class("drag-over")

    def _on_file_drop(self, target, file, x, y):
        """Handle file drop (load AppImage)"""
        self.drop_area.remove_css_class("drag-over")

        file_path = file.get_path()
        if file_path:
            self.load_appimage(file_path)

        return True

    def _on_app_drag_begin(self, source, drag):
        """Handle start of dragging the app icon"""
        self.app_icon_box.add_css_class("dragging")
        self.target_box.add_css_class("highlight")

        # Set the actual app icon as drag icon (not generic file icon)
        paintable = self.app_image.get_paintable()
        if paintable:
            source.set_icon(paintable, 64, 64)

        self._debug_print("Started dragging app icon")

    def _on_app_drag_end(self, source, drag, delete_data):
        """Handle end of dragging the app icon"""
        self.app_icon_box.remove_css_class("dragging")
        self.target_box.remove_css_class("highlight")
        self.target_box.remove_css_class("drop-ready")

    def _on_target_drag_enter(self, target, x, y):
        """Handle drag enter on target (app being dragged to it)"""
        self.target_box.add_css_class("drop-ready")
        self._debug_print("Dragging over Applications folder...")
        return Gdk.DragAction.COPY

    def _on_target_drag_leave(self, target):
        """Handle drag leave from target"""
        self.target_box.remove_css_class("drop-ready")

    def _on_target_drop(self, target, drag_content, x, y):
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
        if not path.suffix.lower() == ".appimage" and not path.name.endswith(
            ".AppImage"
        ):
            self._show_error(_("Not an AppImage file"))
            return

        try:
            # Parse the AppImage
            parser = AppImageParser(file_path, debug=self.debug_mode)
            info = parser.parse()

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

    def _install_appimage(self):
        """Install the current AppImage with progress dialog"""
        if not self.current_appimage or not self.current_info:
            return

        # Get file size for progress tracking
        total_size = self.current_appimage.stat().st_size

        # Show progress dialog
        dialog = InstallProgressDialog(
            parent=self,
            app_name=self.current_info.name,
            total_bytes=total_size
        )
        dialog.present()
        self._debug_print(f"Installing {self.current_appimage.name} ({total_size / 1024 / 1024:.1f} MB)")

        # Track installation result
        install_result = {"success": False, "error": None, "installed_app": None}

        def progress_callback(description: str, bytes_copied: int, total_bytes: int):
            """Update progress dialog from worker thread"""
            GLib.idle_add(dialog.update_progress, description, bytes_copied, total_bytes)

        def install_worker():
            """Run installation in background thread"""
            try:
                installer = AppImageInstaller(debug=self.debug_mode)
                installed_app = installer.install(
                    str(self.current_appimage),
                    self.current_info,
                    make_executable=self.settings.auto_make_executable,
                    progress_callback=progress_callback,
                )
                install_result["installed_app"] = installed_app
                install_result["success"] = True
                GLib.idle_add(on_install_complete, installed_app)
            except Exception as e:
                install_result["error"] = str(e)
                GLib.idle_add(on_install_error, e)
            finally:
                # Cleanup mount point in any case
                GLib.idle_add(self.current_info.cleanup)

        def on_install_complete(installed_app):
            """Called on UI thread when installation succeeds"""
            dialog.close()
            if installed_app:
                self.installed_app = installed_app
                self._show_success(_("Installed {}").format(self.current_info.name))
                self.sound.play_success()
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

        # Start installation in background thread
        import threading
        thread = threading.Thread(target=install_worker, daemon=True)
        thread.start()

    def _add_reveal_button(self):
        """Add a button to reveal the installed app in file manager"""
        # Check if button already exists
        for child in self.drop_area.observe_children():
            if isinstance(child, Gtk.Button) and child.get_label() == _("Show in Folder"):
                return

        reveal_btn = Gtk.Button(label=_("Show in Folder"))
        reveal_btn.add_css_class("suggested-action")
        reveal_btn.add_css_class("pill")
        reveal_btn.set_margin_top(12)
        reveal_btn.connect("clicked", self._on_reveal_clicked)
        self.drop_area.append(reveal_btn)
        reveal_btn.grab_focus()

    def _on_reveal_clicked(self, button):
        """Open file manager to show the installed AppImage"""
        if not self.installed_app:
            return

        install_path = Path(self.installed_app.install_path)
        if install_path.exists():
            # Use xdg-open to reveal the file
            import subprocess

            subprocess.run(["xdg-open", str(install_path.parent)])
            self._debug_print(f"Opened folder: {install_path.parent}")

    def _reset_ui(self):
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

        # Also print to console
        print(message)

    def _show_success(self, message: str):
        """Show a success toast"""
        toast = Adw.Toast(title=message, timeout=3)
        self.toast_overlay.add_toast(toast)

    def _show_error(self, message: str):
        """Show an error toast"""
        toast = Adw.Toast(title=message, timeout=5)
        self.toast_overlay.add_toast(toast)
        self._debug_print(f"ERROR: {message}")

    def _on_settings_clicked(self, button):
        """Open settings dialog"""
        dialog = SettingsDialog(parent=self)
        dialog.present()
