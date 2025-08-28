# infra-uv

A Python utility for checking and installing the `uv` package manager.

## Features

- **UV Installation Check**: Check if `uv` is installed on the system
- **Dry Run Analysis**: See what would happen without making changes
- **Automatic Installation**: Install `uv` if it's not already present
- **Comprehensive Testing**: Full test coverage with pytest
- **Code Quality**: Linting with ruff and code formatting

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd infra-uv

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

```bash
# Install dependencies
just install-dev

# Run tests with coverage
just test

# Run linting
just lint

# Run both tests and linting (CI checks)
just ci

# Check if uv is installed
just check-uv

# Dry run installation analysis
just dry-run-uv

# Install uv if needed
just install-uv

# View coverage report
just coverage-report

# Clean up cache files
just clean
```

### Testing

The project includes comprehensive tests with 100% coverage:

```bash
# Run tests
just test

# Run tests with verbose output
just test-v

# Run tests with coverage
just test-cov
```

### Code Quality

```bash
# Run linting
just lint

# Format code (if using black)
just fmt
```

## CI/CD

The project includes GitHub Actions workflows that run on:

- **Push to main/master**: Runs tests and linting
- **Pull Requests**: Runs tests and linting

### CI Pipeline

1. **Setup**: Python 3.10, 3.11, 3.12, 3.13
2. **Dependencies**: Install with `uv sync --extra dev`
3. **Linting**: Run `ruff check .`
4. **Testing**: Run `pytest` with coverage
5. **Coverage**: Upload to Codecov
6. **Demo**: Run the main script

## Requirements

- Python 3.10+
- uv (for dependency management)

## License

[Add your license here]