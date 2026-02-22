"""Integration tests for the full installation flow."""

import os
import time
from pathlib import Path
from unittest.mock import patch

import pytest

from badgerdrop.core.models import AppImageInfo, InstalledApp
from badgerdrop.install.installer import AppImageInstaller
from badgerdrop.utils import DesktopManagerError, IconInstallerError


class TestInstallationFlow:
    """End-to-end tests for the AppImage installation process."""

    def test_full_install_workflow(
        self, tmp_path: Path, mock_appimage_info, mock_progress_callback
    ):
        """Test complete installation workflow with mock AppImage."""
        # Create a mock AppImage file
        source_appimage = tmp_path / "TestApp-1.0.0.AppImage"
        source_appimage.write_bytes(b"mock appimage content")
        source_appimage.chmod(0o755)
        
        # Setup directories
        install_dir = tmp_path / "Applications"
        local_share = tmp_path / ".local" / "share"
        applications_dir = local_share / "applications"
        icons_dir = local_share / "icons" / "hicolor"
        
        # Create installer with custom paths
        installer = AppImageInstaller.__new__(AppImageInstaller)
        installer.apps_dir = install_dir
        installer.local_share = local_share
        installer.applications_dir = applications_dir
        installer.icons_dir = icons_dir
        
        from badgerdrop.utils import FileCopier, IconInstaller, DesktopManager
        installer._file_copier = FileCopier()
        installer._icon_installer = IconInstaller(installer.icons_dir)
        installer._desktop_manager = DesktopManager(installer.applications_dir)
        
        # Perform installation
        installed_app = installer.install(
            str(source_appimage),
            mock_appimage_info,
            make_executable=True,
            progress_callback=mock_progress_callback,
        )
        
        # Verify results
        assert isinstance(installed_app, InstalledApp)
        assert installed_app.name == "TestApp"
        
        # Verify file was copied
        target_path = install_dir / "TestApp-1.0.0.AppImage"
        assert target_path.exists()
        assert target_path.read_bytes() == b"mock appimage content"
        
        # Verify permissions
        assert os.access(target_path, os.X_OK)
        
        # Verify .desktop file was created
        desktop_file = applications_dir / "testapp.desktop"
        assert desktop_file.exists()
        desktop_content = desktop_file.read_text()
        assert "Name=TestApp" in desktop_content
        assert str(target_path) in desktop_content
        
        # Verify progress was reported
        assert len(mock_progress_callback.calls) > 0
        final_call = mock_progress_callback.calls[-1]
        assert final_call["phase"] == "copying"
        assert final_call["current"] == final_call["total"]

    def test_install_without_executable_permission(
        self, tmp_path: Path, mock_appimage_info
    ):
        """Test installation with make_executable=False."""
        source_appimage = tmp_path / "TestApp.AppImage"
        source_appimage.write_bytes(b"content")
        
        install_dir = tmp_path / "Applications"
        local_share = tmp_path / ".local" / "share"
        
        installer = AppImageInstaller.__new__(AppImageInstaller)
        installer.apps_dir = install_dir
        installer.local_share = local_share
        installer.applications_dir = local_share / "applications"
        installer.icons_dir = local_share / "icons" / "hicolor"
        
        from badgerdrop.utils import FileCopier, IconInstaller, DesktopManager
        installer._file_copier = FileCopier()
        installer._icon_installer = IconInstaller(installer.icons_dir)
        installer._desktop_manager = DesktopManager(installer.applications_dir)
        
        installed_app = installer.install(
            str(source_appimage),
            mock_appimage_info,
            make_executable=False,
        )
        
        target_path = install_dir / "TestApp.AppImage"
        assert target_path.exists()
        # Should NOT be executable
        assert not os.access(target_path, os.X_OK)

    def test_install_with_icon(self, tmp_path: Path, mock_progress_callback):
        """Test installation with icon extraction and installation."""
        source_appimage = tmp_path / "TestApp.AppImage"
        source_appimage.write_bytes(b"content")
        
        # Create a mock icon file
        icon_path = tmp_path / "testapp.png"
        icon_path.write_bytes(b"fake icon data")
        
        # Create AppImageInfo with icon
        info = AppImageInfo(
            name="TestApp",
            exec_cmd="TestApp",
            icon_name="testapp",
            icon_path=icon_path,
            categories=["Graphics"],
            comment="App with icon",
            version="1.0.0",
        )
        
        install_dir = tmp_path / "Applications"
        local_share = tmp_path / ".local" / "share"
        icons_dir = local_share / "icons" / "hicolor"
        
        installer = AppImageInstaller.__new__(AppImageInstaller)
        installer.apps_dir = install_dir
        installer.local_share = local_share
        installer.applications_dir = local_share / "applications"
        installer.icons_dir = icons_dir
        
        from badgerdrop.utils import FileCopier, IconInstaller, DesktopManager
        installer._file_copier = FileCopier()
        installer._icon_installer = IconInstaller(installer.icons_dir)
        installer._desktop_manager = DesktopManager(installer.applications_dir)
        
        installed_app = installer.install(
            str(source_appimage),
            info,
            make_executable=True,
        )
        
        # Verify icon was installed
        target_icon = icons_dir / "128x128" / "apps" / "testapp.png"
        assert target_icon.exists()
        assert target_icon.read_bytes() == b"fake icon data"

    def test_install_registry_integration(self, tmp_path: Path, mock_appimage_info):
        """Test that installation creates proper registry entry."""
        source_appimage = tmp_path / "TestApp.AppImage"
        source_appimage.write_bytes(b"content")
        
        install_dir = tmp_path / "Applications"
        local_share = tmp_path / ".local" / "share"
        
        installer = AppImageInstaller.__new__(AppImageInstaller)
        installer.apps_dir = install_dir
        installer.local_share = local_share
        installer.applications_dir = local_share / "applications"
        installer.icons_dir = local_share / "icons" / "hicolor"
        
        from badgerdrop.utils import FileCopier, IconInstaller, DesktopManager
        installer._file_copier = FileCopier()
        installer._icon_installer = IconInstaller(installer.icons_dir)
        installer._desktop_manager = DesktopManager(installer.applications_dir)
        
        installed_app = installer.install(
            str(source_appimage),
            mock_appimage_info,
            make_executable=True,
        )
        
        # Verify registry entry data
        assert installed_app.name == "TestApp"
        assert installed_app.version == "1.0.0"
        assert installed_app.source_path == str(source_appimage)
        assert installed_app.install_path == str(install_dir / "TestApp.AppImage")
        assert installed_app.icon_name == "testapp"
        assert installed_app.install_date is not None
        assert installed_app.desktop_file is not None

    def test_install_cleanup_on_success(self, tmp_path: Path, mock_appimage_info):
        """Test that resources are cleaned up after successful install."""
        # This test verifies no temp files are left behind
        source_appimage = tmp_path / "TestApp.AppImage"
        source_appimage.write_bytes(b"content")
        
        # Track temp directories created during install
        temp_dirs_before = set(Path(tmp_path).glob("badgerdrop_*"))
        
        install_dir = tmp_path / "Applications"
        local_share = tmp_path / ".local" / "share"
        
        installer = AppImageInstaller.__new__(AppImageInstaller)
        installer.apps_dir = install_dir
        installer.local_share = local_share
        installer.applications_dir = local_share / "applications"
        installer.icons_dir = local_share / "icons" / "hicolor"
        
        from badgerdrop.utils import FileCopier, IconInstaller, DesktopManager
        installer._file_copier = FileCopier()
        installer._icon_installer = IconInstaller(installer.icons_dir)
        installer._desktop_manager = DesktopManager(installer.applications_dir)
        
        installer.install(
            str(source_appimage),
            mock_appimage_info,
            make_executable=True,
        )
        
        # No additional temp dirs should exist after install
        temp_dirs_after = set(Path(tmp_path).glob("badgerdrop_*"))
        assert temp_dirs_after == temp_dirs_before


