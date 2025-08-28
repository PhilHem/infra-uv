# infra-uv

A Python utility for checking and installing the `uv` package manager.

## Features

- **UV Installation Check**: Check if `uv` is installed on the system
- **Dry Run Analysis**: See what would happen without making changes
- **Automatic Installation**: Install `uv` if it's not already present
- **Comprehensive Testing**: Full test coverage with pytest
- **Code Quality**: Linting with ruff and code formatting

## Requirements

- uv (for dependency management and Python version handling)

## Installation

```bash
# Option 1: Clone the repository
git clone <repository-url>
cd infra-uv

# Option 2: Add as git subtree (for tracking updates)
git subtree add --prefix=infra-uv <repository-url> main --squash

# Option 3: Add as git submodule (for tracking updates)
git submodule add <repository-url> infra-uv

# Install dependencies
uv sync --extra dev
```

## Usage

### Command Line

```bash
# Run the main script to check UV status
uv run python uv_check.py

# Or use the justfile commands
just run
```

### Programmatic Usage

```python
from uv_check import is_uv_installed, install_uv, dry_run_install_uv

# Check if uv is installed
if is_uv_installed():
    print("UV is available")

# Get installation analysis without installing
result = dry_run_install_uv()
print(result["message"])

# Install uv if needed
if install_uv():
    print("UV installed successfully")
```

## Development

### Available Commands

| Command | Description |
|---------|-------------|
| `just install-dev` | Install development dependencies |
| `just test` | Run tests with coverage |
| `just lint` | Run linting |
| `just ci` | Run both tests and linting (CI checks) |
| `just check-uv` | Check if uv is installed |
| `just dry-run-uv` | Dry run installation analysis |
| `just install-uv` | Install uv if needed |
| `just coverage-report` | View coverage report |
| `just clean` | Clean up cache files |