"""pytest configuration and fixtures for integration tests."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def temp_install_dir(tmp_path: Path) -> Path:
    """Provide a temporary installation directory."""
    install_dir = tmp_path / "Applications"
    install_dir.mkdir()
    return install_dir


@pytest.fixture
def temp_local_share(tmp_path: Path) -> Path:
    """Provide a temporary .local/share directory structure."""
    local_share = tmp_path / ".local" / "share"
    applications_dir = local_share / "applications"
    icons_dir = local_share / "icons" / "hicolor"
    
    applications_dir.mkdir(parents=True)
    icons_dir.mkdir(parents=True)
    
    return local_share


@pytest.fixture
def mock_installer_components(temp_install_dir, temp_local_share):
    """Create AppImageInstaller with mocked paths."""
    from badgerdrop.install.installer import AppImageInstaller
    
    installer = AppImageInstaller.__new__(AppImageInstaller)
    installer.apps_dir = temp_install_dir
    installer.local_share = temp_local_share
    installer.applications_dir = temp_local_share / "applications"
    installer.icons_dir = temp_local_share / "icons" / "hicolor"
    
    # Initialize utility components
    from badgerdrop.utils import FileCopier, IconInstaller, DesktopManager
    installer._file_copier = FileCopier()
    installer._icon_installer = IconInstaller(installer.icons_dir)
    installer._desktop_manager = DesktopManager(installer.applications_dir)
    
    return installer


@pytest.fixture
def hello_world_appimage():
    """Provide path to hello-world AppImage or skip if not available."""
    appimage_path = Path(__file__).parent.parent / "assets" / "hello-world-test-x86_64.AppImage"
    
    if not appimage_path.exists():
        pytest.skip("hello-world AppImage not available (CI environment)")
    
    return appimage_path


@pytest.fixture
def mock_appimage_info(tmp_path: Path):
    """Create a mock AppImageInfo for testing."""
    from badgerdrop.core.models import AppImageInfo
    
    return AppImageInfo(
        name="TestApp",
        exec_cmd="TestApp",
        icon_name="testapp",
        icon_path=None,
        categories=["Utility"],
        comment="A test application",
        desktop_file_content="[Desktop Entry]\nName=TestApp",
        version="1.0.0",
    )


@pytest.fixture
def mock_progress_callback():
    """Create a mock progress callback that records calls."""
    class CallbackWithCalls:
        def __init__(self):
            self.calls = []
        
        def __call__(self, phase: str, current: int, total: int) -> None:
            self.calls.append({"phase": phase, "current": current, "total": total})
    
    return CallbackWithCalls()
