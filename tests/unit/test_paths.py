"""Unit tests for paths module."""

from pathlib import Path
from unittest.mock import patch

import pytest

from badgerdrop.config.paths import (
    get_applications_dir,
    get_config_dir,
    get_default_install_dir,
    get_icons_dir,
    get_installed_registry_file,
    get_local_share_dir,
    get_settings_file,
)


class TestGetConfigDir:
    """Tests for get_config_dir function."""

    def test_returns_path(self):
        """Test that function returns a Path object."""
        result = get_config_dir()
        assert isinstance(result, Path)

    def test_creates_directory(self, tmp_path: Path):
        """Test that function creates the directory if it doesn't exist."""
        config_dir = tmp_path / ".config" / "badgerdrop"
        
        with patch("pathlib.Path.home", return_value=tmp_path):
            result = get_config_dir()
        
        assert result.exists()
        assert result.is_dir()

    def test_correct_path(self, tmp_path: Path):
        """Test that function returns correct path."""
        expected = tmp_path / ".config" / "badgerdrop"
        
        with patch("pathlib.Path.home", return_value=tmp_path):
            result = get_config_dir()
        
        assert result == expected


class TestGetSettingsFile:
    """Tests for get_settings_file function."""

    def test_returns_path(self, tmp_path: Path):
        """Test that function returns a Path object."""
        with patch("pathlib.Path.home", return_value=tmp_path):
            result = get_settings_file()
        
        assert isinstance(result, Path)
        assert result.name == "settings.json"

    def test_in_config_dir(self, tmp_path: Path):
        """Test that settings file is in config directory."""
        with patch("pathlib.Path.home", return_value=tmp_path):
            result = get_settings_file()
            expected_parent = get_config_dir()
        
        assert result.parent == expected_parent


class TestGetInstalledRegistryFile:
    """Tests for get_installed_registry_file function."""

    def test_returns_path(self, tmp_path: Path):
        """Test that function returns a Path object."""
        with patch("pathlib.Path.home", return_value=tmp_path):
            result = get_installed_registry_file()
        
        assert isinstance(result, Path)
        assert result.name == "installed.json"

    def test_in_config_dir(self, tmp_path: Path):
        """Test that registry file is in config directory."""
        with patch("pathlib.Path.home", return_value=tmp_path):
            result = get_installed_registry_file()
            expected_parent = get_config_dir()
        
        assert result.parent == expected_parent


class TestGetLocalShareDir:
    """Tests for get_local_share_dir function."""

    def test_returns_path(self, tmp_path: Path):
        """Test that function returns a Path object."""
        with patch("pathlib.Path.home", return_value=tmp_path):
            result = get_local_share_dir()
        
        assert isinstance(result, Path)
        assert result.name == "share"

    def test_correct_path(self, tmp_path: Path):
        """Test that function returns correct path."""
        with patch("pathlib.Path.home", return_value=tmp_path):
            result = get_local_share_dir()
        
        assert result == tmp_path / ".local" / "share"


class TestGetApplicationsDir:
    """Tests for get_applications_dir function."""

    def test_returns_path(self, tmp_path: Path):
        """Test that function returns a Path object."""
        with patch("pathlib.Path.home", return_value=tmp_path):
            result = get_applications_dir()
        
        assert isinstance(result, Path)

    def test_creates_directory(self, tmp_path: Path):
        """Test that function creates the directory if it doesn't exist."""
        apps_dir = tmp_path / ".local" / "share" / "applications"
        
        with patch("pathlib.Path.home", return_value=tmp_path):
            result = get_applications_dir()
        
        assert result.exists()
        assert result.is_dir()

    def test_in_local_share(self, tmp_path: Path):
        """Test that applications dir is in local share."""
        with patch("pathlib.Path.home", return_value=tmp_path):
            result = get_applications_dir()
            expected_parent = get_local_share_dir()
        
        assert result.parent == expected_parent


class TestGetIconsDir:
    """Tests for get_icons_dir function."""

    def test_returns_path(self, tmp_path: Path):
        """Test that function returns a Path object."""
        with patch("pathlib.Path.home", return_value=tmp_path):
            result = get_icons_dir()
        
        assert isinstance(result, Path)

    def test_creates_directory(self, tmp_path: Path):
        """Test that function creates the directory if it doesn't exist."""
        icons_dir = tmp_path / ".local" / "share" / "icons" / "hicolor"
        
        with patch("pathlib.Path.home", return_value=tmp_path):
            result = get_icons_dir()
        
        assert result.exists()
        assert result.is_dir()

    def test_in_local_share_icons(self, tmp_path: Path):
        """Test that icons dir is in local share/icons."""
        with patch("pathlib.Path.home", return_value=tmp_path):
            result = get_icons_dir()
            expected_parent = get_local_share_dir() / "icons"
        
        assert result.parent == expected_parent


class TestGetDefaultInstallDir:
    """Tests for get_default_install_dir function."""

    def test_returns_path(self, tmp_path: Path):
        """Test that function returns a Path object."""
        with patch("pathlib.Path.home", return_value=tmp_path):
            result = get_default_install_dir()
        
        assert isinstance(result, Path)

    def test_creates_directory(self, tmp_path: Path):
        """Test that function creates the directory if it doesn't exist."""
        install_dir = tmp_path / "Applications"
        
        with patch("pathlib.Path.home", return_value=tmp_path):
            result = get_default_install_dir()
        
        assert result.exists()
        assert result.is_dir()

    def test_in_home_directory(self, tmp_path: Path):
        """Test that install dir is in home directory."""
        with patch("pathlib.Path.home", return_value=tmp_path):
            result = get_default_install_dir()
        
        assert result == tmp_path / "Applications"
