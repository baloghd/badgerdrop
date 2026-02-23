#!/bin/bash
# Script to test CI build locally using Docker

set -e

echo "Building Docker image for CI testing..."
docker build -f Dockerfile.ci -t badgerdrop-ci-test .

echo ""
echo "Running tests in Docker container..."
docker run --rm badgerdrop-ci-test
