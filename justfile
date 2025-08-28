# Justfile for infra-uv project

# Default recipe to show available commands
default:
    @just --list

# Install dependencies
install:
    uv sync

# Install development dependencies
install-dev:
    uv sync --extra dev

# Run tests with coverage
test:
    uv run pytest

# Run tests with verbose output
test-v:
    uv run pytest -v

# Run tests with coverage (redundant now since test includes coverage)
test-cov:
    uv run pytest --cov=uv_check

# Open coverage report in browser
coverage-report:
    open htmlcov/index.html

# Run the main script
run:
    uv run python uv_check.py

# Check if uv is installed (using our function)
check-uv:
    uv run python -c "from uv_check import is_uv_installed; print('UV installed:', is_uv_installed())"

# Install uv if not already installed
install-uv:
    uv run python -c "from uv_check import install_uv; print('UV install result:', install_uv())"

# Dry run to check if uv needs installation
dry-run-uv:
    uv run python -c "from uv_check import dry_run_install_uv; import json; result = dry_run_install_uv(); print(json.dumps(result, indent=2))"

# Check if git is up to date
check-git:
    uv run python -c "from uv_check import ensure_git_up_to_date; ensure_git_up_to_date()"

# Format code
fmt:
    uv run black .

# Lint code
lint:
    uv run ruff check .

# Type check
type-check:
    uv run mypy uv_check.py

# Clean up cache files
clean:
    rm -rf .pytest_cache
    rm -rf .mypy_cache
    rm -rf __pycache__
    rm -rf tests/__pycache__
    find . -name "*.pyc" -delete

# Run CI checks locally (lint + test)
ci:
    just lint
    just test
