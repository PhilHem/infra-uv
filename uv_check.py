import subprocess

UV_INSTALL_COMMAND = "curl -LsSf https://astral.sh/uv/install.sh | sh"


def is_uv_installed() -> bool:
    """Check if uv is installed on the system."""
    try:
        subprocess.run(["uv", "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def install_uv() -> bool:
    """Install uv if it's not already installed. Returns True if successful."""
    if is_uv_installed():
        return True

    try:
        subprocess.run(UV_INSTALL_COMMAND, shell=True, check=True)
        return is_uv_installed()  # Verify installation was successful
    except subprocess.CalledProcessError:
        return False


def main():
    print("Hello from infra-uv!")


if __name__ == "__main__":
    main()
