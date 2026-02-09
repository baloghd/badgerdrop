"""Dataclass models for BadgerDrop core domain"""

from dataclasses import dataclass, field
from pathlib import Path
from subprocess import Popen


@dataclass
class AppImageInfo:
    """Extracted information from an AppImage"""

    name: str
    exec_cmd: str
    icon_name: str
    icon_path: Path | None = None
    categories: list[str] = field(default_factory=list)
    comment: str = ""
    desktop_file_content: str = ""
    temp_extract_dir: Path | None = None
    mount_proc: Popen | None = None
    version: str | None = None

    def __post_init__(self) -> None:
        """Post-initialization to ensure categories is a list"""
        if self.categories is None:
            self.categories = []

    def cleanup(self) -> None:
        """Clean up temporary files and unmount AppImage"""
        import shutil

        # Terminate mount process if exists
        if self.mount_proc is not None:
            self.mount_proc.terminate()
            try:
                self.mount_proc.wait(timeout=5)
            except Exception:
                self.mount_proc.kill()
            self.mount_proc = None

        # Remove temp directory if exists
        if self.temp_extract_dir is not None and self.temp_extract_dir.exists():
            shutil.rmtree(self.temp_extract_dir, ignore_errors=True)
            self.temp_extract_dir = None


@dataclass
class InstalledApp:
    """Metadata about an installed AppImage"""

    name: str
    version: str
    source_path: str  # Original file location
    install_path: str  # Where it was copied to
    icon_name: str
    install_date: str
    categories: list[str] = field(default_factory=list)
    comment: str | None = None
    desktop_file: str | None = None

    def __post_init__(self) -> None:
        """Post-initialization to ensure categories is a list"""
        if self.categories is None:
            self.categories = []


@dataclass
class AppSettings:
    """Application settings"""

    play_sound_on_install: bool = True
    sound_theme: str = "default"
    auto_make_executable: bool = True
    show_notifications: bool = True
    install_directory: str = "~/Applications"

    def __post_init__(self) -> None:
        """Post-initialization to validate install directory"""
        if not self.install_directory or not self.install_directory.strip():
            self.install_directory = "~/Applications"
