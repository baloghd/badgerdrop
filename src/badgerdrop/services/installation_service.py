"""Installation orchestration service for AppImages."""

import logging
import threading
import traceback
from collections.abc import Callable
from pathlib import Path

from badgerdrop.core.models import AppImageInfo, InstalledApp
from badgerdrop.install.installer import AppImageInstaller

logger = logging.getLogger(__name__)


class InstallationServiceError(Exception):
    """Exception raised for errors in the installation service."""

    pass


class InstallationService:
    """Service for orchestrating AppImage installations.

    This service manages the installation process including:
    - Running installation in a background thread
    - Progress callbacks
    - Success/error callbacks
    - Sound notifications (optional)

    The service owns the installation thread lifecycle and provides
    an async interface with callbacks for UI updates.
    """

    def __init__(self, debug: bool = False):
        """Initialize the installation service.

        Args:
            debug: Enable debug output
        """
        self.debug = debug

    def install_async(
        self,
        appimage_path: Path,
        info: AppImageInfo,
        make_executable: bool,
        progress_callback: Callable[[str, int, int], None],
        success_callback: Callable[[InstalledApp], None],
        error_callback: Callable[[Exception], None],
        cleanup_callback: Callable[[], None] | None = None,
    ) -> None:
        """Install an AppImage asynchronously in a background thread.

        Args:
            appimage_path: Path to the AppImage file
            info: AppImage metadata
            make_executable: Whether to make the AppImage executable
            progress_callback: Called with (phase, bytes_copied, total_bytes)
            success_callback: Called with InstalledApp on success
            error_callback: Called with Exception on failure
            cleanup_callback: Optional cleanup to run after completion
        """

        def install_worker():
            """Run installation in background thread."""
            try:
                installer = AppImageInstaller()
                installed_app = installer.install(
                    str(appimage_path),
                    info,
                    make_executable=make_executable,
                    progress_callback=progress_callback,
                )
                success_callback(installed_app)
            except Exception as e:
                logger.error("Installation failed: %s", e)
                if self.debug:
                    traceback.print_exc()
                error_callback(e)
            finally:
                if cleanup_callback:
                    cleanup_callback()

        # Start installation in background thread
        thread = threading.Thread(target=install_worker, daemon=True)
        thread.start()

        logger.debug("Started installation thread for %s", appimage_path.name)
