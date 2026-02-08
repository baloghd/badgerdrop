"""Installation logic for AppImages"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional

from .appimage import AppImageInfo
from .installed import InstalledApp, InstalledAppsManager
from .utils import DesktopManager, FileCopier, IconInstaller

logger = logging.getLogger(__name__)


class AppImageInstaller:
    """Install AppImages to the user's system"""

    def __init__(self, install_dir: Optional[Path] = None):
        self.apps_dir = (
            install_dir.expanduser() if install_dir else Path.home() / "Applications"
        )
        self.local_share = Path.home() / ".local" / "share"
        self.applications_dir = self.local_share / "applications"
        self.icons_dir = self.local_share / "icons" / "hicolor"
        self.registry = InstalledAppsManager()

        # Initialize utility components
        self._file_copier = FileCopier()
        self._icon_installer = IconInstaller(self.icons_dir)
        self._desktop_manager = DesktopManager(self.applications_dir, self.icons_dir)

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
        safe_name = self._desktop_manager._sanitize_filename(info.name)
        desktop_file = self.applications_dir / f"{safe_name}.desktop"

        logger.debug("Installing to: %s", target_appimage)

        try:
            # Copy AppImage with progress
            self._file_copier.copy_with_progress(
                appimage_src, target_appimage, progress_callback
            )

            # Make executable if requested
            if make_executable:
                target_appimage.chmod(0o755)
                logger.debug("Made %s executable", target_appimage)
            else:
                logger.debug(
                    "Skipped making %s executable (user preference)", target_appimage
                )

            # Install icon if found
            if info.icon_path:
                self._icon_installer.install_icon(info.icon_path, info.icon_name)

            # Create .desktop file
            self._desktop_manager.create_desktop_entry(target_appimage, info)

            # Update desktop database
            self._desktop_manager.update_desktop_database()

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

            logger.info("Successfully installed %s", info.name)

            return installed_app

        except Exception as e:
            logger.error("Installation failed: %s", e)
            raise
