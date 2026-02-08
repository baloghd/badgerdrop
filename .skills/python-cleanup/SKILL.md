# python-cleanup

Clean Python code using ruff format, ruff check, and deadcode detection.

## Purpose

Runs a comprehensive cleanup of Python code:
1. **Format**: Auto-format code with ruff format
2. **Lint**: Check for issues with ruff check
3. **Dead Code**: Find unused code with deadcode

## Usage

```bash
# Run cleanup
.skills/python-cleanup/clean.sh

# Or via skill system
python-cleanup
```

## Exit Codes

- **0**: All checks passed, code is clean
- **1**: Issues found (format applied, or lint/deadcode issues remain)

## Loop Usage

Designed to run in a loop until clean:

```bash
while ! .skills/python-cleanup/clean.sh; do
    echo "Issues remain, review and continue..."
    # Agent fixes issues here, then loop continues
    sleep 1
done
echo "Code is clean!"
```

## Tools

- **ruff**: Fast Python linter and formatter
- **deadcode**: Find unused Python code

## Scope

Targets the `src/` directory by default.
