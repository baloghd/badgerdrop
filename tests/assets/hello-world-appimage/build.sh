#!/bin/bash
# Build script for Hello World test AppImage

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_DIR="$SCRIPT_DIR/src"
BUILD_DIR="$SCRIPT_DIR/build"
APPDIR="$BUILD_DIR/AppDir"
OUTPUT_DIR="$SCRIPT_DIR/../.."

# Clean previous build
rm -rf "$BUILD_DIR"
mkdir -p "$APPDIR"

# Copy source files
cp "$SRC_DIR/AppRun" "$APPDIR/"
cp "$SRC_DIR/hello-world.desktop" "$APPDIR/"
cp "$SRC_DIR/hello-world.svg" "$APPDIR/"
cp "$SRC_DIR/hello-world.py" "$APPDIR/"

# Make AppRun executable
chmod +x "$APPDIR/AppRun"

# Download appimagetool if not present
APPIMAGETOOL="$BUILD_DIR/appimagetool-x86_64.AppImage"
if [ ! -f "$APPIMAGETOOL" ]; then
    echo "Downloading appimagetool..."
    wget -q -O "$APPIMAGETOOL" "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"
    chmod +x "$APPIMAGETOOL"
fi

# Build the AppImage
echo "Building Hello World AppImage..."
ARCH=x86_64 "$APPIMAGETOOL" "$APPDIR" "$OUTPUT_DIR/hello-world-test-x86_64.AppImage"

echo "Build complete: $OUTPUT_DIR/hello-world-test-x86_64.AppImage"
