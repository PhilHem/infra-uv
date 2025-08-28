import os
import subprocess
import sys
from unittest.mock import patch

# Add the parent directory to the path so we can import uv_check
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from uv_check import check_git_up_to_date, dry_run_install_uv, ensure_git_up_to_date, install_uv, is_uv_installed, main


def test_is_uv_installed_when_available():
    """Test that is_uv_installed returns True when uv is available."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        assert is_uv_installed() is True
        mock_run.assert_called_once_with(["uv", "--version"], capture_output=True, check=True)


def test_is_uv_installed_when_not_available():
    """Test that is_uv_installed returns False when uv is not available."""
    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = FileNotFoundError()
        assert is_uv_installed() is False


def test_is_uv_installed_when_command_fails():
    """Test that is_uv_installed returns False when uv command fails."""
    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = subprocess.CalledProcessError(1, "uv --version")
        assert is_uv_installed() is False


def test_dry_run_install_uv_when_already_installed():
    """Test that dry_run_install_uv returns correct info when uv is already installed."""
    with patch("uv_check.is_uv_installed") as mock_check:
        mock_check.return_value = True
        result = dry_run_install_uv()

        assert result["needs_install"] is False
        assert result["message"] == "uv is already installed"
        mock_check.assert_called_once()


def test_dry_run_install_uv_when_not_installed():
    """Test that dry_run_install_uv returns correct info when uv is not installed."""
    with patch("uv_check.is_uv_installed") as mock_check:
        mock_check.return_value = False
        result = dry_run_install_uv()

        assert result["needs_install"] is True
        assert "uv is not installed and would be installed using:" in result["message"]
        assert "curl -LsSf https://astral.sh/uv/install.sh | sh" in result["message"]
        mock_check.assert_called_once()


def test_install_uv_when_already_installed():
    """Test that install_uv returns True when uv is already installed."""
    with patch("uv_check.is_uv_installed") as mock_check:
        mock_check.return_value = True
        assert install_uv() is True
        mock_check.assert_called_once()


def test_install_uv_when_not_installed_success():
    """Test that install_uv installs uv successfully when not installed."""
    with (
        patch("uv_check.is_uv_installed") as mock_check,
        patch("subprocess.run") as mock_run,
    ):
        # First call returns False (not installed), second call returns True (installed)
        mock_check.side_effect = [False, True]
        mock_run.return_value.returncode = 0

        assert install_uv() is True
        assert mock_check.call_count == 2
        mock_run.assert_called_once()


def test_install_uv_when_installation_fails():
    """Test that install_uv returns False when installation fails."""
    with (
        patch("uv_check.is_uv_installed") as mock_check,
        patch("subprocess.run") as mock_run,
    ):
        mock_check.return_value = False
        mock_run.side_effect = subprocess.CalledProcessError(1, "install command")

        assert install_uv() is False
        mock_check.assert_called_once()
        mock_run.assert_called_once()


def test_main():
    """Test the main function."""
    with (
        patch("uv_check.is_uv_installed") as mock_check,
        patch("uv_check.dry_run_install_uv") as mock_dry_run,
        patch("builtins.print") as mock_print,
    ):
        mock_check.return_value = True
        mock_dry_run.return_value = {
            "needs_install": False,
            "message": "uv is already installed",
        }

        main()

        # Verify the functions were called
        mock_check.assert_called()
        mock_dry_run.assert_called_once()

        # Verify print was called multiple times (for the formatted output)
        assert mock_print.call_count > 1


def test_main_when_uv_not_installed():
    """Test the main function when uv is not installed."""
    with (
        patch("uv_check.is_uv_installed") as mock_check,
        patch("uv_check.dry_run_install_uv") as mock_dry_run,
        patch("builtins.print") as mock_print,
    ):
        mock_check.return_value = False
        mock_dry_run.return_value = {
            "needs_install": True,
            "message": (
                "uv is not installed and would be installed using: curl -LsSf https://astral.sh/uv/install.sh | sh"
            ),
        }

        main()

        # Verify the functions were called
        mock_check.assert_called()
        mock_dry_run.assert_called_once()

        # Verify print was called multiple times (for the formatted output)
        assert mock_print.call_count > 1


def test_ensure_git_up_to_date_prints_error_message():
    """Test that ensure_git_up_to_date prints error messages when git is not up to date."""
    with patch("subprocess.run") as mock_run, patch("sys.exit") as mock_exit, patch("builtins.print") as mock_print:
        # Mock git commands to simulate not up to date scenario
        mock_run.side_effect = [
            type("obj", (object,), {"returncode": 0})(),  # git rev-parse --git-dir (success)
            type("obj", (object,), {"returncode": 0})(),  # git fetch (success)
            type("obj", (object,), {"returncode": 0, "stdout": "main\n"}),  # git rev-parse --abbrev-ref HEAD (success)
            type("obj", (object,), {"returncode": 0, "stdout": "abc123\n"}),  # git rev-parse HEAD (success)
            type(
                "obj", (object,), {"returncode": 0, "stdout": "def456\n"}
            ),  # git rev-parse origin/main (different commit)
        ]

        ensure_git_up_to_date()

        # Verify error messages were printed
        mock_print.assert_any_call("❌ Error: Current git representation is not up to date.")
        mock_print.assert_any_call("Please update your repository with:")
        mock_print.assert_any_call("  git pull origin main")
        mock_exit.assert_called_once_with(1)


def test_check_git_up_to_date_when_git_rev_parse_fails():
    """Test that check_git_up_to_date returns True when git rev-parse --git-dir fails."""
    with patch("subprocess.run") as mock_run:
        # Mock git rev-parse --git-dir to fail with CalledProcessError
        mock_run.side_effect = subprocess.CalledProcessError(1, "git rev-parse --git-dir")
        assert check_git_up_to_date() is True


def test_check_git_up_to_date_when_git_fetch_fails():
    """Test that check_git_up_to_date returns True when git fetch fails."""
    with patch("subprocess.run") as mock_run:
        # Mock git commands to simulate git fetch failure
        mock_run.side_effect = [
            type("obj", (object,), {"returncode": 0})(),  # git rev-parse --git-dir (success)
            subprocess.CalledProcessError(1, "git fetch"),  # git fetch (fails)
        ]
        assert check_git_up_to_date() is True


def test_check_git_up_to_date_when_git_rev_parse_head_fails():
    """Test that check_git_up_to_date returns True when git rev-parse HEAD fails."""
    with patch("subprocess.run") as mock_run:
        # Mock git commands to simulate git rev-parse HEAD failure
        mock_run.side_effect = [
            type("obj", (object,), {"returncode": 0})(),  # git rev-parse --git-dir (success)
            type("obj", (object,), {"returncode": 0})(),  # git fetch (success)
            type("obj", (object,), {"returncode": 0, "stdout": "main\n"}),  # git rev-parse --abbrev-ref HEAD (success)
            subprocess.CalledProcessError(1, "git rev-parse HEAD"),  # git rev-parse HEAD (fails)
        ]
        assert check_git_up_to_date() is True


def test_check_git_up_to_date_when_git_rev_parse_origin_fails():
    """Test that check_git_up_to_date returns True when git rev-parse origin/branch fails."""
    with patch("subprocess.run") as mock_run:
        # Mock git commands to simulate git rev-parse origin/branch failure
        mock_run.side_effect = [
            type("obj", (object,), {"returncode": 0})(),  # git rev-parse --git-dir (success)
            type("obj", (object,), {"returncode": 0})(),  # git fetch (success)
            type("obj", (object,), {"returncode": 0, "stdout": "main\n"}),  # git rev-parse --abbrev-ref HEAD (success)
            type("obj", (object,), {"returncode": 0, "stdout": "abc123\n"}),  # git rev-parse HEAD (success)
            subprocess.CalledProcessError(1, "git rev-parse origin/main"),  # git rev-parse origin/main (fails)
        ]
        assert check_git_up_to_date() is True


def test_command_line_script_installation():
    """Test that the uv_check command-line script is properly installed and executable."""
    # This test verifies that the entry point is correctly configured
    # and that the script can be executed as a command

    # Check if we're in a development environment where the package is installed
    try:
        # Try to import the main function directly
        from uv_check import main

        assert callable(main), "main function should be callable"

        # Test that main function can be called without errors
        with (
            patch("uv_check.is_uv_installed") as mock_check,
            patch("uv_check.dry_run_install_uv") as mock_dry_run,
            patch("builtins.print") as mock_print,
        ):
            mock_check.return_value = True
            mock_dry_run.return_value = {
                "needs_install": False,
                "message": "uv is already installed",
            }

            # This should not raise any exceptions
            main()

            # Verify the functions were called
            mock_check.assert_called()
            mock_dry_run.assert_called_once()

    except ImportError:
        # If we can't import, that's okay - this test is for when the package is installed
        pass


def test_entry_point_configuration():
    """Test that the entry point configuration in pyproject.toml is correct."""
    import os
    import toml

    # Read the pyproject.toml file
    pyproject_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "pyproject.toml")

    with open(pyproject_path, "r") as f:
        config = toml.load(f)

    # Check that the scripts section exists
    assert "project" in config, "pyproject.toml should have a [project] section"
    assert "scripts" in config["project"], "pyproject.toml should have a [project.scripts] section"

    # Check that uv_check entry point is configured
    scripts = config["project"]["scripts"]
    assert "uv_check" in scripts, "uv_check should be defined in [project.scripts]"
    assert scripts["uv_check"] == "uv_check:main", "uv_check should point to uv_check:main"


def test_command_line_execution():
    """Test that the uv_check command can be executed as a subprocess."""
    import subprocess
    import sys

    # This test verifies that the command-line script can be executed
    # It's a basic integration test to ensure the entry point works

    try:
        # Try to run uv_check as a subprocess
        # We use the current Python interpreter to ensure we're testing the installed version
        result = subprocess.run(
            [sys.executable, "-m", "uv_check"],
            capture_output=True,
            text=True,
            timeout=10,  # Add timeout to prevent hanging
        )

        # The command should execute successfully
        assert result.returncode == 0, f"uv_check should exit with code 0, got {result.returncode}"

        # Should produce some output
        assert result.stdout, "uv_check should produce output"

        # Should contain expected output
        assert "=== UV Installation Checker ===" in result.stdout, "Output should contain the header"

    except subprocess.TimeoutExpired:
        # If it times out, that's a failure
        assert False, "uv_check command timed out"
    except FileNotFoundError:
        # If the module can't be found, that's okay - this test is for when the package is installed
        pass


def test_git_repository_installation_and_execution():
    """Test the full workflow: create project, add git repo, and test entry point."""
    import os
    import subprocess
    import tempfile
    import shutil

    # This test simulates the exact scenario we tested manually:
    # 1. Create a new uv project
    # 2. Add the infra-uv git repository as a dependency
    # 3. Test that the uv_check command works

    # Create a temporary directory for the test
    with tempfile.TemporaryDirectory() as temp_dir:
        original_dir = os.getcwd()

        try:
            # Change to the temporary directory
            os.chdir(temp_dir)

            # Step 1: Initialize a new uv project
            result = subprocess.run(
                ["uv", "init", "--name", "test-project"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            assert result.returncode == 0, f"Failed to initialize project: {result.stderr}"

            # Step 2: Update Python version to 3.13 (required by infra-uv)
            pyproject_path = os.path.join(temp_dir, "pyproject.toml")
            python_version_path = os.path.join(temp_dir, ".python-version")

            # Update .python-version file
            with open(python_version_path, "w") as f:
                f.write("3.13\n")

            # Update pyproject.toml requires-python
            import toml

            with open(pyproject_path, "r") as f:
                config = toml.load(f)
            config["project"]["requires-python"] = ">=3.13"
            with open(pyproject_path, "w") as f:
                toml.dump(config, f)

            # Step 3: Add the infra-uv git repository
            result = subprocess.run(
                ["uv", "add", "git+https://github.com/PhilHem/infra-uv"],
                capture_output=True,
                text=True,
                timeout=60,
            )
            assert result.returncode == 0, f"Failed to add git dependency: {result.stderr}"

            # Step 4: Test that uv_check command works with uv run
            result = subprocess.run(
                ["uv", "run", "uv_check"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            assert result.returncode == 0, f"uv_check command failed: {result.stderr}"
            assert "=== UV Installation Checker ===" in result.stdout, "Expected output not found"

            # Step 5: Test that uv_check command works from venv bin directory
            venv_bin_path = os.path.join(temp_dir, ".venv", "bin", "uv_check")
            if os.path.exists(venv_bin_path):
                result = subprocess.run(
                    [venv_bin_path],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                assert result.returncode == 0, f"Direct venv execution failed: {result.stderr}"
                assert "=== UV Installation Checker ===" in result.stdout, "Expected output not found"

        finally:
            # Cleanup: Change back to original directory
            os.chdir(original_dir)

            # The temporary directory will be automatically cleaned up by the context manager
            # when the with block exits, but we can also explicitly clean up any additional resources
            # if needed in the future
