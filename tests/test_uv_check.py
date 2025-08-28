import os
import subprocess
import sys
from unittest.mock import patch

# Add the parent directory to the path so we can import uv_check
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from uv_check import dry_run_install_uv, install_uv, is_uv_installed, main, check_git_up_to_date, ensure_git_up_to_date


def test_is_uv_installed_when_available():
    """Test that is_uv_installed returns True when uv is available."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        assert is_uv_installed() is True
        mock_run.assert_called_once_with(
            ["uv", "--version"], capture_output=True, check=True
        )


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
