# AppImg Makefile
# AppImage installer for Linux

VERSION ?= 0.1.2

# Dynamic Python site-packages path detection
# Gets path like /usr/lib/python3.11/site-packages and extracts lib/python3.11/site-packages
PYTHON_SITE_PACKAGES := $(shell python3 -c "import sysconfig; print(sysconfig.get_path('purelib'))" 2>/dev/null | sed 's|^/usr/||')
# Fallback to Debian default if detection fails
ifeq ($(PYTHON_SITE_PACKAGES),)
PYTHON_SITE_PACKAGES = lib/python3/dist-packages
endif

.PHONY: help setup run debug format check test clean clean-all deps install-deps install-desktop uninstall-desktop prepare-pkgdir build-dpkg install-package reinstall-package clean-dpkg install-fpm build-rpm build-all clean-rpm translations clean-translations

# Default target
help:
	@echo "AppImg - AppImage installer"
	@echo ""
	@echo "Available commands:"
	@echo "  make setup          - Install Python dependencies with uv"
	@echo "  make translations   - Compile .po files to .mo files"
	@echo "  make deps           - Install system dependencies (Ubuntu/Debian)"
	@echo "  make run            - Run the application"
	@echo "  make run APP=path   - Run with specific AppImage"
	@echo "  make debug APP=path - Run in debug mode with verbose output"
	@echo "  make list           - List all installed AppImages"
	@echo "  make install-desktop   - Register badgerdrop as default AppImage handler"
	@echo "  make uninstall-desktop - Restore previous default handler"
	@echo "  make test-assets    - Build hello-world test AppImage"
	@echo "  make test-status    - Check Cursor test app status"
	@echo "  make test-install   - Install Cursor AppImage for testing"
	@echo "  make test-run       - Run badgerdrop with Cursor for testing"
	@echo "  make test-uninstall - Uninstall Cursor test app"
	@echo "  make build-dpkg     - Build Debian .deb package"
	@echo "  make install-package - Install built .deb package"
	@echo "  make reinstall-package - Remove and reinstall package"
	@echo "  make clean-dpkg     - Clean package build artifacts"
	@echo "  make format         - Format code with black and ruff"
	@echo "  make check          - Run linting and type checks"
	@echo "  make test           - Run tests"
	@echo "  make clean          - Remove build artifacts"
	@echo "  make clean-translations - Remove compiled .mo files"
	@echo "  make clean-all      - Full cleanup including uv cache and translations"

# Setup Python environment
setup:
	@echo "Installing Python dependencies..."
	uv sync --all-extras
	@echo "Setup complete!"

# Install system dependencies (Ubuntu/Debian)
deps:
	@echo "Installing system dependencies..."
	sudo apt-get update
	sudo apt-get install -y libgirepository1.0-dev libgirepository-2.0-dev libcairo2-dev gobject-introspection gir1.2-gtk-4.0 gir1.2-adw-1
	@echo "System dependencies installed!"

# Install system dependencies (Fedora)
deps-fedora:
	@echo "Installing system dependencies for Fedora..."
	sudo dnf install -y gobject-introspection-devel cairo-gobject-devel gtk4-devel libadwaita-devel
	@echo "System dependencies installed!"

# Install system dependencies (Arch)
deps-arch:
	@echo "Installing system dependencies for Arch..."
	sudo pacman -S gobject-introspection cairo gtk4 libadwaita
	@echo "System dependencies installed!"

# Run the application
run:
	@echo "Starting AppImg..."
	uv run badgerdrop

# Run in debug mode (requires APP=path/to/file)
debug:
ifdef APP
	@echo "Running in debug mode: $(APP)"
	uv run badgerdrop-debug --appimage $(APP)
else
	@echo "Usage: make debug APP=/path/to/app.AppImage"
	@exit 1
endif

# List installed AppImages
list:
	@echo "Listing installed AppImages..."
	uv run badgerdrop-list

# Register badgerdrop as default AppImage handler
install-desktop:
	@echo "Registering badgerdrop as default AppImage handler..."
	python3 scripts/install-desktop.py

# Unregister badgerdrop and restore previous handler
uninstall-desktop:
	@echo "Unregistering badgerdrop as default AppImage handler..."
	python3 scripts/uninstall-desktop.py

# Format code
format:
	@echo "Formatting code..."
	uv run ruff check --fix --unsafe-fixes src/
	@echo "Formatting complete!"

# Run linting and type checks
check:
	@echo "Running checks..."
	uv run ruff check src/
	@echo "Checks complete!"

# Run tests
test:
	@echo "Running tests..."
	uv run pytest tests/ -v || echo "No tests found"

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -rf build/ dist/ *.egg-info .pytest_cache .mypy_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "Clean complete!"

