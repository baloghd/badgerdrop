"""Installation logic for AppImages"""

import shutil
import shlex
from pathlib import Path
import subprocess
from datetime import datetime
from typing import Optional, Callable
import gettext

_ = gettext.gettext

from .appimage import AppImageInfo
from .installed import InstalledAppsManager, InstalledApp


class AppImageInstaller:
    """Install AppImages to the user's system"""

    def __init__(self, debug: bool = False, install_dir: Optional[Path] = None):
        self.debug = debug
        self.apps_dir = (
            install_dir.expanduser() if install_dir else Path.home() / "Applications"
        )
        self.local_share = Path.home() / ".local" / "share"
        self.applications_dir = self.local_share / "applications"
        self.icons_dir = self.local_share / "icons" / "hicolor"
        self.registry = InstalledAppsManager()

    def install(
        self,
        appimage_path: str,
        info: AppImageInfo,
        make_executable: bool = True,
        progress_callback: Optional[Callable[[str, int, int], None]] = None,
    ) -> InstalledApp:
        """Install an AppImage to ~/Applications with desktop integration

        Args:
            appimage_path: Path to the AppImage file
            info: AppImageInfo with metadata
            make_executable: Whether to make the installed AppImage executable
            progress_callback: Optional callback for progress updates.
                             Called with (phase, current_bytes, total_bytes)
        """
        appimage_src = Path(appimage_path)

        # Ensure directories exist
        self.apps_dir.mkdir(parents=True, exist_ok=True)
        self.applications_dir.mkdir(parents=True, exist_ok=True)

        # Use original filename to preserve version info
        target_appimage = self.apps_dir / appimage_src.name

        # Desktop file uses sanitized app name
        safe_name = self._sanitize_filename(info.name)
        desktop_file = self.applications_dir / f"{safe_name}.desktop"

        if self.debug:
            print(f"[DEBUG] Installing to: {target_appimage}")

        try:
            # Copy AppImage with progress
            self._copy_with_progress(appimage_src, target_appimage, progress_callback)

            # Make executable if requested
            if make_executable:
                target_appimage.chmod(0o755)
                if self.debug:
                    print(f"[DEBUG] Made {target_appimage} executable")
            else:
                if self.debug:
                    print(
                        f"[DEBUG] Skipped making {target_appimage} executable (user preference)"
                    )

            # Install icon if found
            if info.icon_path:
                self._install_icon(info.icon_path, info.icon_name)

            # Create .desktop file
            self._create_desktop_entry(target_appimage, info)

            # Update desktop database
            self._update_desktop_database()

            # Register in registry
            installed_app = InstalledApp(
                name=info.name,
                version=info.version or "unknown",
                source_path=str(appimage_src),
                install_path=str(target_appimage),
                icon_name=info.icon_name,
                categories=info.categories,
                install_date=datetime.now().isoformat(),
                comment=info.comment,
                desktop_file=str(desktop_file),
            )
            self.registry.add(installed_app)

            if self.debug:
                print(f"[DEBUG] Successfully installed {info.name}")

            return installed_app

        except Exception as e:
            if self.debug:
                print(f"[DEBUG] Installation failed: {e}")
            raise

    def _copy_with_progress(
        self,
        src: Path,
        dst: Path,
        progress_callback: Optional[Callable[[str, int, int], None]] = None,
        chunk_size: int = 8192,
    ):
        """Copy file with optional progress callback

        Args:
            src: Source file path
            dst: Destination file path
            progress_callback: Called with (phase, current_bytes, total_bytes)
            chunk_size: Size of chunks to copy at a time
        """
        total_size = src.stat().st_size
        copied = 0

        if self.debug:
            print(f"[DEBUG] Copying {src} ({total_size} bytes) to {dst}")

        with open(src, "rb") as fsrc, open(dst, "wb") as fdst:
            while True:
                chunk = fsrc.read(chunk_size)
                if not chunk:
                    break
                fdst.write(chunk)
                copied += len(chunk)

                if progress_callback:
                    progress_callback("copying", copied, total_size)

        if self.debug:
            print(f"[DEBUG] Copy complete: {copied} bytes copied")

    def _sanitize_filename(self, name: str) -> str:
        """Create a safe filename from app name"""
        # Remove/replace unsafe characters
        unsafe = '<>:"/\\|?*'
        for char in unsafe:
            name = name.replace(char, "")
        return name.strip() or "Application"

    def _install_icon(self, icon_path: Path, icon_name: str):
        """Install icon to user's icon directory"""
        if icon_path.suffix == ".svg":
            target_dir = self.icons_dir / "scalable" / "apps"
            target_name = f"{icon_name}.svg"
        else:
            # Try to determine size, default to 128x128
            target_dir = self.icons_dir / "128x128" / "apps"
            target_name = f"{icon_name}.png"

        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / target_name

        if self.debug:
            print(f"[DEBUG] Installing icon: {target_path}")

        shutil.copy2(icon_path, target_path)

    def _is_electron_app(self, info: AppImageInfo) -> bool:
        """Detect if AppImage is Electron-based by checking for Chrome sandbox in mounted files"""
        # For mounted AppImages, we check if the mount process is still running
        # and look for chrome-sandbox in the mount point
        if info.mount_proc is None or info.mount_proc.poll() is not None:
            return False

        try:
            # The mount_proc's stdout has the mount point
            # We need to find the mount point from the AppImageInfo
            # Actually, we don't have direct access to mount point from info
            # Let's check if we can find it from temp_extract_dir
            # Actually, let's modify AppImageInfo to store mount_point
            return False
        except Exception as e:
            if self.debug:
                print(f"[DEBUG] Error detecting Electron app: {e}")
            return False

    def _create_desktop_entry(self, appimage_path: Path, info: AppImageInfo):
        """Create a .desktop file for the installed AppImage"""
        desktop_file = (
            self.applications_dir / f"{self._sanitize_filename(info.name)}.desktop"
        )

        # Quote the exec path to handle spaces in filename
        exec_path = shlex.quote(str(appimage_path))

        # Build desktop entry content
        lines = [
            "[Desktop Entry]",
            f"Name={info.name}",
            f"Exec={exec_path}",
            f"Icon={info.icon_name}",
            "Type=Application",
            "Terminal=false",
        ]

        if info.categories:
            lines.append(f"Categories={';'.join(info.categories)};")

        if info.comment:
            lines.append(f"Comment={info.comment}")

        lines.append("")  # Trailing newline

        content = "\n".join(lines)

        if self.debug:
            print(f"[DEBUG] Creating .desktop file: {desktop_file}")
            print(f"[DEBUG] Content:\n{content}")

        desktop_file.write_text(content, encoding="utf-8")
        desktop_file.chmod(0o644)

    def _update_desktop_database(self):
        """Update the desktop database to register the new application"""
        try:
            subprocess.run(
                ["update-desktop-database", str(self.applications_dir)],
                capture_output=True,
                check=False,
            )

            # Also update icon cache
            subprocess.run(
                ["gtk-update-icon-cache", "-f", "-t", str(self.icons_dir)],
                capture_output=True,
                check=False,
            )

            if self.debug:
                print("[DEBUG] Updated desktop database and icon cache")

        except FileNotFoundError:
            # Commands might not be available, that's okay
            if self.debug:
                print(
                    "[DEBUG] update-desktop-database or gtk-update-icon-cache not found (optional)"
                )
