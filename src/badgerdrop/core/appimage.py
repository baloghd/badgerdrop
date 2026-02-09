"""AppImage parsing and metadata extraction"""

import atexit
import logging
import shutil
import subprocess
import tempfile
from configparser import ConfigParser
from pathlib import Path

from badgerdrop.config.constants import PROCESS_TERMINATE_TIMEOUT
from badgerdrop.core.models import AppImageInfo

logger = logging.getLogger(__name__)


class AppImageParser:
    """Parse AppImage files to extract metadata"""

    def __init__(self, appimage_path: str, debug: bool = False) -> None:
        self.appimage_path = Path(appimage_path)
        self.debug = debug
        self._temp_extract_dir: Path | None = None
        self._mount_proc: subprocess.Popen | None = None

    def parse(self) -> AppImageInfo:
        """Parse the AppImage and return extracted info"""
        # Ensure cleanup on exit
        atexit.register(self.cleanup)

        # Mount the AppImage
        mount_point = self._mount_appimage()

        # Find and parse .desktop file
        desktop_file = self._find_desktop_file(mount_point)
        if not desktop_file:
            raise ValueError("No .desktop file found in AppImage")

        info = self._extract_info(desktop_file, mount_point)
        info.temp_extract_dir = self._temp_extract_dir
        info.mount_proc = self._mount_proc

        return info

    def _mount_appimage(self) -> Path:
        """Mount the AppImage and return mount point"""
        logger.debug("Mounting AppImage: %s", self.appimage_path)

        self._temp_extract_dir = Path(tempfile.mkdtemp(prefix="badgerdrop_"))

        try:
            proc = subprocess.Popen(
                [str(self.appimage_path), "--appimage-mount"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            # Read mount point from stdout
            mount_point_line = proc.stdout.readline() if proc.stdout else None
            if not mount_point_line:
                proc.terminate()
                raise RuntimeError("Failed to mount AppImage: no output")

            mount_point = Path(mount_point_line.strip())
            self._mount_proc = proc

            logger.debug("AppImage mounted at: %s", mount_point)
            return mount_point

        except Exception:
            self.cleanup()
            raise

    def _find_desktop_file(self, mount_point: Path) -> Path | None:
        """Find the main .desktop file in the mounted AppImage"""
        for desktop_file in mount_point.rglob("*.desktop"):
            if desktop_file.is_file():
                return desktop_file
        return None

    def _extract_info(self, desktop_file: Path, mount_point: Path) -> AppImageInfo:
        """Extract information from .desktop file"""
        logger.debug("Parsing desktop file: %s", desktop_file)

        config = ConfigParser(interpolation=None)
        config.optionxform = str  # Preserve case

        try:
            config.read(desktop_file)
        except Exception as e:
            logger.warning("Failed to parse desktop file: %s", e)
            config = ConfigParser(interpolation=None)
            config.optionxform = str

        desktop_entry = config["Desktop Entry"] if "Desktop Entry" in config else {}

        name = self._get_desktop_value(desktop_entry, "Name", "Unknown App")
        exec_cmd = self._get_desktop_value(desktop_entry, "Exec", "")
        icon_name = self._get_desktop_value(
            desktop_entry, "Icon", "application-x-executable"
        )
        categories_str = self._get_desktop_value(desktop_entry, "Categories", "")
        comment = self._get_desktop_value(desktop_entry, "Comment", "")

        categories = [c.strip() for c in categories_str.split(";") if c.strip()]

        # Read desktop file content for later use
        desktop_content = desktop_file.read_text()

        # Find icon file if exists
        icon_path = self._find_icon_file(mount_point, icon_name)

        return AppImageInfo(
            name=name,
            exec_cmd=exec_cmd,
            icon_name=icon_name,
            icon_path=icon_path,
            categories=categories,
            comment=comment,
            desktop_file_content=desktop_content,
        )

    def _get_desktop_value(self, section: dict, key: str, default: str = "") -> str:
        """Safely get value from desktop entry section"""
        try:
            return section.get(key, default)
        except (KeyError, AttributeError):
            return default

    def _find_icon_file(self, mount_point: Path, icon_name: str) -> Path | None:
        """Find icon file in the AppImage"""
        if not icon_name:
            return None

        icon_extensions = [".png", ".svg", ".xpm"]

        # Look for icon in common locations
        search_paths = [
            mount_point / "usr" / "share" / "icons" / "hicolor",
            mount_point / "usr" / "share" / "pixmaps",
            mount_point,
        ]

        for search_path in search_paths:
            if not search_path.exists():
                continue

            for ext in icon_extensions:
                for icon_file in search_path.rglob(f"{icon_name}{ext}"):
                    if icon_file.is_file():
                        return icon_file

        return None

    def cleanup(self) -> None:
        """Clean up mounted AppImage and temporary files"""
        if self._mount_proc:
            logger.debug("Unmounting AppImage")
            self._mount_proc.terminate()
            try:
                self._mount_proc.wait(timeout=PROCESS_TERMINATE_TIMEOUT)
            except subprocess.TimeoutExpired:
                self._mount_proc.kill()
            self._mount_proc = None

        if self._temp_extract_dir and self._temp_extract_dir.exists():
            logger.debug("Removing temp directory: %s", self._temp_extract_dir)
            shutil.rmtree(self._temp_extract_dir, ignore_errors=True)
            self._temp_extract_dir = None
