"""Path utilities and configuration directories"""

from pathlib import Path


def get_config_dir() -> Path:
    """Get the badgerdrop configuration directory (~/.config/badgerdrop)"""
    config_dir = Path.home() / ".config" / "badgerdrop"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_settings_file() -> Path:
    """Get the settings.json file path"""
    return get_config_dir() / "settings.json"


def get_installed_registry_file() -> Path:
    """Get the installed.json registry file path"""
    return get_config_dir() / "installed.json"


def get_local_share_dir() -> Path:
    """Get ~/.local/share directory for desktop integration"""
    return Path.home() / ".local" / "share"


def get_applications_dir() -> Path:
    """Get ~/.local/share/applications for .desktop files"""
    apps_dir = get_local_share_dir() / "applications"
    apps_dir.mkdir(parents=True, exist_ok=True)
    return apps_dir


def get_icons_dir() -> Path:
    """Get ~/.local/share/icons/hicolor for application icons"""
    icons_dir = get_local_share_dir() / "icons" / "hicolor"
    icons_dir.mkdir(parents=True, exist_ok=True)
    return icons_dir


def get_default_install_dir() -> Path:
    """Get the default AppImage installation directory (~/Applications)"""
    install_dir = Path.home() / "Applications"
    install_dir.mkdir(parents=True, exist_ok=True)
    return install_dir
