"""Desktop entry management utilities for AppImages."""

import logging
import re
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


class DesktopManagerError(Exception):
    """Exception raised for desktop entry management errors."""

    pass


class DesktopManager:
    """Utility for managing .desktop files and updating desktop databases.

    Handles creation of .desktop files and updating system desktop caches.
    """

    def __init__(self, applications_dir: Path):
        """Initialize the desktop manager.

        Args:
            applications_dir: Directory for .desktop files
        """
        self.applications_dir = applications_dir

    def _sanitize_filename(self, name: str) -> str:
        """Sanitize app name for use as filename.

        Removes unsafe characters that could cause issues with filenames.

        Args:
            name: The application name to sanitize

        Returns:
            A safe filename string
        """
        # Remove characters that are unsafe for filenames
        unsafe_chars = r'[<>:"/\\|?*]'
        safe_name = re.sub(unsafe_chars, "", name)
        # Replace spaces with hyphens
        safe_name = safe_name.replace(" ", "-")
        return safe_name.lower()

    def create_desktop_entry(
        self,
        appimage_path: Path,
        name: str,
        exec_cmd: str,
        icon_name: str,
        categories: list[str],
        comment: str,
    ) -> Path:
        """Create a .desktop file for an AppImage.

        Args:
            appimage_path: Path to the AppImage file
            name: Application name
            exec_cmd: Command to execute
            icon_name: Name of the icon
            categories: List of application categories
            comment: Application description

        Returns:
            Path to the created .desktop file

        Raises:
            DesktopManagerError: If creation fails
        """
        sanitized = self._sanitize_filename(name)
        desktop_file = self.applications_dir / f"{sanitized}.desktop"

        desktop_content = f"""[Desktop Entry]
Name={name}
Exec={appimage_path}
Icon={icon_name}
Type=Application
Terminal=false
Categories={";".join(categories)};
Comment={comment}
"""

        logger.debug("Creating desktop entry: %s", desktop_file)

        try:
            self.applications_dir.mkdir(parents=True, exist_ok=True)
            desktop_file.write_text(desktop_content, encoding="utf-8")
        except Exception as e:
            raise DesktopManagerError(f"Failed to create desktop entry: {e}") from e

        return desktop_file

    def update_desktop_database(self) -> None:
        """Update the desktop database and icon cache.

        Runs update-desktop-database and gtk-update-icon-cache to refresh
        the system caches. Errors are logged but not raised.
        """
        logger.debug("Updating desktop database")

        # Update desktop database
        try:
            subprocess.run(
                ["update-desktop-database", str(self.applications_dir)],
                check=True,
                capture_output=True,
            )
            logger.debug("Desktop database updated")
        except Exception as e:
            logger.warning("Failed to update desktop database: %s", e)

        # Update icon cache
        try:
            icons_dir = self.applications_dir.parent / "icons" / "hicolor"
            if icons_dir.exists():
                subprocess.run(
                    ["gtk-update-icon-cache", "-f", "-t", str(icons_dir)],
                    check=True,
                    capture_output=True,
                )
                logger.debug("Icon cache updated")
        except Exception as e:
            logger.warning("Failed to update icon cache: %s", e)
