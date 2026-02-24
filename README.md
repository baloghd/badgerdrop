# BadgerDrop

A GTK4/Adwaita-based AppImage installer for Linux. Drag and drop AppImages to install them with proper desktop integration.

## Demo
[demo_trimmed.webm](https://github.com/user-attachments/assets/d90f9c8a-c36e-49b3-b942-83e879bb1e00)

## Features

- **Drag-and-drop interface**: Modern GTK4 interface with LibAdwaita styling
- **Desktop integration**: Automatically creates .desktop entries
- **Icon extraction**: Extracts and installs app icons
- **User-only installation**: Installs to `~/Applications`, no sudo required
- **Debug mode**: Shows detailed extraction and installation logs
- **Sound notifications**: Optional audio feedback on completion
- **Settings management**: Persistent preferences for installation directory and sound

## Quick Start

### 1. Install System Dependencies

```bash
# Debian/Ubuntu
sudo apt-get update
sudo apt-get install -y libgirepository1.0-dev libgirepository-2.0-dev libcairo2-dev gobject-introspection gir1.2-gtk-4.0 gir1.2-adw-1

# Fedora
sudo dnf install gobject-introspection-devel cairo-gobject-devel gtk4-devel libadwaita-devel
```

### 2. Setup Python Environment

```bash
# Clone and enter directory
cd badgerdrop

# Install Python dependencies with uv
make setup

# Or manually:
# uv sync --all-extras
```

### 3. Run

```bash
# Launch GUI
make run

# Or in debug mode
make debug APP=/path/to/app.AppImage
```

## Usage

```bash
# Launch GUI
badgerdrop

# With a specific file
badgerdrop /path/to/app.AppImage

# Debug mode (verbose)
badgerdrop-debug --appimage /path/to/app.AppImage
```

Drag and drop any AppImage onto the Applications folder target to install it.

## How It Works

1. **Drag & Drop**: Drop an AppImage onto the installer window
2. **Extraction**: AppImage is extracted to analyze its contents
3. **Metadata**: .desktop file and icon are extracted using Pydantic models
4. **Installation**:
   - AppImage copied to `~/Applications/`
   - Icon installed to `~/.local/share/icons/`
   - .desktop entry created in `~/.local/share/applications/`
   - Desktop database updated

## Project Structure

```
badgerdrop/
├── src/badgerdrop/
│   ├── __init__.py          # Package exports and version
│   ├── __main__.py          # Entry point
│   ├── main.py              # GTK4/Adwaita application class
│   ├── core/                # Core domain models and AppImage parsing
│   │   ├── models.py        # Pydantic models (AppImageInfo, InstalledApp, AppSettings)
│   │   └── appimage.py      # AppImage parsing logic
│   ├── config/              # Configuration and paths
│   │   ├── constants.py     # Application constants
│   │   ├── paths.py         # Path utilities
│   │   └── settings.py      # Settings persistence
│   ├── install/             # Installation and registry
│   │   ├── installer.py     # AppImageInstaller
│   │   └── registry.py      # InstalledAppsManager
│   ├── system/              # System integration
│   │   ├── notifications.py # Desktop notifications
│   │   └── sound.py         # Audio playback
│   ├── ui/                  # GUI components
│   │   ├── window.py        # Main window UI
│   │   ├── drag_content.py  # Drag and drop handling
│   │   ├── progress_dialog.py
│   │   ├── settings_dialog.py
│   │   └── helpers.py
│   ├── services/            # Business logic services
│   │   ├── installation_service.py
│   │   ├── appimage_service.py
│   │   └── errors.py
│   └── utils/               # Utility modules
│       ├── file_copier.py
│       ├── desktop.py
│       ├── desktop_manager.py
│       ├── icon_installer.py
│       ├── validators.py
│       └── logging_config.py
├── tests/                   # Test suite (pytest)
│   ├── unit/
│   ├── integration/
│   └── edge_cases/
├── Makefile
├── pyproject.toml
└── README.md
```

## Development

Use the provided Makefile for common tasks:

```bash
# Setup environment
make setup              # Install Python deps

# Run the app
make run               # Run with default settings
make debug APP=/path   # Run in debug mode

# Development
make format            # Format code with black and ruff
make check             # Run linting checks
make test              # Run tests

# Cleanup
make clean             # Remove build artifacts
make clean-all         # Full cleanup including venv
```

Or use `uv` directly:

```bash
# Run the application
uv run badgerdrop

# Run in debug mode (verbose logging)
uv run badgerdrop-debug --appimage /path/to/app.AppImage

# Run tests
uv run pytest tests/ -v

# Format code
uv run black src/
uv run ruff check --fix src/

# Type checking
uv run mypy src/
```

## Requirements

- Python 3.11+
- GTK4
- libadwaita
- gobject-introspection
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

## Architecture

BadgerDrop uses a layered architecture:

- **Models**: Pydantic-based data models for type safety and validation
- **Services**: Business logic layer handling installation workflows
- **Core**: AppImage parsing and domain logic
- **UI**: GTK4/Adwaita components with CSS styling
- **Utils**: Helper modules for file operations and desktop integration

All code includes type hints and follows the project's coding standards.

## License

MIT
