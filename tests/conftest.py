"""pytest configuration and fixtures for BadgerDrop tests."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def temp_dir(tmp_path: Path) -> Path:
    """Provide a temporary directory for tests."""
    return tmp_path


@pytest.fixture
def temp_config_dir(tmp_path: Path) -> Path:
    """Provide a temporary config directory for settings tests."""
    config_dir = tmp_path / ".config" / "badgerdrop"
    config_dir.mkdir(parents=True)
    return config_dir


@pytest.fixture
def mock_gtk():
    """Mock GTK4/Adwaita imports."""
    with patch.dict("sys.modules", {
        "gi": MagicMock(),
        "gi.repository": MagicMock(),
    }):
        gi_mock = MagicMock()
        gi_mock.require_version = MagicMock()
        
        gtk_mock = MagicMock()
        adw_mock = MagicMock()
        glib_mock = MagicMock()
        
        with patch("builtins.__import__", lambda name, *args, **kwargs: {
            "gi": gi_mock,
            "gi.repository.Gtk": gtk_mock,
            "gi.repository.Adw": adw_mock,
            "gi.repository.GLib": glib_mock,
        }.get(name, MagicMock())):
            yield {
                "gi": gi_mock,
                "Gtk": gtk_mock,
                "Adw": adw_mock,
                "GLib": glib_mock,
            }


@pytest.fixture
def sample_appimage_info():
    """Provide a sample AppImageInfo instance."""
    from badgerdrop.core.models import AppImageInfo
    
    return AppImageInfo(
        name="TestApp",
        exec_cmd="TestApp",
        icon_name="testapp",
        icon_path=Path("/tmp/test/icon.png"),
        categories=["Utility", "Development"],
        comment="A test application",
    )


@pytest.fixture
def sample_installed_app():
    """Provide a sample InstalledApp instance."""
    from badgerdrop.core.models import InstalledApp
    
    return InstalledApp(
        name="TestApp",
        version="1.0.0",
        source_path="/home/user/Downloads/TestApp.AppImage",
        install_path="/home/user/Applications/TestApp-1.0.0.AppImage",
        icon_name="testapp",
        install_date="2024-01-01",
        desktop_file="/home/user/.local/share/applications/testapp.desktop",
    )


@pytest.fixture
def sample_settings():
    """Provide a sample AppSettings instance."""
    from badgerdrop.core.models import AppSettings
    
    return AppSettings(
        play_sound_on_install=True,
        sound_theme="default",
        auto_make_executable=True,
        show_notifications=True,
        install_directory="~/Applications",
    )


@pytest.fixture
def mock_settings_manager(temp_config_dir):
    """Provide a SettingsManager with temporary config directory."""
    from badgerdrop.config.settings import SettingsManager
    
    with patch.object(SettingsManager, "_config_dir", temp_config_dir):
        with patch.object(SettingsManager, "_settings_file", temp_config_dir / "settings.json"):
            manager = SettingsManager()
            yield manager


@pytest.fixture
def mock_registry(temp_config_dir):
    """Provide an InstalledAppRegistry with temporary config directory."""
    from badgerdrop.install.registry import InstalledAppRegistry
    
    registry_file = temp_config_dir / "installed_apps.json"
    
    # Create registry with direct attribute assignment
    registry = object.__new__(InstalledAppRegistry)
    object.__setattr__(registry, "_registry_file", registry_file)
    object.__setattr__(registry, "_apps", [])
    yield registry
