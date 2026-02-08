"""Installation orchestration service for AppImages."""

import threading
import traceback
from pathlib import Path
from typing import Callable, Optional

from ..appimage import AppImageInfo
from ..installer import AppImageInstaller
from ..installed import InstalledApp


class InstallationServiceError(Exception):
    """Exception raised for installation service errors."""

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
        cleanup_callback: Optional[Callable[[], None]] = None,
    ) -> None:
        """Install an AppImage asynchronously in a background thread.

        Args:
            appimage_path: Path to the AppImage file
            info: AppImage metadata
            make_executable: Whether to make the AppImage executable
            progress_callback: Called with (phase, bytes_copied, total_bytes)
            success_callback: Called with InstalledApp on success
            error_callback: Called with Exception on failure
            cleanup_callback: Optional cleanup to run after completion (success or error)
        """

        def install_worker():
            """Run installation in background thread."""
            try:
                installer = AppImageInstaller(debug=self.debug)
                installed_app = installer.install(
                    str(appimage_path),
                    info,
                    make_executable=make_executable,
                    progress_callback=progress_callback,
                )
                success_callback(installed_app)
            except Exception as e:
                if self.debug:
                    print(f"[DEBUG] Installation failed: {e}")
                    traceback.print_exc()
                error_callback(e)
            finally:
                if cleanup_callback:
                    cleanup_callback()

        # Start installation in background thread
        thread = threading.Thread(target=install_worker, daemon=True)
        thread.start()

        if self.debug:
            print(f"[DEBUG] Started installation thread for {appimage_path.name}")