class TestInstallationFlowWithRealAppImage:
    """Integration tests using the real hello-world AppImage."""

    @pytest.mark.skipif(
        not (Path(__file__).parent.parent / "assets" / "hello-world-test-x86_64.AppImage").exists(),
        reason="hello-world AppImage not available",
    )
    def test_real_appimage_install(self, tmp_path: Path):
        """Test installation with real hello-world AppImage."""
        appimage_path = Path(__file__).parent.parent / "assets" / "hello-world-test-x86_64.AppImage"
        
        install_dir = tmp_path / "Applications"
        local_share = tmp_path / ".local" / "share"
        
        installer = AppImageInstaller.__new__(AppImageInstaller)
        installer.apps_dir = install_dir
        installer.local_share = local_share
        installer.applications_dir = local_share / "applications"
        installer.icons_dir = local_share / "icons" / "hicolor"
        
        from badgerdrop.utils import FileCopier, IconInstaller, DesktopManager
        installer._file_copier = FileCopier()
        installer._icon_installer = IconInstaller(installer.icons_dir)
        installer._desktop_manager = DesktopManager(installer.applications_dir)
        
        # Parse the AppImage first
        from badgerdrop.core.appimage import AppImageParser
        parser = AppImageParser(str(appimage_path))
        info = parser.parse()
        assert info.icon_path is not None, "Expected icon_path to be set"
        
        try:
            installed_app = installer.install(
                str(appimage_path),
                info,
                make_executable=True,
            )
            
            # Verify installation
            assert installed_app.name == info.name
            assert Path(installed_app.install_path).exists()
            
            # Verify desktop file
            assert installed_app.desktop_file is not None
            desktop_path = Path(installed_app.desktop_file)
            assert desktop_path.exists()
            
        finally:
            parser.cleanup()