# Full cleanup
clean-all: clean clean-translations
	@echo "Full cleanup..."
	rm -rf .venv
	uv cache clean
	@echo "Full cleanup complete!"

translations:
	@echo "Compiling translations..."
	@for lang in de fr es hu; do \
		mkdir -p po/locale/$$lang/LC_MESSAGES; \
		msgfmt po/$$lang.po -o po/locale/$$lang/LC_MESSAGES/badgerdrop.mo; \
		echo "  ✓ $$lang"; \
	done
	@echo "Translations compiled to po/locale/"

clean-translations:
	@echo "Cleaning compiled translations..."
	@rm -rf po/locale
	@echo "✓ Translations cleaned"

# Reinstall (clean + setup)
reinstall: clean-all setup
	@echo "Reinstall complete!"

# Test install/uninstall with Cursor AppImage
TEST_APP_NAME = Cursor
TEST_APPIMAGE = /home/xcvb/Cursor-2.4.28-x86_64.AppImage
TEST_APPS_DIR = $(HOME)/Applications
TEST_DESKTOP_FILE = $(HOME)/.local/share/applications/Cursor.desktop

test-install:
	@echo "Testing install of $(TEST_APP_NAME)..."
	@if [ ! -f "$(TEST_APPIMAGE)" ]; then \
		echo "Error: $(TEST_APPIMAGE) not found"; \
		echo "Please download Cursor AppImage to $(TEST_APPIMAGE)"; \
		exit 1; \
	fi
	@echo "Installing $(TEST_APP_NAME)..."
	@mkdir -p $(TEST_APPS_DIR)
	@cp "$(TEST_APPIMAGE)" "$(TEST_APPS_DIR)/Cursor-2.4.28-x86_64.AppImage"
	@chmod +x "$(TEST_APPS_DIR)/Cursor-2.4.28-x86_64.AppImage"
	@echo "✓ Installed to $(TEST_APPS_DIR)/Cursor-2.4.28-x86_64.AppImage"
	@echo ""
	@echo "Note: Desktop entry will be created when you drag-and-drop in badgerdrop"
	@echo "Run: make test-run"

test-uninstall:
	@echo "Uninstalling $(TEST_APP_NAME)..."
	@rm -f "$(TEST_APPS_DIR)/Cursor-2.4.28-x86_64.AppImage"
	@rm -f "$(TEST_DESKTOP_FILE)"
	@echo "✓ Removed $(TEST_APPIMAGE)"
	@echo "✓ Removed $(TEST_DESKTOP_FILE)"
	@echo "Updating desktop database..."
	@update-desktop-database $(HOME)/.local/share/applications/ 2>/dev/null || true
	@echo "✓ Uninstall complete!"

	test-run:
	@echo "Running badgerdrop with Cursor test AppImage..."
	@if [ ! -f "$(TEST_APPIMAGE)" ]; then \
		echo "Error: $(TEST_APPIMAGE) not found"; \
		echo "Run: make test-install first"; \
		exit 1; \
	fi
	uv run badgerdrop '$(TEST_APPIMAGE)'

# Build hello-world test AppImage
TEST_ASSETS_DIR = tests/assets/hello-world-appimage
TEST_APPIMAGE_PATH = tests/assets/hello-world-1.0.0-x86_64.AppImage

test-assets:
	@echo "Building hello-world test AppImage..."
	@if [ ! -d "$(TEST_ASSETS_DIR)" ]; then \
		echo "Error: $(TEST_ASSETS_DIR) not found"; \
		exit 1; \
	fi
	@cd $(TEST_ASSETS_DIR) && ./build.sh
	@echo "✓ Test AppImage built: $(TEST_APPIMAGE_PATH)"
	@echo "Use: make test-assets-run"

test-assets-run: test-assets
	@echo "Running badgerdrop with hello-world test AppImage..."
	@if [ ! -f "$(TEST_APPIMAGE_PATH)" ]; then \
		echo "Error: $(TEST_APPIMAGE_PATH) not found"; \
		echo "Run: make test-assets first"; \
		exit 1; \
	fi
	@uv run badgerdrop '$(TEST_APPIMAGE_PATH)'

# Debian package building
DPKG_DIR = debian
BUILD_DIR = $(DPKG_DIR)/badgerdrop
DEB_FILE = ../badgerdrop_0.1.0-1_all.deb

