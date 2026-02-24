<img src="https://github.com/user-attachments/assets/0942d0ef-9241-49ee-be4f-c416f6bfe2af" width="128">  

# BadgerDrop 
A GTK4/Adwaita-based AppImage installer for Linux. Drag and drop AppImages to install them with proper desktop integration.

## Demo
[demo_trimmed.webm](https://github.com/user-attachments/assets/d90f9c8a-c36e-49b3-b942-83e879bb1e00)

## Installation

### Option 1: Download Pre-built Package (Recommended)

Download the latest release for your distribution:

**Debian/Ubuntu:**
```bash
wget https://github.com/baloghd/badgerdrop/releases/latest/download/badgerdrop_0.1.1-1_all.deb
sudo dpkg -i badgerdrop_0.1.1-1_all.deb
```

**Fedora/RHEL:**
```bash
wget https://github.com/baloghd/badgerdrop/releases/latest/download/badgerdrop-0.1.1-1.noarch.rpm
sudo rpm -i badgerdrop-0.1.1-1.noarch.rpm
```

That's it! BadgerDrop is now installed and ready to use.

### Option 2: Build from Source

See the [Development](#development) section below for build instructions.

## Features

- **Drag-and-drop interface**: Modern GTK4 interface with LibAdwaita styling
- **Desktop integration**: Automatically creates .desktop entries
- **Icon extraction**: Extracts and installs app icons
- **User-only installation**: Installs to `~/Applications`, no sudo required
- **Debug mode**: Shows detailed extraction and installation logs
- **Sound notifications**: Optional audio feedback on completion
- **Settings management**: Persistent preferences for installation directory and sound

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

## Development

### Prerequisites

- Python 3.11+
- GTK4
- libadwaita
- gobject-introspection
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

### Setup

```bash
# Clone and enter directory
cd badgerdrop

# Install Python dependencies with uv
make setup
```

### Running

```bash
# Launch GUI
make run

# Debug mode
make debug APP=/path/to/app.AppImage
```

### Project Structure

```
badgerdrop/
├── src/badgerdrop/
│   ├── core/                # Core domain models and AppImage parsing
│   ├── config/              # Configuration and paths
│   ├── install/             # Installation and registry
│   ├── system/              # System integration (notifications, sound)
│   ├── ui/                  # GUI components
│   ├── services/            # Business logic services
│   └── utils/               # Utility modules
├── tests/                   # Test suite (pytest)
├── Makefile
├── pyproject.toml
└── README.md
```

### Development Commands

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

# Run tests
uv run pytest tests/ -v

# Format code
uv run black src/
uv run ruff check --fix src/
```

### Architecture

BadgerDrop uses a layered architecture:

- **Models**: Pydantic-based data models for type safety and validation
- **Services**: Business logic layer handling installation workflows
- **Core**: AppImage parsing and domain logic
- **UI**: GTK4/Adwaita components with CSS styling
- **Utils**: Helper modules for file operations and desktop integration

All code includes type hints and follows the project's coding standards.

## License

MIT
