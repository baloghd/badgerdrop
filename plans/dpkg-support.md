# Plan: Real dpkg Install Support

## Overview
Add support for installing .deb packages alongside AppImages using real dpkg/apt with pkexec for privilege escalation.

---

## Phase 1: Core Infrastructure

### 1. Create `core/package_types.py` - Package Type Enum
```python
from enum import Enum

class PackageType(Enum):
    APPIMAGE = "appimage"
    DEB = "deb"
    # Future: RPM = "rpm", FLATPAK = "flatpak"
```

### 2. Extend `core/models.py` - Unified Package Model
```python
@dataclass
class PackageInfo:
    """Unified package metadata for all supported types"""
    package_type: PackageType
    name: str
    version: Optional[str] = None
    description: Optional[str] = None
    icon_name: Optional[str] = None
    icon_path: Optional[str] = None  # Local extracted path for preview
    categories: list[str] = field(default_factory=list)
    # Type-specific data
    appimage_mount_process: Optional[Any] = None  # Only for AppImage
    appimage_temp_dir: Optional[str] = None       # Only for AppImage
    deb_control_data: Optional[dict] = None       # Only for .deb
```

### 3. Create `core/deb.py` - DebParser
```python
class DebParser:
    """Parse .deb package metadata without installing"""
    
    def __init__(self, deb_path: str):
        self.deb_path = Path(deb_path)
        self.temp_dir: Optional[tempfile.TemporaryDirectory] = None
        self.control_data: Optional[dict] = None
        self.icon_path: Optional[str] = None
    
    def parse(self) -> PackageInfo:
        # Use dpkg-deb -I to get control info
        # Extract control.tar.xz and parse control file
        # Try to extract icon from the deb for preview
        # Return PackageInfo with PackageType.DEB
        
    def _extract_control(self) -> dict:
        # dpkg-deb -f deb_path Package Version Description ...
        # Parse output into dict
        
    def _extract_icon(self) -> Optional[str]:
        # Try common icon paths in the deb
        # Extract to temp dir for preview
```

---

## Phase 2: Privilege Escalation Strategy

### Critical Decision: How to handle root access?

**Option A: pkexec (GUI-friendly) - RECOMMENDED**
```python
subprocess.run(["pkexec", "dpkg", "-i", deb_path], ...)
```
- Shows GUI password dialog
- Clean integration
- Can capture output
- Standard for GUI apps needing root

**Option B: sudo (CLI-friendly)**
```python
subprocess.run(["sudo", "-S", "dpkg", "-i", deb_path], ...)
```
- Requires password handling
- Less GUI-friendly

**Option C: PolicyKit .policy file**
- Create `/usr/share/polkit-1/actions/dev.badgerdrop.install-deb.policy`
- Allows passwordless install for specific users (security risk?)
- **Not recommended** for security

**Decision: Use pkexec**

---

## Phase 3: Service Layer

### 4. Create `services/deb_service.py`
```python
class DebService:
    """Service for .deb package operations"""
    
    def validate_deb(self, file_path: str) -> bool:
        # Check extension .deb
        # Verify it's a valid deb (ar archive with debian-binary)
        
    def parse_deb(self, file_path: str) -> PackageInfo:
        # Use DebParser
        
    def install_deb(
        self,
        deb_path: str,
        progress_callback: Optional[Callable[[int], None]] = None,
        completion_callback: Optional[Callable[[bool, str], None]] = None,
    ) -> None:
        """
        Install .deb using dpkg with pkexec
        
        Since dpkg doesn't have progress callbacks, we'll:
        1. Show indeterminate progress (pulsing bar)
        2. Parse dpkg output for status updates
        3. Report success/failure
        """
        # Run in thread to not block UI
        # Use subprocess with output parsing
        # Handle dependency errors gracefully
        
    def uninstall_deb(self, package_name: str) -> bool:
        """Uninstall using pkexec apt remove"""
```

---

## Phase 4: Installation Service Refactoring

