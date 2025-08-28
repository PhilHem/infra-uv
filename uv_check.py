import subprocess
import sys

UV_INSTALL_COMMAND = "curl -LsSf https://astral.sh/uv/install.sh | sh"


def check_git_up_to_date() -> bool:
    """Check if the current git representation is up to date.

    Returns:
        bool: True if up to date, False otherwise
    """
    try:
        # Check if we're in a git repository
        subprocess.run(["git", "rev-parse", "--git-dir"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Not in a git repository, consider it up to date
        return True

    try:
        # Fetch latest changes from remote
        subprocess.run(["git", "fetch"], capture_output=True, check=True)

        # Get current branch
        current_branch = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True, check=True
        ).stdout.strip()

        # Compare local with remote
        local_commit = subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
        ).stdout.strip()

        remote_commit = subprocess.run(
            ["git", "rev-parse", f"origin/{current_branch}"], capture_output=True, text=True, check=True
        ).stdout.strip()

        return local_commit == remote_commit

    except subprocess.CalledProcessError:
        # If any git command fails, assume it's up to date
        return True


def ensure_git_up_to_date():
    """Check if git is up to date and exit with error if not."""
    if not check_git_up_to_date():
        print("❌ Error: Current git representation is not up to date.")
        print("Please update your repository with:")
        print("  git pull origin main")
        sys.exit(1)


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
            "message": "uv is not installed and would be installed using: " + UV_INSTALL_COMMAND,
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

    # Check if git is up to date
    print("1. Checking if git is up to date...")
    ensure_git_up_to_date()
    print("   ✅ Git is up to date")

    # Check if uv is installed
    print("\n2. Checking if uv is installed...")
    if is_uv_installed():
        print("   ✅ uv is installed and available")
    else:
        print("   ❌ uv is not installed")

    print("\n3. Dry run analysis...")
    dry_run_result = dry_run_install_uv()
    print(f"   {dry_run_result['message']}")

    print("\n4. Installation status...")
    if dry_run_result["needs_install"]:
        print("   Would install uv using the official installer")
        print(f"   Command: {UV_INSTALL_COMMAND}")
    else:
        print("   No installation needed - uv is ready to use")

    print("\n=== Summary ===")
    print(f"UV Status: {'Installed' if is_uv_installed() else 'Not Installed'}")
    print(f"Action Required: {'Install' if dry_run_result['needs_install'] else 'None'}")


if __name__ == "__main__":
    main()
