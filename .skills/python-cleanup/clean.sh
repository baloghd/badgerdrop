#!/bin/bash
# Python code cleanup script
# Runs ruff format, ruff check, and deadcode
# Returns 0 if clean, 1 if issues remain

set -e

echo "=== Python Code Cleanup ==="
echo ""

# Track if any changes/issues remain
EXIT_CODE=0

# 1. Format code with ruff
echo "→ Running ruff format..."
if uv run ruff format src/; then
    echo "  ✓ Format complete"
else
    echo "  ✗ Format failed"
    EXIT_CODE=1
fi
echo ""

# 2. Check for linting issues
echo "→ Running ruff check..."
if uv run ruff check src/; then
    echo "  ✓ No linting issues"
else
    echo "  ✗ Linting issues found"
    EXIT_CODE=1
fi
echo ""

# 3. Check for dead code
echo "→ Running deadcode..."
if uv run deadcode src/; then
    echo "  ✓ No dead code found"
else
    echo "  ✗ Dead code detected"
    EXIT_CODE=1
fi
echo ""

# Summary
echo "=== Cleanup Summary ==="
if [ $EXIT_CODE -eq 0 ]; then
    echo "✓ All checks passed - code is clean!"
else
    echo "✗ Issues remain - review output above"
fi

exit $EXIT_CODE