# Common package directory preparation (used by both Debian and RPM builds)
prepare-pkgdir:
	@echo "Preparing package directory..."
	@echo "Python site-packages path: $(PYTHON_SITE_PACKAGES)"
	@echo "Creating package structure..."
	@mkdir -p $(BUILD_DIR)/usr/$(PYTHON_SITE_PACKAGES)
	@mkdir -p $(BUILD_DIR)/usr/bin
	@mkdir -p $(BUILD_DIR)/usr/share/applications
	@mkdir -p $(BUILD_DIR)/usr/share/mime/packages
	@mkdir -p $(BUILD_DIR)/usr/share/pixmaps
	@mkdir -p $(BUILD_DIR)/usr/share/icons/hicolor/scalable/apps
	@echo "Installing Python package..."
	@cp -r src/badgerdrop $(BUILD_DIR)/usr/$(PYTHON_SITE_PACKAGES)/
	@echo "Installing entry points..."
	@echo '#!/bin/sh' > $(BUILD_DIR)/usr/bin/badgerdrop
	@echo '# AppImg main entry point' >> $(BUILD_DIR)/usr/bin/badgerdrop
	@echo 'exec /usr/bin/python3 -m badgerdrop "$$@"' >> $(BUILD_DIR)/usr/bin/badgerdrop
	@echo '#!/bin/sh' > $(BUILD_DIR)/usr/bin/badgerdrop-debug
	@echo '# AppImg debug entry point' >> $(BUILD_DIR)/usr/bin/badgerdrop-debug
	@echo 'exec /usr/bin/python3 -m badgerdrop --debug "$$@"' >> $(BUILD_DIR)/usr/bin/badgerdrop-debug
	@echo '#!/bin/sh' > $(BUILD_DIR)/usr/bin/badgerdrop-list
	@echo '# AppImg list entry point' >> $(BUILD_DIR)/usr/bin/badgerdrop-list
	@echo 'exec /usr/bin/python3 -c "from badgerdrop.install.registry import InstalledAppsManager; import json; apps = InstalledAppsManager().get_all_apps(); print(json.dumps([{\"name\": a.name, \"version\": a.version, \"install_path\": str(a.install_path), \"install_date\": a.install_date} for a in apps], indent=2))"' >> $(BUILD_DIR)/usr/bin/badgerdrop-list
	@echo '#!/bin/sh' > $(BUILD_DIR)/usr/bin/badgerdrop-sound
	@echo '# AppImg sound toggle entry point' >> $(BUILD_DIR)/usr/bin/badgerdrop-sound
	@echo 'exec /usr/bin/python3 -c "from badgerdrop.config.settings import SettingsManager; s = SettingsManager(); s.play_sound_on_install = not s.play_sound_on_install; print(f\"Sound notifications: {\\\"enabled\\\" if s.play_sound_on_install else \\\"disabled\\\"}\")"' >> $(BUILD_DIR)/usr/bin/badgerdrop-sound
	@chmod +x $(BUILD_DIR)/usr/bin/badgerdrop*
	@echo "Installing desktop files..."
	@cp data/dev.badgerdrop.Installer.desktop $(BUILD_DIR)/usr/share/applications/
	@cp data/badgerdrop.mime.xml $(BUILD_DIR)/usr/share/mime/packages/badgerdrop.xml
	@cp data/badgerdrop.svg $(BUILD_DIR)/usr/share/pixmaps/
	@cp data/badgerdrop.svg $(BUILD_DIR)/usr/share/icons/hicolor/scalable/apps/
	@echo "Installing translations..."
	@for lang in de fr es hu; do \
		mkdir -p $(BUILD_DIR)/usr/share/locale/$$lang/LC_MESSAGES; \
		msgfmt po/$$lang.po -o $(BUILD_DIR)/usr/share/locale/$$lang/LC_MESSAGES/badgerdrop.mo; \
	done
	@echo "✓ Package directory prepared"

build-dpkg: prepare-pkgdir
	@echo "Building Debian package..."
	@echo "Installing package control files..."
	@mkdir -p $(BUILD_DIR)/DEBIAN
	@cp debian/control.binary $(BUILD_DIR)/DEBIAN/control
	@cp debian/postinst $(BUILD_DIR)/DEBIAN/
	@cp debian/prerm $(BUILD_DIR)/DEBIAN/
	@chmod +x $(BUILD_DIR)/DEBIAN/postinst $(BUILD_DIR)/DEBIAN/prerm
	@echo "Building .deb package..."
	@dpkg-deb --build $(BUILD_DIR) $(DEB_FILE)
	@echo "✓ Package built: $(DEB_FILE)"
	@echo ""
	@echo "To install: make install-package"

install-package:
	@if [ ! -f $(DEB_FILE) ]; then \
		echo "Error: Package not found. Run: make build-dpkg"; \
		exit 1; \
	fi
	@echo "Installing badgerdrop package..."
	@sudo dpkg -i $(DEB_FILE)
	@echo "✓ Package installed!"
	@echo ""
	@echo "AppImg is now the default handler for .AppImage files"
	@echo "You can now double-click any .AppImage to open it with badgerdrop"

