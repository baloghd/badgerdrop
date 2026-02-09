"""Pydantic models for BadgerDrop core domain"""

from pathlib import Path
from subprocess import Popen

from pydantic import BaseModel, Field, field_validator


class AppImageInfo(BaseModel):
    """Extracted information from an AppImage"""

    name: str
    exec_cmd: str
    icon_name: str
    icon_path: Path | None = None
    categories: list[str] = Field(default_factory=list)
    comment: str = ""
    desktop_file_content: str = ""
    temp_extract_dir: Path | None = None
    mount_proc: Popen | None = None
    version: str | None = None

    @field_validator("categories", mode="before")
    @classmethod
    def ensure_categories_list(cls, v):
        """Ensure categories is always a list"""
        if v is None:
            return []
        return v

    class Config:
        """Pydantic config - allow arbitrary types like Path and Popen"""

        arbitrary_types_allowed = True

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


class InstalledApp(BaseModel):
    """Metadata about an installed AppImage"""

    name: str
    version: str
    source_path: str  # Original file location
    install_path: str  # Where it was copied to
    icon_name: str
    categories: list[str] = Field(default_factory=list)
    install_date: str
    comment: str | None = None
    desktop_file: str | None = None


class AppSettings(BaseModel):
    """Application settings"""

    play_sound_on_install: bool = True
    sound_theme: str = "default"
    auto_make_executable: bool = True
    show_notifications: bool = True
    install_directory: str = "~/Applications"

    @field_validator("install_directory")
    @classmethod
    def validate_install_directory(cls, v: str) -> str:
        """Ensure install directory is not empty"""
        if not v or not v.strip():
            return "~/Applications"
        return v
