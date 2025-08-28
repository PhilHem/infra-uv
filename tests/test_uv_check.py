import pytest
from unittest.mock import patch
import subprocess
import sys
import os

# Add the parent directory to the path so we can import uv_check
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from uv_check import is_uv_installed, install_uv


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
