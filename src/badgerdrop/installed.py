"""Track installed AppImages with metadata"""

import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Optional


@dataclass
class InstalledApp:
    """Metadata about an installed AppImage"""

    name: str
    version: str
    source_path: str  # Original file location
    install_path: str  # Where it was copied to
    icon_name: str
    categories: List[str]
    install_date: str
    comment: Optional[str] = None
    desktop_file: Optional[str] = None


class InstalledAppsManager:
    """Manage registry of installed AppImages"""

    def __init__(self):
        self.config_dir = Path.home() / ".config" / "badgerdrop"
        self.registry_file = self.config_dir / "installed.json"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.apps: List[InstalledApp] = []
        self._load_registry()

    def _load_registry(self):
        """Load installed apps from registry file"""
        if self.registry_file.exists():
            try:
                data = json.loads(self.registry_file.read_text())
                self.apps = [InstalledApp(**app) for app in data.get("apps", [])]
            except (json.JSONDecodeError, TypeError):
                self.apps = []

    def _save_registry(self):
        """Save installed apps to registry file"""
        data = {"apps": [asdict(app) for app in self.apps]}
        self.registry_file.write_text(json.dumps(data, indent=2))

    def add(self, app: InstalledApp):
        """Add an app to the registry"""
        # Remove any existing entry with same install_path
        self.apps = [a for a in self.apps if a.install_path != app.install_path]
        self.apps.append(app)
        self._save_registry()

    def remove(self, install_path: str):
        """Remove an app from the registry"""
        self.apps = [a for a in self.apps if a.install_path != install_path]
        self._save_registry()

    def get_all(self) -> List[InstalledApp]:
        """Get all installed apps, sorted by install date (newest first)"""
        return sorted(self.apps, key=lambda a: a.install_date, reverse=True)

    def get_by_name(self, name: str) -> Optional[InstalledApp]:
        """Find an app by name"""
        for app in self.apps:
            if app.name.lower() == name.lower():
                return app
        return None

    def is_installed(self, name: str) -> bool:
        """Check if an app is already installed"""
        return any(app.name.lower() == name.lower() for app in self.apps)

    def get_by_filename(self, filename: str) -> Optional[InstalledApp]:
        """Find an app by its filename (basename of install_path)"""
        for app in self.apps:
            if Path(app.install_path).name == filename:
                return app
        return None
