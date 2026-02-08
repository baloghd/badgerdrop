"""AppImage parsing and metadata extraction"""

import subprocess
import tempfile
import shutil
import os
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
import configparser
import gettext

_ = gettext.gettext


@dataclass
class AppImageInfo:
    """Extracted information from an AppImage"""

    name: str
    exec_cmd: str
    icon_name: str
    icon_path: Optional[Path]
    categories: list[str]
    comment: str
    desktop_file_content: str
    temp_extract_dir: Optional[Path]
    mount_proc: Optional[subprocess.Popen] = None
    version: Optional[str] = None

    def cleanup(self):
        """Remove temporary extraction directory and unmount"""
        # Unmount if we have a running mount process
        if self.mount_proc and self.mount_proc.poll() is None:
            try:
                self.mount_proc.terminate()
                self.mount_proc.wait(timeout=5)
            except Exception:
                try:
                    self.mount_proc.kill()
                except Exception:
                    pass

        if self.temp_extract_dir and self.temp_extract_dir.exists():
            shutil.rmtree(self.temp_extract_dir, ignore_errors=True)


class AppImageParser:
    """Parse AppImage files and extract metadata"""

    def __init__(self, appimage_path: str, debug: bool = False):
        self.appimage_path = Path(appimage_path)
        self.debug = debug
        self._temp_dir: Optional[Path] = None
        self._mount_proc: Optional[subprocess.Popen] = None
        self._mount_point: Optional[Path] = None

        if not self.appimage_path.exists():
            raise FileNotFoundError(f"AppImage not found: {appimage_path}")

    def parse(self) -> AppImageInfo:
        """Extract all metadata from the AppImage"""
        self._temp_dir = Path(tempfile.mkdtemp(prefix="badgerdrop_"))

        if self.debug:
            print(f"[DEBUG] Mounting AppImage to: {self._temp_dir}")

        # Mount AppImage instead of extracting
        self._mount_appimage()

        # Parse .desktop file
        desktop_info = self._parse_desktop_file()

        # Find icon
        icon_path = self._find_icon(desktop_info.get("icon", "application"))

        info = AppImageInfo(
            name=desktop_info.get("name", self.appimage_path.stem),
            exec_cmd=desktop_info.get("exec", ""),
            icon_name=desktop_info.get("icon", "application"),
            icon_path=icon_path,
            categories=desktop_info.get("categories", []),
            comment=desktop_info.get("comment", ""),
            desktop_file_content=desktop_info.get("raw", ""),
            temp_extract_dir=self._temp_dir,
            mount_proc=self._mount_proc,
        )

        if self.debug:
            self._debug_print(info)

        return info

    def _mount_appimage(self):
        """Mount AppImage using --appimage-mount"""
        # Check if file is executable, make it executable if needed
        if not os.access(self.appimage_path, os.X_OK):
            if self.debug:
                print(f"[DEBUG] Making AppImage executable: {self.appimage_path}")
            try:
                self.appimage_path.chmod(self.appimage_path.stat().st_mode | 0o111)
            except PermissionError as e:
                raise RuntimeError(f"Cannot make AppImage executable: {e}")

        # Start mount process - it will print the mount point and block
        self._mount_proc = subprocess.Popen(
            [str(self.appimage_path), "--appimage-mount"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        # Read the mount point from stdout with timeout
        import select

        try:
            # Wait up to 10 seconds for the mount point
            ready, _, _ = select.select([self._mount_proc.stdout], [], [], 10.0)
            if not ready:
                self._mount_proc.kill()
                raise RuntimeError("Timeout waiting for AppImage mount point")

            mount_point_line = self._mount_proc.stdout.readline().strip()
            if not mount_point_line:
                # Check stderr for errors
                stderr_output = self._mount_proc.stderr.read()
                self._mount_proc.kill()
                raise RuntimeError(
                    f"Failed to get mount point from AppImage. Stderr: {stderr_output}"
                )
            self._mount_point = Path(mount_point_line)
            if self.debug:
                print(f"[DEBUG] AppImage mounted at: {self._mount_point}")
        except Exception as e:
            if self._mount_proc.poll() is None:
                self._mount_proc.kill()
            raise RuntimeError(f"Failed to mount AppImage: {e}")

    @property
    def _squashfs_root(self) -> Path:
        """Get the root of the mounted squashfs"""
        if not self._mount_point:
            raise RuntimeError("AppImage not mounted")
        return self._mount_point

    def _parse_desktop_file(self) -> dict:
        """Find and parse the .desktop file from mounted contents"""
        squashfs_root = self._squashfs_root

        # Find .desktop files
        desktop_files = list(squashfs_root.glob("*.desktop"))
        if not desktop_files:
            # Try usr/share/applications
            desktop_files = list(squashfs_root.glob("usr/share/applications/*.desktop"))

        if not desktop_files:
            raise RuntimeError("No .desktop file found in AppImage")

        desktop_file = desktop_files[0]

        if self.debug:
            print(f"[DEBUG] Found .desktop file: {desktop_file}")

        parser = configparser.ConfigParser(interpolation=None)
        parser.optionxform = str  # Preserve case

        with open(desktop_file, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            parser.read_string(content)

        if "Desktop Entry" not in parser:
            raise RuntimeError("Invalid .desktop file: no [Desktop Entry] section")

        entry = parser["Desktop Entry"]

        return {
            "name": entry.get("Name", ""),
            "exec": entry.get("Exec", ""),
            "icon": entry.get("Icon", ""),
            "categories": [
                c.strip() for c in entry.get("Categories", "").split(";") if c.strip()
            ],
            "comment": entry.get("Comment", ""),
            "raw": content,
        }

    def _find_icon(self, icon_name: str) -> Optional[Path]:
        """Find the icon file in the mounted AppImage"""
        squashfs_root = self._squashfs_root

        # Search paths for icons
        search_paths = [
            squashfs_root / f"{icon_name}.png",
            squashfs_root / f"{icon_name}.svg",
            squashfs_root
            / "usr"
            / "share"
            / "icons"
            / "hicolor"
            / "256x256"
            / "apps"
            / f"{icon_name}.png",
            squashfs_root
            / "usr"
            / "share"
            / "icons"
            / "hicolor"
            / "128x128"
            / "apps"
            / f"{icon_name}.png",
            squashfs_root
            / "usr"
            / "share"
            / "icons"
            / "hicolor"
            / "64x64"
            / "apps"
            / f"{icon_name}.png",
            squashfs_root
            / "usr"
            / "share"
            / "icons"
            / "hicolor"
            / "scalable"
            / "apps"
            / f"{icon_name}.svg",
            squashfs_root / "usr" / "share" / "pixmaps" / f"{icon_name}.png",
            squashfs_root / "usr" / "share" / "pixmaps" / f"{icon_name}.svg",
        ]

        for path in search_paths:
            if path.exists():
                if self.debug:
                    print(f"[DEBUG] Found icon: {path}")
                return path

        if self.debug:
            print(f"[DEBUG] Icon not found: {icon_name}")
        return None

    def _debug_print(self, info: AppImageInfo):
        """Print debug information about extracted AppImage"""
        print("\n" + "=" * 60)
        print("[DEBUG] AppImage Analysis Results")
        print("=" * 60)
        print("\n[METADATA]")
        print(f"  File: {self.appimage_path}")
        print(f"  Name: {info.name}")
        print(f"  Exec: {info.exec_cmd}")
        print(f"  Icon: {info.icon_name}")
        print(f"  Icon Path: {info.icon_path}")
        print(
            f"  Categories: {', '.join(info.categories) if info.categories else 'None'}"
        )
        print(f"  Comment: {info.comment}")
        print(f"  Version: {info.version if info.version else 'Not specified'}")
        print(f"  Temp Dir: {info.temp_extract_dir}")
        print("\n[DESKTOP FILE CONTENT]")
        print(info.desktop_file_content)
        print("=" * 60 + "\n")
