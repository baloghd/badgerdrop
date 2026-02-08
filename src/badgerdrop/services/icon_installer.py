"""Icon installation service for AppImages."""

import shutil
from pathlib import Path


class IconInstallerError(Exception):
    """Exception raised for icon installation errors."""

    pass


class IconInstaller:
    """Service for installing application icons to the user's icon directory.

    Handles installation of both SVG and PNG icons to the appropriate
    hicolor icon theme directories.
    """

    def __init__(self, icons_dir: Path, debug: bool = False):
        """Initialize the icon installer.

        Args:
            icons_dir: Base directory for icons (typically ~/.local/share/icons/hicolor)
            debug: Enable debug output
        """
        self.icons_dir = icons_dir
        self.debug = debug

    def install_icon(self, icon_path: Path, icon_name: str) -> Path:
        """Install an icon to the user's icon directory.

        Args:
            icon_path: Path to the icon file (SVG or PNG)
            icon_name: Name for the installed icon (without extension)

        Returns:
            Path to the installed icon

        Raises:
            IconInstallerError: If the icon file doesn't exist or installation fails
        """
        if not icon_path.exists():
            raise IconInstallerError(f"Icon file does not exist: {icon_path}")

        # Determine target directory based on icon format
        if icon_path.suffix == ".svg":
            target_dir = self.icons_dir / "scalable" / "apps"
            target_name = f"{icon_name}.svg"
        else:
            # Default to 128x128 for PNG icons
            target_dir = self.icons_dir / "128x128" / "apps"
            target_name = f"{icon_name}.png"

        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / target_name

        if self.debug:
            print(f"[DEBUG] Installing icon: {target_path}")

        try:
            shutil.copy2(icon_path, target_path)
        except Exception as e:
            raise IconInstallerError(f"Failed to install icon: {e}") from e

        return target_path
