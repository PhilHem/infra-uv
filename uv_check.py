import subprocess

UV_INSTALL_COMMAND = "curl -LsSf https://astral.sh/uv/install.sh | sh"


def is_uv_installed() -> bool:
    """Check if uv is installed on the system."""
    try:
        subprocess.run(["uv", "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def dry_run_install_uv() -> dict:
    """Check if uv needs to be installed without actually installing it.

    Returns:
        dict: Contains 'needs_install' (bool) and 'message' (str)
    """
    if is_uv_installed():
        return {"needs_install": False, "message": "uv is already installed"}
    else:
        return {
            "needs_install": True,
            "message": "uv is not installed and would be installed using: "
            + UV_INSTALL_COMMAND,
        }


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
    """Main function that demonstrates the uv_check functionality."""
    print("=== UV Installation Checker ===\n")

    # Check if uv is installed
    print("1. Checking if uv is installed...")
    if is_uv_installed():
        print("   ✅ uv is installed and available")
    else:
        print("   ❌ uv is not installed")

    print("\n2. Dry run analysis...")
    dry_run_result = dry_run_install_uv()
    print(f"   {dry_run_result['message']}")

    print("\n3. Installation status...")
    if dry_run_result["needs_install"]:
        print("   Would install uv using the official installer")
        print(f"   Command: {UV_INSTALL_COMMAND}")
    else:
        print("   No installation needed - uv is ready to use")

    print("\n=== Summary ===")
    print(f"UV Status: {'Installed' if is_uv_installed() else 'Not Installed'}")
    print(
        f"Action Required: {'Install' if dry_run_result['needs_install'] else 'None'}"
    )


if __name__ == "__main__":
    main()