### 5. Refactor `services/installation_service.py`
```python
class InstallationService:
    """Unified installation service for all package types"""
    
    def install(
        self,
        package_info: PackageInfo,
        install_options: InstallOptions,
        callbacks: InstallationCallbacks,
    ) -> None:
        if package_info.package_type == PackageType.APPIMAGE:
            self._install_appimage(package_info, install_options, callbacks)
        elif package_info.package_type == PackageType.DEB:
            self._install_deb(package_info, install_options, callbacks)
            
    def _install_deb(self, ...):
        # Use DebService.install_deb
        # Different progress handling (indeterminate vs determinate)
```

---

## Phase 5: UI Updates

### 6. Update `ui/progress_dialog.py`
```python
class ProgressDialog:
    def set_indeterminate(self, indeterminate: bool):
        """For operations without measurable progress (dpkg)"""
        
    def set_package_type(self, package_type: PackageType):
        """Adjust UI text based on package type"""
        # .deb: "Installing system package..."
        # AppImage: "Copying application..."
```

### 7. Update `ui/window.py`
```python
def load_package(self, file_path: str):
    """Renamed from load_appimage"""
    # Detect package type from extension
    # Route to appropriate parser
    # Update UI elements based on type:
    # - Hide "Make executable" toggle for .deb
    # - Change drop target text
    # - Show package type indicator
```

---

## Phase 6: Registry & Tracking

### 8. Update `install/registry.py`
```python
@dataclass
class InstalledApp:
    package_type: PackageType  # Add this field
    # ... existing fields ...
    
    def uninstall(self):
        """Type-specific uninstall logic"""
        if self.package_type == PackageType.DEB:
            # Use apt remove with pkexec
        else:
            # Use existing AppImage uninstall
```

---

## Phase 7: MIME Types & Packaging

### 9. Update `data/badgerdrop.mime.xml`
```xml
<mime-type type="application/vnd.debian.binary-package">
  <comment>Debian package</comment>
  <glob pattern="*.deb"/>
</mime-type>
```

### 10. Update `data/dev.badgerdrop.Installer.desktop`
```
MimeType=application/vnd.appimage;application/x-appimage;application/vnd.debian.binary-package;
```

### 11. Update Debian Package
- No new dependencies (dpkg is already present)
- Add polkit policy if we want custom auth rules (optional)

---

## Phase 8: Testing Strategy

### 12. Create Test Assets
- `tests/assets/fake-package.deb` - Small test .deb
- Integration tests for DebParser
- Mock tests for dpkg interactions

---

## Implementation Order

Recommended sequence:

1. **Core models** - Add PackageType enum, update PackageInfo
2. **DebParser** - Can test standalone
3. **DebService.validate_deb** - Simple validation
4. **UI detection** - Detect .deb and show "not yet supported" message
5. **DebService.install_deb** - Core functionality with pkexec
6. **InstallationService integration** - Wire it all together
7. **UI polish** - Progress dialogs, messaging
8. **Registry updates** - Track .deb installs
9. **MIME types** - Register as handler

---

## Key Design Decisions

### Real dpkg install simplifies the installation flow:
- Desktop file installation handled by .deb (to system `/usr/share/applications/`)
- Icon installation handled by .deb (to system icon themes)
- File placement handled by .deb (to system directories)
- BadgerDrop just orchestrates the install and tracks it

### Progress Indication:
Since dpkg doesn't have percentage progress, options:
- Show indeterminate progress (pulsing bar)
- Parse dpkg output for stages: "Preparing...", "Installing...", "Configuring..."

### Dependency Handling:
If .deb has unmet dependencies, dpkg will fail. Options:
- Try `apt install -f` afterward automatically?
- Show error and let user run `apt --fix-broken install` manually?

### Uninstall Tracking:
For .deb, track the package name (from control file) not the file path, since `apt remove` needs the package name.

---

## Open Questions

1. **Progress indication**: Indeterminate pulsing bar or parse dpkg output for stages?
2. **Dependency handling**: Auto-fix with `apt install -f` or manual error?
3. **Should we create a PolicyKit policy** for custom authentication rules?

---

*Created: 2026-02-09*
*Status: Planned - Implementation pending*
