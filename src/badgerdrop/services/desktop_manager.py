"""Desktop entry management service for AppImages."""

import shlex
import subprocess
from pathlib import Path

from ..appimage import AppImageInfo


class DesktopManagerError(Exception):
    """Exception raised for desktop entry errors."""

    pass


class DesktopManager:
    """Service for managing .desktop files and desktop integration.

    Handles creation of .desktop files for installed applications and
    updating the desktop database to register new applications.
    """

    def __init__(self, applications_dir: Path, icons_dir: Path, debug: bool = False):
        """Initialize the desktop manager.

        Args:
            applications_dir: Directory for .desktop files
            icons_dir: Directory for icons (needed for cache updates)
            debug: Enable debug output
        """
        self.applications_dir = applications_dir
        self.icons_dir = icons_dir
        self.debug = debug

    def _sanitize_filename(self, name: str) -> str:
        """Create a safe filename from app name.

        Args:
            name: Original app name

        Returns:
            Sanitized name safe for use in filenames
        """
        # Remove/replace unsafe characters
        unsafe = '<>:"/\\|?*'
        for char in unsafe:
            name = name.replace(char, "")
        return name.strip() or "Application"

    def create_desktop_entry(self, appimage_path: Path, info: AppImageInfo) -> Path:
        """Create a .desktop file for the installed AppImage.

        Args:
            appimage_path: Path to the installed AppImage
            info: AppImage metadata

        Returns:
            Path to the created .desktop file

        Raises:
            DesktopManagerError: If desktop file creation fails
        """
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

        try:
            desktop_file.write_text(content, encoding="utf-8")
            desktop_file.chmod(0o644)
        except Exception as e:
            raise DesktopManagerError(f"Failed to create desktop entry: {e}") from e

        return desktop_file

    def update_desktop_database(self) -> None:
        """Update the desktop database to register new applications.

        This updates both the desktop database and the icon cache.
        Errors are silently ignored if the commands are not available.
        """
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
