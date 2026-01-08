"""Tests for self_updater module."""

import sys
from unittest.mock import MagicMock, patch

import pytest

from py_mcp_installer.self_updater import (
    InstallMethod,
    SelfUpdater,
    UpdateCheckResult,
)


class TestInstallMethodDetection:
    """Test installation method detection."""

    def test_detect_pip_default(self):
        """Default should be pip."""
        with patch.object(sys, "executable", "/usr/bin/python"):
            updater = SelfUpdater("test-package", current_version="1.0.0")
            # Force re-detection
            updater._install_method = None
            assert updater.install_method == InstallMethod.PIP

    def test_detect_pipx(self):
        """Detect pipx installation."""
        with patch.object(
            sys, "executable", "/home/user/.local/pipx/venvs/test/bin/python"
        ):
            updater = SelfUpdater("test-package", current_version="1.0.0")
            updater._install_method = None
            assert updater.install_method == InstallMethod.PIPX

    def test_detect_uv(self):
        """Detect uv installation."""
        with patch.object(
            sys, "executable", "/home/user/.local/share/uv/tools/test/bin/python"
        ):
            updater = SelfUpdater("test-package", current_version="1.0.0")
            updater._install_method = None
            assert updater.install_method == InstallMethod.UV

    def test_detect_homebrew(self):
        """Detect homebrew installation."""
        with patch.object(
            sys, "executable", "/opt/homebrew/Cellar/python@3.11/3.11.0/bin/python"
        ):
            updater = SelfUpdater("test-package", current_version="1.0.0")
            updater._install_method = None
            assert updater.install_method == InstallMethod.HOMEBREW


class TestUpgradeCommands:
    """Test upgrade command generation."""

    @pytest.mark.parametrize(
        "method,expected",
        [
            (InstallMethod.PIP, "pip install --upgrade test-pkg"),
            (InstallMethod.PIPX, "pipx upgrade test-pkg"),
            (InstallMethod.UV, "uv tool upgrade test-pkg"),
            (InstallMethod.HOMEBREW, "brew upgrade test-pkg"),
            (InstallMethod.DEVELOPMENT, "git pull && uv sync"),
        ],
    )
    def test_upgrade_commands(self, method, expected):
        """Test correct command for each method."""
        updater = SelfUpdater("test-pkg", current_version="1.0.0")
        updater._install_method = method
        assert updater.get_upgrade_command() == expected


class TestVersionComparison:
    """Test version comparison."""

    def test_newer_version_detected(self):
        """Detect when newer version available."""
        updater = SelfUpdater("test-package", current_version="1.0.0")
        assert updater._version_gt("1.0.1", "1.0.0") is True
        assert updater._version_gt("2.0.0", "1.9.9") is True

    def test_same_version(self):
        """Same version is not greater."""
        updater = SelfUpdater("test-package", current_version="1.0.0")
        assert updater._version_gt("1.0.0", "1.0.0") is False

    def test_older_version(self):
        """Older version is not greater."""
        updater = SelfUpdater("test-package", current_version="1.0.0")
        assert updater._version_gt("0.9.0", "1.0.0") is False


class TestPyPICheck:
    """Test PyPI version checking."""

    def test_get_latest_version_success(self):
        """Test successful PyPI fetch."""
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"info": {"version": "2.0.0"}}'
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)

        with patch("urllib.request.urlopen", return_value=mock_response):
            updater = SelfUpdater("test-package", current_version="1.0.0")
            assert updater.get_latest_version() == "2.0.0"

    def test_get_latest_version_failure(self):
        """Test PyPI fetch failure returns None."""
        with patch("urllib.request.urlopen", side_effect=Exception("Network error")):
            updater = SelfUpdater("test-package", current_version="1.0.0")
            assert updater.get_latest_version() is None


class TestUpdateCheckResult:
    """Test UpdateCheckResult dataclass."""

    def test_update_check_result_creation(self):
        """Test creating UpdateCheckResult."""
        result = UpdateCheckResult(
            package_name="test-pkg",
            current_version="1.0.0",
            latest_version="2.0.0",
            update_available=True,
            install_method=InstallMethod.PIP,
            upgrade_command="pip install --upgrade test-pkg",
            is_development=False,
        )

        assert result.package_name == "test-pkg"
        assert result.current_version == "1.0.0"
        assert result.latest_version == "2.0.0"
        assert result.update_available is True
        assert result.install_method == InstallMethod.PIP
        assert result.upgrade_command == "pip install --upgrade test-pkg"
        assert result.is_development is False


class TestUpdateMethod:
    """Test update execution."""

    def test_update_already_up_to_date(self):
        """Test update when already up to date."""
        updater = SelfUpdater("test-package", current_version="1.0.0")

        with patch.object(updater, "get_latest_version", return_value="1.0.0"):
            result = updater.update(confirm=False)
            assert result is True

    def test_update_dry_run(self, capsys):
        """Test update dry run."""
        updater = SelfUpdater("test-package", current_version="1.0.0")

        with patch.object(updater, "get_latest_version", return_value="2.0.0"):
            result = updater.update(dry_run=True)
            assert result is True
            captured = capsys.readouterr()
            assert "Would run:" in captured.out

    def test_update_development_mode(self, capsys):
        """Test update in development mode."""
        updater = SelfUpdater("test-package", current_version="1.0.0")
        updater._install_method = InstallMethod.DEVELOPMENT

        with patch.object(updater, "get_latest_version", return_value="2.0.0"):
            result = updater.update(confirm=False)
            assert result is False
            captured = capsys.readouterr()
            assert "Development mode detected" in captured.out

    def test_update_cancelled(self, capsys):
        """Test update cancelled by user."""
        updater = SelfUpdater("test-package", current_version="1.0.0")

        def mock_confirm():
            return False

        with patch.object(updater, "get_latest_version", return_value="2.0.0"):
            result = updater.update(confirm=True, confirm_callback=mock_confirm)
            assert result is False
            captured = capsys.readouterr()
            assert "Upgrade cancelled" in captured.out

    def test_update_success(self):
        """Test successful update."""
        updater = SelfUpdater("test-package", current_version="1.0.0")

        with patch.object(updater, "get_latest_version", return_value="2.0.0"):
            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=0)
                result = updater.update(confirm=False)
                assert result is True
                mock_run.assert_called_once()
