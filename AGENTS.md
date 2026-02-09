# AGENTS.md - Coding Guidelines for BadgerDrop

This file provides guidance for AI coding agents working on the BadgerDrop codebase.

## Project Overview

BadgerDrop is a GTK4/Adwaita-based AppImage installer for Linux. It provides a drag-and-drop interface for installing AppImage applications.

- **Language**: Python 3.11+
- **GUI**: GTK4 with LibAdwaita
- **Package Manager**: UV
- **Location**: `/home/xcvb/badgerdrop`

## Build/Development Commands

### Setup
```bash
make setup          # Install dependencies with uv sync
make deps           # Install system GTK4/Adwaita deps (Ubuntu)
```

### Run
```bash
make run            # Run the main application
make debug APP=path/to/app.AppImage   # Run debug mode
uv run badgerdrop --appimage path/to/app.AppImage
```

### Lint/Format
```bash
make format         # Format with Black + fix with Ruff
make check          # Lint with Ruff + type check with mypy
```

### Test
```bash
make test           # Run all tests: uv run pytest tests/ -v
uv run pytest tests/test_file.py -v          # Run single test file
uv run pytest tests/test_file.py::test_name -v  # Run single test
uv run pytest -k test_name -v                # Run tests matching pattern
```

## Code Style Guidelines

### Formatting
- **Formatter**: Black
- **Line Length**: 88 characters (Black default)
- **Indent**: 4 spaces
- **Quotes**: Double quotes for strings and docstrings

### Imports
1. `gi.require_version()` calls FIRST (before gi.repository imports)
2. Standard library imports (subprocess, os, pathlib, etc.)
3. `gi.repository` imports (Gtk, Adw, GLib, etc.)
4. Third-party imports (if any beyond GTK)
5. Local package imports (absolute only: `from badgerdrop.module import X`)

### Naming Conventions
- **Classes**: PascalCase (`AppImageParser`, `SettingsManager`)
- **Functions/Methods**: snake_case (`install_appimage`, `_cleanup`)
- **Private**: Leading underscore (`_private_method`)
- **Constants**: UPPER_CASE (`CSS_STYLES`, `INSTALL_DIR`)
- **CSS Classes**: kebab-case (`.drop-area`, `.drag-over`)
- **File Names**: snake_case (`settings_dialog.py`)

### Type Hints
- **REQUIREMENT**: All function parameters and return types MUST have type hints
- **REQUIREMENT**: Do NOT use `typing.Any` - find the proper type instead
- **REQUIREMENT**: Do NOT use `TYPE_CHECKING` blocks - import types directly
- Import from `typing`: `Optional`, `Union`, `list`, `dict`, `Callable` (Python 3.9+)
- For GTK callback signatures, use `Callable[[Arg1, Arg2], ReturnType]`

### Docstrings
- Module-level docstrings required
- Class docstrings explaining purpose
- Function docstrings for public methods

### Architecture Patterns

#### GTK4 Application Structure
```python
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib

class App(Adw.Application):
    def __init__(self):
        super().__init__(application_id="dev.badgerdrop")
```

#### Internationalization
- Use `import gettext` and `_ = gettext.gettext("badgerdrop")`
- Wrap user-visible strings: `_("Install Complete")`

#### Data Models
- Use **Pydantic 2.0** models for all data structures (`AppSettings`, `AppImageInfo`, `InstalledApp`)
- All models in `core/models.py`
- Pydantic provides validation, serialization, and type safety
- Use `list[T]` instead of `field(default_factory=list)` - Pydantic handles defaults

#### Error Handling
- Use try/except with specific exceptions
- Use `GLib.idle_add()` for thread-safe GTK updates
- Log errors before raising or returning

### File Organization
```
src/badgerdrop/
├── core/               # Core domain models and AppImage parsing
│   ├── __init__.py
│   ├── models.py       # Pydantic models (AppImageInfo, InstalledApp, AppSettings)
│   └── appimage.py     # AppImage parsing logic
├── config/             # Configuration and paths
│   ├── __init__.py
│   ├── constants.py    # Application constants
│   ├── paths.py        # Path utilities
│   └── settings.py     # Settings persistence with Pydantic
├── install/            # Installation and registry
│   ├── __init__.py
│   ├── installer.py    # AppImageInstaller
│   └── registry.py     # InstalledAppsManager
├── system/             # System integration
│   ├── __init__.py
│   ├── notifications.py
│   └── sound.py
├── ui/                 # GUI components
│   ├── __init__.py
│   ├── window.py
│   ├── drag_content.py
│   ├── progress_dialog.py
│   └── settings_dialog.py
├── services/           # Business logic services
├── utils/              # Utility modules
├── __init__.py         # Exports and version
├── __main__.py         # Entry point
└── main.py             # Application class
```

### Settings Storage
- Store in `~/.config/badgerdrop/` via `SettingsManager`
- JSON format for persistence
- Use `AppSettings` dataclass with defaults

## Testing

No tests currently exist. When adding tests:
- Create `tests/` directory at project root
- Use pytest
- Mock GTK components for headless testing
- Use `pytest-mock` or unittest.mock for patching

## Dependencies

Key system requirements:
- GTK4 (libgtk-4-dev)
- LibAdwaita (libadwaita-1-dev)
- GObject introspection (gir1.2-adw-1)

Python packages:
- pygobject >= 3.46.0
- pytest (dev)
- black (dev)
- ruff (dev)

## Common Tasks

### Adding a New Dialog
1. Create file in `src/badgerdrop/ui/`
2. Inherit from `Adw.Dialog` or `Gtk.Dialog`
3. Add CSS styles in `window.py` CSS_STYLES if needed
4. Export from `src/badgerdrop/ui/__init__.py`

### Adding CLI Commands
- Add entry point in `pyproject.toml` under `[project.scripts]`
- Create handler function in `main.py`
- Use `argparse` for argument parsing

## Notes

- No Cursor rules or Copilot instructions currently exist
- This is a GUI application - always consider thread safety when updating UI
- AppImages are executed and parsed to extract metadata
- Sound playback requires optional dependencies
- After doing any significant changes, run `make format` and `make check` to ensure code quality
- After doing any significant changes, run `make test` to ensure functionality is intact
- After doing any significant changes, if there are a correspoding TODO in TODO.md, mark it as done
