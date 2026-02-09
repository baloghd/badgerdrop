# Hello World Test AppImage

A minimal GTK4 application packaged as an AppImage for testing BadgerDrop functionality.

## Building

Run the build script:

```bash
./build.sh
```

This will create `hello-world-test-x86_64.AppImage` in the `tests/assets/` directory.

## Requirements

- appimagetool (will be downloaded automatically if not present)
- Python 3 with GTK4 bindings (PyGObject)

## Usage

After building, you can use this AppImage to test BadgerDrop:

```bash
# Run directly
./tests/assets/hello-world-test-x86_64.AppImage

# Or use with BadgerDrop
badgerdrop ./tests/assets/hello-world-test-x86_64.AppImage
```

## Features

- Simple GTK4 window with "Hello World!" message
- Application icon
- Desktop entry with proper metadata
- Minimal size (~10-15 MB depending on bundled dependencies)