reinstall-package:
	@echo "Reinstalling badgerdrop package..."
	@sudo apt-get remove -y badgerdrop 2>/dev/null || true
	@$(MAKE) build-dpkg
	@$(MAKE) install-package
	@echo "✓ Package reinstalled!"

clean-dpkg:
	@echo "Cleaning dpkg build artifacts..."
	@rm -rf $(BUILD_DIR)/usr
	@rm -f $(DEB_FILE)
	@echo "✓ Clean complete!"

test-status:
	@echo "=== Cursor Test App Status ==="
	@echo ""
	@echo "AppImage file:"
	@if [ -f "$(TEST_APPIMAGE)" ]; then \
		echo "  ✓ $(TEST_APPIMAGE)"; \
	else \
		echo "  ✗ $(TEST_APPIMAGE) (not found)"; \
	fi
	@echo ""
	@echo "Installed application:"
	@if [ -f "$(TEST_APPS_DIR)/Cursor-2.4.28-x86_64.AppImage" ]; then \
		echo "  ✓ $(TEST_APPS_DIR)/Cursor-2.4.28-x86_64.AppImage"; \
	else \
		echo "  ✗ Not installed in $(TEST_APPS_DIR)"; \
	fi
	@echo ""
	@echo "Desktop entry:"
	@if [ -f "$(TEST_DESKTOP_FILE)" ]; then \
		echo "  ✓ $(TEST_DESKTOP_FILE)"; \
		grep "^Exec=" "$(TEST_DESKTOP_FILE)" | head -1; \
	else \
		echo "  ✗ Not found"; \
	fi
	@echo ""
	@echo "To test: make test-install → make test-run → make test-uninstall"

# ============================================
# RPM Package Building (using fpm)
# ============================================

RPM_FILE = ../badgerdrop-$(VERSION)-1.noarch.rpm

install-fpm:  ## Install fpm (Effing Package Management) for RPM building
	@echo "Installing fpm..."
	@echo "Note: fpm requires Ruby and RubyGems"
	@if command -v dnf >/dev/null 2>&1; then \
		echo "Detected Fedora/RHEL system, using dnf..."; \
		sudo dnf install -y ruby ruby-devel rubygems gcc make rpm-build; \
	elif command -v apt-get >/dev/null 2>&1; then \
		echo "Detected Debian/Ubuntu system, using apt-get..."; \
		sudo apt-get update; \
		sudo apt-get install -y ruby ruby-dev rubygems build-essential; \
	elif command -v pacman >/dev/null 2>&1; then \
		echo "Detected Arch system, using pacman..."; \
		sudo pacman -S --needed ruby; \
	else \
		echo "Could not detect package manager. Please install Ruby and RubyGems manually."; \
		exit 1; \
	fi
	@echo "Installing fpm gem..."
	sudo gem install fpm
	@echo "✓ fpm installed successfully"

build-rpm: prepare-pkgdir  ## Build RPM package using fpm
	@echo "Building RPM package..."
	@echo "Source: $(BUILD_DIR)/usr/"
	@echo "Output: $(RPM_FILE)"
	fpm -s dir -t rpm \
		-n badgerdrop \
		-v $(VERSION) \
		--iteration 1 \
		--architecture noarch \
		--description "AppImage installer for Linux" \
		--url "https://github.com/xcvb/badgerdrop" \
		--license "MIT" \
		--vendor "xcvb" \
		--maintainer "xcvb" \
		-d "python3 >= 3.11" \
		-d "python3-pydantic" \
		-d "python3-gobject-base" \
		-d "gtk4" \
		-d "libadwaita" \
		--after-install debian/postinst \
		--before-remove debian/prerm \
		--prefix / \
		-C $(BUILD_DIR) \
		usr/ \
		|| (echo "RPM build failed. Make sure fpm is installed (make install-fpm)" && exit 1)
	@mv badgerdrop-$(VERSION)-1.noarch.rpm $(RPM_FILE) 2>/dev/null || true
	@echo "✓ RPM package built: $(RPM_FILE)"

clean-rpm:  ## Clean RPM build artifacts
	@echo "Cleaning RPM build artifacts..."
	@rm -f $(RPM_FILE)
	@rm -f badgerdrop-$(VERSION)-1.noarch.rpm
	@echo "✓ RPM artifacts cleaned!"

# ============================================
# Build All Packages
# ============================================

build-all: clean build-dpkg build-rpm  ## Build both .deb and .rpm packages
	@echo ""
	@echo "✓ All packages built successfully:"
	@ls -lh $(DEB_FILE) $(RPM_FILE) 2>/dev/null || \
		echo "  Packages location: $(DEB_FILE) and $(RPM_FILE)"
