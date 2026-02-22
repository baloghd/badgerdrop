"""Unit tests for registry module."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from badgerdrop.core.models import InstalledApp
from badgerdrop.config.paths import get_config_dir, get_installed_registry_file
from badgerdrop.install.registry import InstalledAppRegistry


class TestInstalledAppRegistry:
    """Tests for InstalledAppRegistry class."""

    @pytest.fixture
    def temp_registry(self, tmp_path: Path):
        """Create a registry with a temporary file."""
        registry_file = tmp_path / "installed.json"
        
        with patch("badgerdrop.config.paths.get_config_dir", return_value=tmp_path):
            with patch("badgerdrop.config.paths.get_installed_registry_file", return_value=registry_file):
                registry = InstalledAppRegistry()
                return registry

    def test_add_app(self, temp_registry):
        """Test adding an app to the registry."""
        app = InstalledApp(
            name="TestApp",
            version="1.0.0",
            source_path="/home/user/Downloads/TestApp.AppImage",
            install_path="/home/user/Applications/TestApp.AppImage",
            icon_name="testapp",
            install_date="2024-01-01",
        )
        
        temp_registry.add(app)
        
        assert len(temp_registry.apps) == 1
        assert temp_registry.apps[0].name == "TestApp"
        assert temp_registry.apps[0].version == "1.0.0"

    def test_add_multiple_apps(self, temp_registry):
        """Test adding multiple apps to the registry."""
        app1 = InstalledApp(
            name="App1",
            version="1.0.0",
            source_path="/src1",
            install_path="/dst1/App1.AppImage",
            icon_name="app1",
            install_date="2024-01-01",
        )
        app2 = InstalledApp(
            name="App2",
            version="2.0.0",
            source_path="/src2",
            install_path="/dst2/App2.AppImage",
            icon_name="app2",
            install_date="2024-02-01",
        )
        
        temp_registry.add(app1)
        temp_registry.add(app2)
        
        assert len(temp_registry.apps) == 2

    def test_add_replaces_existing_same_path(self, temp_registry):
        """Test that adding app with same install_path replaces old entry."""
        app1 = InstalledApp(
            name="OldApp",
            version="1.0.0",
            source_path="/src",
            install_path="/dst/App.AppImage",  # Same path
            icon_name="oldapp",
            install_date="2024-01-01",
        )
        app2 = InstalledApp(
            name="NewApp",
            version="2.0.0",
            source_path="/src",
            install_path="/dst/App.AppImage",  # Same path
            icon_name="newapp",
            install_date="2024-02-01",
        )
        
        temp_registry.add(app1)
        temp_registry.add(app2)
        
        assert len(temp_registry.apps) == 1
        assert temp_registry.apps[0].name == "NewApp"

    def test_remove_app(self, temp_registry):
        """Test removing an app from the registry by install_path."""
        app = InstalledApp(
            name="TestApp",
            version="1.0.0",
            source_path="/home/user/Downloads/TestApp.AppImage",
            install_path="/home/user/Applications/TestApp.AppImage",
            icon_name="testapp",
            install_date="2024-01-01",
        )
        
        temp_registry.add(app)
        assert len(temp_registry.apps) == 1
        
        temp_registry.remove("/home/user/Applications/TestApp.AppImage")
        
        assert len(temp_registry.apps) == 0

    def test_get_all_sorted_by_date(self, temp_registry):
        """Test getting all apps sorted by install date (newest first)."""
        app1 = InstalledApp(
            name="App1",
            version="1.0.0",
            source_path="/src1",
            install_path="/dst1",
            icon_name="app1",
            install_date="2024-01-01",
        )
        app2 = InstalledApp(
            name="App2",
            version="2.0.0",
            source_path="/src2",
            install_path="/dst2",
            icon_name="app2",
            install_date="2024-03-01",
        )
        app3 = InstalledApp(
            name="App3",
            version="3.0.0",
            source_path="/src3",
            install_path="/dst3",
            icon_name="app3",
            install_date="2024-02-01",
        )
        
        temp_registry.add(app1)
        temp_registry.add(app2)
        temp_registry.add(app3)
        
        all_apps = temp_registry.get_all()
        
        assert len(all_apps) == 3
        assert all_apps[0].name == "App2"  # 2024-03-01
        assert all_apps[1].name == "App3"  # 2024-02-01
        assert all_apps[2].name == "App1"  # 2024-01-01

    def test_get_all_empty(self, temp_registry):
        """Test getting all apps when registry is empty."""
        all_apps = temp_registry.get_all()
        
        assert all_apps == []

    def test_get_by_name_case_insensitive(self, temp_registry):
        """Test getting an app by name (case insensitive)."""
        app = InstalledApp(
            name="TestApp",
            version="1.0.0",
            source_path="/src",
            install_path="/dst",
            icon_name="testapp",
            install_date="2024-01-01",
        )
        
        temp_registry.add(app)
        
        found = temp_registry.get_by_name("testapp")  # lowercase
        assert found is not None
        assert found.name == "TestApp"
        
        found2 = temp_registry.get_by_name("TESTAPP")  # uppercase
        assert found2 is not None
        assert found2.name == "TestApp"

    def test_get_by_name_not_found(self, temp_registry):
        """Test getting an app by name when not found."""
        found = temp_registry.get_by_name("NonExistent")
        
        assert found is None

    def test_is_installed_case_insensitive(self, temp_registry):
        """Test checking if an app is installed (case insensitive)."""
        app = InstalledApp(
            name="TestApp",
            version="1.0.0",
            source_path="/src",
            install_path="/dst",
            icon_name="testapp",
            install_date="2024-01-01",
        )
        
        temp_registry.add(app)
        
        assert temp_registry.is_installed("TestApp") is True
        assert temp_registry.is_installed("testapp") is True
        assert temp_registry.is_installed("TESTAPP") is True
        assert temp_registry.is_installed("NonExistent") is False

    def test_get_by_filename(self, temp_registry):
        """Test getting an app by its filename."""
        app = InstalledApp(
            name="TestApp",
            version="1.0.0",
            source_path="/home/user/Downloads/TestApp.AppImage",
            install_path="/home/user/Applications/TestApp-1.0.0.AppImage",
            icon_name="testapp",
            install_date="2024-01-01",
        )
        
        temp_registry.add(app)
        
        found = temp_registry.get_by_filename("TestApp-1.0.0.AppImage")
        
        assert found is not None
        assert found.name == "TestApp"

    def test_get_by_filename_not_found(self, temp_registry):
        """Test getting an app by filename when not found."""
        found = temp_registry.get_by_filename("NonExistent.AppImage")
        
        assert found is None

    def test_persistence(self, tmp_path: Path):
        """Test that registry persists to file."""
        registry_file = tmp_path / "installed.json"
        
        # Create and populate first registry
        with patch("badgerdrop.config.paths.get_config_dir", return_value=tmp_path):
            with patch("badgerdrop.config.paths.get_installed_registry_file", return_value=registry_file):
                registry1 = InstalledAppRegistry()
                
                app = InstalledApp(
                    name="TestApp",
                    version="1.0.0",
                    source_path="/src",
                    install_path="/dst",
                    icon_name="testapp",
                    install_date="2024-01-01",
                )
                registry1.add(app)
        
        # Verify file was created
        assert registry_file.exists()
        
        # Load with second registry
        with patch("badgerdrop.config.paths.get_config_dir", return_value=tmp_path):
            with patch("badgerdrop.config.paths.get_installed_registry_file", return_value=registry_file):
                registry2 = InstalledAppRegistry()
                
                assert len(registry2.apps) == 1
                assert registry2.apps[0].name == "TestApp"

    def test_load_invalid_json(self, tmp_path: Path):
        """Test loading when registry file contains invalid JSON."""
        registry_file = tmp_path / "installed.json"
        registry_file.write_text("not valid json {{")
        
        with patch("badgerdrop.config.paths.get_config_dir", return_value=tmp_path):
            with patch("badgerdrop.config.paths.get_installed_registry_file", return_value=registry_file):
                registry = InstalledAppRegistry()
                
                # Should handle gracefully and set empty list
                assert registry.apps == []

    def test_load_missing_apps_key(self, tmp_path: Path):
        """Test loading when registry file has missing 'apps' key."""
        registry_file = tmp_path / "installed.json"
        registry_file.write_text(json.dumps({"other_key": "value"}))
        
        with patch("badgerdrop.config.paths.get_config_dir", return_value=tmp_path):
            with patch("badgerdrop.config.paths.get_installed_registry_file", return_value=registry_file):
                registry = InstalledAppRegistry()
                
                assert registry.apps == []
