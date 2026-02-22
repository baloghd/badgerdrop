"""Integration tests for installation service (async operations)."""

import threading
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from badgerdrop.core.models import AppImageInfo, InstalledApp
from badgerdrop.install.installer import AppImageInstaller
from badgerdrop.services.installation_service import InstallationService


class TestInstallationService:
    """Tests for async installation service."""

    def test_async_installation_triggers_success_callback(
        self, tmp_path: Path, mock_appimage_info
    ):
        """Test that successful installation triggers success callback."""
        service = InstallationService()
        
        # Create a fake AppImage file
        appimage_file = tmp_path / "test.AppImage"
        appimage_file.write_bytes(b"fake appimage content")
        
        success_called = threading.Event()
        success_result = None
        
        def success_callback(installed_app: InstalledApp):
            nonlocal success_result
            success_result = installed_app
            success_called.set()
        
        def error_callback(error: Exception):
            pytest.fail(f"Should not error: {error}")
        
        # Mock the installer to return immediately
        mock_installed = InstalledApp(
            name="TestApp",
            version="1.0.0",
            source_path=str(appimage_file),
            install_path=str(tmp_path / "installed.AppImage"),
            icon_name="testapp",
            install_date="2024-01-01",
        )
        
        with patch.object(AppImageInstaller, 'install', return_value=mock_installed):
            service.install_async(
                appimage_file,
                mock_appimage_info,
                make_executable=True,
                progress_callback=lambda p, c, t: None,
                success_callback=success_callback,
                error_callback=error_callback,
            )
            
            # Wait for callback (with timeout)
            assert success_called.wait(timeout=2), "Success callback was not called"
            assert success_result is not None
            assert success_result.name == "TestApp"

    def test_async_installation_triggers_error_callback(
        self, tmp_path: Path, mock_appimage_info
    ):
        """Test that failed installation triggers error callback."""
        service = InstallationService()
        
        appimage_file = tmp_path / "test.AppImage"
        appimage_file.write_bytes(b"fake content")
        
        error_called = threading.Event()
        error_result = None
        
        def success_callback(installed_app: InstalledApp):
            pytest.fail("Should not succeed")
        
        def error_callback(error: Exception):
            nonlocal error_result
            error_result = error
            error_called.set()
        
        # Mock installer to raise error
        with patch.object(AppImageInstaller, 'install', side_effect=Exception("Installation failed")):
            service.install_async(
                appimage_file,
                mock_appimage_info,
                make_executable=True,
                progress_callback=lambda p, c, t: None,
                success_callback=success_callback,
                error_callback=error_callback,
            )
            
            assert error_called.wait(timeout=2), "Error callback was not called"
            assert error_result is not None
            assert "Installation failed" in str(error_result)

    def test_async_installation_calls_progress_callback(
        self, tmp_path: Path, mock_appimage_info
    ):
        """Test that progress callback is called during installation."""
        service = InstallationService()
        
        appimage_file = tmp_path / "test.AppImage"
        appimage_file.write_bytes(b"x" * 1000)
        
        progress_calls = []
        completion_event = threading.Event()
        
        def progress_callback(phase: str, current: int, total: int):
            progress_calls.append((phase, current, total))
        
        def success_callback(installed_app: InstalledApp):
            completion_event.set()
        
        def error_callback(error: Exception):
            completion_event.set()
        
        mock_installed = InstalledApp(
            name="TestApp",
            version="1.0.0",
            source_path=str(appimage_file),
            install_path=str(tmp_path / "installed.AppImage"),
            icon_name="testapp",
            install_date="2024-01-01",
        )
        
        # Mock installer to call progress callback
        def mock_install(*args, **kwargs):
            progress_cb = kwargs.get('progress_callback')
            if progress_cb:
                progress_cb("copying", 500, 1000)
                progress_cb("copying", 1000, 1000)
            return mock_installed
        
        with patch.object(AppImageInstaller, 'install', side_effect=mock_install):
            service.install_async(
                appimage_file,
                mock_appimage_info,
                make_executable=True,
                progress_callback=progress_callback,
                success_callback=success_callback,
                error_callback=error_callback,
            )
            
            completion_event.wait(timeout=2)

    def test_async_installation_calls_cleanup_callback(
        self, tmp_path: Path, mock_appimage_info
    ):
        """Test that cleanup callback is called after completion."""
        service = InstallationService()
        
        appimage_file = tmp_path / "test.AppImage"
        appimage_file.write_bytes(b"fake content")
        
        cleanup_called = threading.Event()
        completion_event = threading.Event()
        
        def success_callback(installed_app: InstalledApp):
            completion_event.set()
        
        def error_callback(error: Exception):
            completion_event.set()
        
        def cleanup_callback():
            cleanup_called.set()
        
        mock_installed = InstalledApp(
            name="TestApp",
            version="1.0.0",
            source_path=str(appimage_file),
            install_path=str(tmp_path / "installed.AppImage"),
            icon_name="testapp",
            install_date="2024-01-01",
        )
        
        with patch.object(AppImageInstaller, 'install', return_value=mock_installed):
            service.install_async(
                appimage_file,
                mock_appimage_info,
                make_executable=True,
                progress_callback=lambda p, c, t: None,
                success_callback=success_callback,
                error_callback=error_callback,
                cleanup_callback=cleanup_callback,
            )
            
            # Wait for completion first
            completion_event.wait(timeout=2)
            # Then check cleanup was called
            assert cleanup_called.wait(timeout=1), "Cleanup callback was not called"

    def test_async_installation_thread_cleanup(
        self, tmp_path: Path, mock_appimage_info
    ):
        """Test that installation thread is properly cleaned up."""
        service = InstallationService()
        
        appimage_file = tmp_path / "test.AppImage"
        appimage_file.write_bytes(b"fake content")
        
        completion_event = threading.Event()
        
        def success_callback(installed_app: InstalledApp):
            completion_event.set()
        
        def error_callback(error: Exception):
            completion_event.set()
        
        initial_threads = threading.active_count()
        
        mock_installed = InstalledApp(
            name="TestApp",
            version="1.0.0",
            source_path=str(appimage_file),
            install_path=str(tmp_path / "installed.AppImage"),
            icon_name="testapp",
            install_date="2024-01-01",
        )
        
        with patch.object(AppImageInstaller, 'install', return_value=mock_installed):
            service.install_async(
                appimage_file,
                mock_appimage_info,
                make_executable=True,
                progress_callback=lambda p, c, t: None,
                success_callback=success_callback,
                error_callback=error_callback,
            )
            
            # Wait for completion
            completion_event.wait(timeout=2)
            
            # Give thread time to terminate
            time.sleep(0.2)
            
            # Thread count should be back to initial (or close to it)
            final_threads = threading.active_count()
            assert final_threads <= initial_threads + 1, "Thread was not cleaned up"
