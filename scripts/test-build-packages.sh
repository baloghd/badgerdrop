#!/bin/bash
# Test build-packages job locally

set -e

echo "Testing build-packages job locally..."
echo "======================================"

# Build the image
docker build -f Dockerfile.ci -t badgerdrop-build-test .

# Run the package build
docker run --rm badgerdrop-build-test bash -c "
    echo 'Installing Python dependencies...'
    uv sync --all-extras
    
    echo ''
    echo 'Building Debian package...'
    make build-dpkg
    
    echo ''
    echo 'Package built successfully!'
    ls -la debian/*.deb
"
