"""Edge case tests for invalid or corrupted AppImages."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from badgerdrop.core.appimage import AppImageParser
from badgerdrop.core.models import AppImageInfo
from badgerdrop.install.installer import AppImageInstaller


class TestInvalidAppImages:
    """Tests for handling invalid AppImage files."""

    def test_empty_appimage_file(self, tmp_path: Path):
        """Test handling of completely empty AppImage file."""
        empty_appimage = tmp_path / "empty.AppImage"
        empty_appimage.write_bytes(b"")
        empty_appimage.chmod(0o755)
        
        parser = AppImageParser(str(empty_appimage))
        
        # Should fail when trying to mount/parse
        with pytest.raises((ValueError, RuntimeError, OSError)):
            parser.parse()
        
        parser.cleanup()

    def test_corrupted_desktop_file_syntax(self, tmp_path: Path):
        """Test handling of AppImage with malformed .desktop file."""
        # Create a temp dir with malformed desktop file
        temp_dir = Path(tempfile.mkdtemp())
        desktop_file = temp_dir / "broken.desktop"
        desktop_file.write_text("This is not valid ini {{[")
        
        fake_appimage = tmp_path / "fake.AppImage"
        fake_appimage.write_bytes(b"#!/bin/bash")
        fake_appimage.chmod(0o755)
        
        parser = AppImageParser(str(fake_appimage))
        
        # Mock mount to return our temp dir with bad desktop file
        with patch.object(parser, '_mount_appimage', return_value=temp_dir):
            with patch.object(parser, '_find_desktop_file', return_value=desktop_file):
                # Should handle gracefully and return defaults
                info = parser.parse()
                
                # Should get default values for corrupted file
                assert info.name == "Unknown App"
                assert info.exec_cmd == ""
        
        parser.cleanup()

    def test_missing_desktop_file_in_appimage(self, tmp_path: Path):
        """Test handling of AppImage without any .desktop file."""
        # Create temp dir with no desktop file
        temp_dir = Path(tempfile.mkdtemp())
        (temp_dir / "somefile.txt").write_text("not a desktop file")
        
        fake_appimage = tmp_path / "no-desktop.AppImage"
        fake_appimage.write_bytes(b"#!/bin/bash")
        fake_appimage.chmod(0o755)
        
        parser = AppImageParser(str(fake_appimage))
        
        # Mock mount to return temp dir with no desktop file
        with patch.object(parser, '_mount_appimage', return_value=temp_dir):
            with patch.object(parser, '_find_desktop_file', return_value=None):
                # Should raise ValueError
                with pytest.raises(ValueError, match="No .desktop file found"):
                    parser.parse()
        
        parser.cleanup()

    def test_nonexistent_appimage_path(self):
        """Test parsing non-existent AppImage file."""
        fake_path = "/definitely/does/not/exist.AppImage"
        
        parser = AppImageParser(fake_path)
        
        # Should raise FileNotFoundError or similar
        with pytest.raises((FileNotFoundError, OSError)):
            parser.parse()

    def test_appimage_with_missing_icon(self, tmp_path: Path):
        """Test parsing AppImage that references non-existent icon."""
        # Create temp dir with desktop file referencing missing icon
        temp_dir = Path(tempfile.mkdtemp())
        desktop_file = temp_dir / "test.desktop"
        desktop_file.write_text("""[Desktop Entry]
Name=TestApp
Exec=TestApp
Icon=nonexistent-icon
Categories=Utility;
Comment=Test app
""")
        
        fake_appimage = tmp_path / "fake.AppImage"
        fake_appimage.write_bytes(b"#!/bin/bash")
        fake_appimage.chmod(0o755)
        
        parser = AppImageParser(str(fake_appimage))
        
        with patch.object(parser, '_mount_appimage', return_value=temp_dir):
            with patch.object(parser, '_find_desktop_file', return_value=desktop_file):
                info = parser.parse()
                
                # Should have icon name but no icon path
                assert info.icon_name == "nonexistent-icon"
                assert info.icon_path is None
        
        parser.cleanup()

    def test_desktop_file_missing_required_fields(self, tmp_path: Path):
        """Test parsing AppImage with incomplete .desktop file."""
        temp_dir = Path(tempfile.mkdtemp())
        desktop_file = temp_dir / "minimal.desktop"
        # Minimal desktop file - only Name, no Exec or Icon
        desktop_file.write_text("""[Desktop Entry]
