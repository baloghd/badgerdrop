## UI/UX Features
- [x] FEATURE: add settings dialog
- [x] FEATURE: add sound after installation
- [x] FEATURE: make sound notification optional / configurable
- [x] FEATURE: "make executable" should be an option on UI, autoset to true - but user can disable it if they want
- [x] FEATURE: add system notification for successful installation / failure
- [x] FEATURE: add support for multiple languages
- [x] FEATURE: add progress bar for installation process
- [x] FEATURE: add option to choose installation directory
- [x] BUG: if user tries to install an appimage that is already installed, it should prompt them to either overwrite the existing one or cancel the installation, not fail with an error
- [x] BUG: application gets launched immediately after installation, even if the user has not chosen to do so (and we get the application is not responding error)
  - Fixed: `_is_electron_app()` was running the AppImage with subprocess to detect Electron. Now checks for chrome-sandbox file in extracted AppImage instead.
- [x] BUG: we make the file executable even if we don't install it -> only make executable if user chooses to install
- [x] BUG: window title should be "BadgerDrop" instead of "AppImage Installer"
- [x] BUG: different icon from Gnome menu vs on dock
- [x] BUG: investigate 'app does not respond' error on some AppImages (e.g. Obsidian) - may be related to how we detect Electron apps 
- [ ] IMPROVEMENT: UI window default size should be dynamic based on monitor resulution (currently hardcoded to 800x500)


## File/Package Support
- [ ] FEATURE: handle .dkpg / .rpm files
- [ ] FEATURE: add support for installing .flatpak files
- [x] FEATURE: make the app file opener for .appimage files
  - Created data/badgerdrop.mime.xml MIME type definition (handles both application/vnd.appimage and application/x-appimage)
  - Created data/dev.badgerdrop.Installer.desktop with MimeType association
  - postinst script registers badgerdrop as default handler
  - prerm script unregisters on uninstall
  - NOTE: Nautilus (GNOME Files) runs executable files directly instead of opening with default app. This is standard behavior.
    - Web-downloaded AppImages (not executable): Double-click opens with badgerdrop ✓
    - Already executable AppImages: Double-click runs directly (expected - use right-click → "Open With badgerdrop" if needed)

## Packaging & Distribution
- [x] IMPROVEMENT: package up as dpkg
  - Created debian/ packaging directory
  - Built badgerdrop_0.1.0-1_all.deb (44KB)
  - Includes entry points: badgerdrop, badgerdrop-debug, badgerdrop-list, badgerdrop-sound
  - Makefile targets: build-dpkg, install-package, reinstall-package, clean-dpkg
- [x] IMPROVEMENT: package up as rpm
  - Built badgerdrop-0.1.0-1.noarch.rpm (59KB) using fpm
  - Makefile targets: build-rpm, build-all, clean-rpm
  - Package includes all entry points and proper dependencies
- [ ] IMPROVEMENT: add support for more package managers (e.g. apt, yum)
- [ ] IMPROVEMENT: create a PPA for easy installation on Ubuntu-based systems
- [ ] IMPROVEMENT: determine Python version compatibility matrix

## Code Quality & Testing

### Testing
- [ ] IMPROVEMENT: add basic unit test suite
- [ ] IMPROVEMENT: add integration tests for installation process
- [ ] IMPROVEMENT: add tests for edge cases (e.g. installing to non-writable directory, handling invalid AppImages)
- [ ] IMPROVEMENT: add process for creating 'hello world' AppImage for testing purposes

### Architecture & Refactoring - Phase 1: Foundation (Critical)
- [x] REFACTOR: Create constants module - extract magic numbers (margins, icon sizes, timeouts, permissions, defaults) from window.py, installer.py, appimage.py, settings.py
- [x] REFACTOR: Create paths.py module - single source of truth for config/paths (deduplicate installed.py:27 and settings.py:22)
- [x] REFACTOR: Extract CSS styles from window.py:22-116 to ui/styles.css file
- [x] REFACTOR: Fix import consistency - standardize relative imports in UI and gettext usage across codebase

### Architecture & Refactoring - Phase 2: Core Architecture (High Priority)
- [x] REFACTOR: Extract InstallationService from window.py:474-547 - move installation orchestration logic to services layer
- [x] REFACTOR: Decompose installer.py into smaller classes - FileCopier, IconInstaller, DesktopEntryManager
- [x] REFACTOR: Create services/appimage_service.py - extract AppImage parsing from window.py:413-448

### Architecture & Refactoring - Phase 3: Clean Up (Medium Priority)
- [x] REFACTOR: Implement proper logging - replace debug print() patterns with Python logging module
- [x] REFACTOR: Create utils/validators.py - extract directory validation from settings_dialog.py:209-235
- [x] REFACTOR: Create utils/desktop.py - extract file manager integration from window.py:549-575
- [x] REFACTOR: Clean settings_dialog.py - remove commented-out code at lines 46-49

### Architecture & Refactoring - Phase 4: CLI & Dead Code (Lower Priority)
- [x] REFACTOR: Extract CLI commands to cli/commands.py - move CLI entry points from main.py
- [x] REFACTOR: Remove or implement _is_electron_app() dead code in installer.py:176-193

### Bugs & Issues
- [x] IMPROVEMENT: add logging for debugging purposes instead of print statements
- [x] BUG: 'make executable' should only be applied to the installed file if the user does not choose to install
- [ ] BUG: when uninstalling the dpkg, I get:
  ```
  (badgerdrop) ➜ xcvb@t14  ~/badgerdrop git:(main) ✗ sudo apt remove badgerdrop
  Reading package lists... Done
  Building dependency tree... Done
  Reading state information... Done
  The following packages will be REMOVED:
  badgerdrop
  0 upgraded, 0 newly installed, 1 to remove and 12 not upgraded.
  After this operation, 0 B of additional disk space will be used.
  Do you want to continue? [Y/n] y
  (Reading database ... 514681 files and directories currently installed.)
  Removing badgerdrop (0.1.0) ...
  dpkg: warning: while removing badgerdrop, directory '/usr/lib/python3/dist-packages/badgerdrop/ui/__pycache__' not empty so not removed
  dpkg: warning: while removing badgerdrop, directory '/usr/lib/python3/dist-packages/badgerdrop/__pycache__' not empty so not removed
  Processing triggers for gnome-menus (3.36.0-1.1ubuntu3) ...
  Processing triggers for shared-mime-info (2.4-4) ...
  Processing triggers for mailcap (3.70+nmu1ubuntu1) ...
  Processing triggers for desktop-file-utils (0.27-2build1) .
  Processing triggers for mime-support (3.64ubuntu1) ...
  ```
  - This is because the postrm script only removes the main package files, not the __pycache__ directories. This is expected behavior and does not cause any issues.
