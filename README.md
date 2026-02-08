# AppImg

AppImage installer for Linux. Drag and drop AppImages to install them with proper desktop integration.

## Features

- **Drag-and-drop interface**: Drag AppImage onto the Applications folder
- **Desktop integration**: Automatically creates .desktop entries
- **Icon extraction**: Extracts and installs app icons
- **User-only installation**: Installs to `~/Applications`, no sudo required
- **Debug mode**: Shows detailed extraction and installation logs

## Quick Start

### 1. Install System Dependencies

```bash
# Debian/Ubuntu
sudo apt-get update
sudo apt-get install -y libgirepository1.0-dev libgirepository-2.0-dev libcairo2-dev gobject-introspection gir1.2-gtk-4.0 gir1.2-adw-1

# Fedora
sudo dnf install gobject-introspection-devel cairo-gobject-devel gtk4-devel libadwaita-devel

# Arch Linux
sudo pacman -S gobject-introspection cairo gtk4 libadwaita
```

### 2. Setup Python Environment

```bash
# Clone and enter directory
cd appimgdmg

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
appimg

# With a specific file
appimg /path/to/app.AppImage

# Debug mode (verbose)
appimg-debug --appimage /path/to/app.AppImage
```

Drag and drop any AppImage onto the Applications folder target to install it.

## How It Works

1. **Drag & Drop**: Drop an AppImage onto the installer window
2. **Extraction**: AppImage is extracted to analyze its contents
3. **Metadata**: .desktop file and icon are extracted
4. **Installation**: 
   - AppImage copied to `~/Applications/`
   - Icon installed to `~/.local/share/icons/`
   - .desktop entry created in `~/.local/share/applications/`
   - Desktop database updated

## Project Structure

```
appimgdmg/
├── src/appimg/
│   ├── __init__.py
│   ├── main.py              # GTK app entry point
│   ├── appimage.py          # AppImage parsing
│   ├── installer.py         # Desktop integration
│   └── ui/
│       ├── __init__.py
│       └── window.py        # Main window UI
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
# Run in debug mode (verbose logging)
uv run appimg-debug --appimage /path/to/app.AppImage

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

## License

MIT