Name=MinimalApp
""")
        
        fake_appimage = tmp_path / "fake.AppImage"
        fake_appimage.write_bytes(b"#!/bin/bash")
        fake_appimage.chmod(0o755)
        
        parser = AppImageParser(str(fake_appimage))
        
        with patch.object(parser, '_mount_appimage', return_value=temp_dir):
            with patch.object(parser, '_find_desktop_file', return_value=desktop_file):
                info = parser.parse()
                
                # Should get defaults for missing fields
                assert info.name == "MinimalApp"
                assert info.exec_cmd == ""  # Default
                assert info.icon_name == "application-x-executable"  # Default
        
        parser.cleanup()

    def test_install_with_invalid_appimage_info(self, tmp_path: Path):
        """Test install with AppImageInfo missing required fields."""
        appimage_file = tmp_path / "test.AppImage"
        appimage_file.write_bytes(b"content")
        
        installer = AppImageInstaller(tmp_path / "apps")
        
        # Create info with empty required fields
        info = AppImageInfo(
            name="",
            exec_cmd="",
            icon_name="",
        )
        
        # Should handle gracefully - creates desktop entry with empty name
        # This may produce weird results but shouldn't crash
        result = installer.install(str(appimage_file), info)
        assert result is not None
        assert result.name == ""

    def test_appimage_with_binary_desktop_file(self, tmp_path: Path):
        """Test parsing AppImage with binary (non-text) .desktop file."""
        fake_appimage = tmp_path / "fake.AppImage"
        fake_appimage.write_bytes(b"#!/bin/bash\necho 'test'")
        fake_appimage.chmod(0o755)
        
        # Create temp dir with binary desktop file
        temp_dir = Path(tempfile.mkdtemp())
        desktop_file = temp_dir / "test.desktop"
        # Write binary content with high bytes
        desktop_file.write_bytes(bytes([0xFF, 0xFE] * 100))
        
        parser = AppImageParser(str(fake_appimage))
        
        # Should raise UnicodeDecodeError when trying to read binary desktop file
        with patch.object(parser, '_temp_extract_dir', temp_dir):
            with patch.object(parser, '_mount_appimage', return_value=temp_dir):
                with patch.object(parser, '_find_desktop_file', return_value=desktop_file):
                    # The actual error occurs when reading the file content
                    with pytest.raises((UnicodeDecodeError, Exception)):
                        info = parser.parse()
        
        parser.cleanup()


class TestInvalidInstallationScenarios:
    """Tests for invalid installation scenarios."""

    def test_install_with_none_icon_path(self, tmp_path: Path):
        """Test install when AppImageInfo.icon_path is None."""
        appimage_file = tmp_path / "test.AppImage"
        appimage_file.write_bytes(b"fake content")
        
        install_dir = tmp_path / "apps"
        install_dir.mkdir()
        
        installer = AppImageInstaller(install_dir)
        
        info = AppImageInfo(
            name="TestApp",
            exec_cmd="TestApp",
            icon_name="testapp",
            icon_path=None,  # No icon
        )
        
        # Should succeed without icon
        installed = installer.install(str(appimage_file), info)
        
        assert installed is not None
        assert installed.name == "TestApp"

    def test_install_source_file_not_readable(self, tmp_path: Path):
        """Test install when source AppImage is not readable."""
        from badgerdrop.utils.file_copier import FileCopierError
        
        appimage_file = tmp_path / "unreadable.AppImage"
        appimage_file.write_bytes(b"content")
        appimage_file.chmod(0o000)  # No permissions
        
        try:
            installer = AppImageInstaller(tmp_path / "apps")
            
            info = AppImageInfo(
                name="TestApp",
                exec_cmd="TestApp",
                icon_name="testapp",
            )
            
            # Should raise FileCopierError when trying to copy unreadable file
            with pytest.raises((PermissionError, FileCopierError, OSError)):
                installer.install(str(appimage_file), info)
        finally:
            # Restore permissions for cleanup
            appimage_file.chmod(0o644)

    def test_install_to_file_instead_of_directory(self, tmp_path: Path):
        """Test install when target path is a file, not directory."""
        appimage_file = tmp_path / "test.AppImage"
        appimage_file.write_bytes(b"content")
        
        # Create a file instead of directory
        target_file = tmp_path / "not_a_dir"
        target_file.write_text("I am a file")
        
        installer = AppImageInstaller(target_file)
        
        info = AppImageInfo(
            name="TestApp",
            exec_cmd="TestApp",
            icon_name="testapp",
        )
        
        # Should fail when trying to use file as directory
        with pytest.raises((NotADirectoryError, OSError)):
            installer.install(str(appimage_file), info)
