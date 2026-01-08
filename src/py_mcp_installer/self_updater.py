"""Self-update functionality for PyPI packages."""

from __future__ import annotations

import json
import subprocess
import sys
import urllib.request
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Callable, Optional


class InstallMethod(Enum):
    """Package installation methods."""

    PIP = "pip"
    PIPX = "pipx"
    UV = "uv"
    HOMEBREW = "homebrew"
    DEVELOPMENT = "development"


@dataclass
class UpdateCheckResult:
    """Result of checking for updates."""

    package_name: str
    current_version: str
    latest_version: str
    update_available: bool
    install_method: InstallMethod
    upgrade_command: str
    is_development: bool = False


class SelfUpdater:
    """Self-update manager for PyPI packages.

    Detects installation method and provides correct upgrade commands.

    Example:
        updater = SelfUpdater("kuzu-memory")
        result = updater.check_for_updates()
        if result.update_available:
            updater.update(confirm=True)
    """

    PYPI_API_URL = "https://pypi.org/pypi/{package}/json"

    def __init__(self, package_name: str, current_version: Optional[str] = None):
        """Initialize SelfUpdater.

        Args:
            package_name: PyPI package name
            current_version: Current version (auto-detected if not provided)
        """
        self.package_name = package_name
        self._current_version = current_version
        self._install_method: Optional[InstallMethod] = None

    @property
    def current_version(self) -> str:
        """Get current installed version."""
        if self._current_version is None:
            self._current_version = self._get_installed_version()
        return self._current_version

    @property
    def install_method(self) -> InstallMethod:
        """Get detected installation method."""
        if self._install_method is None:
            self._install_method = self._detect_installation_method()
        return self._install_method

    def _get_installed_version(self) -> str:
        """Get installed version using importlib.metadata."""
        try:
            from importlib.metadata import version

            return version(self.package_name)
        except Exception:
            return "0.0.0"

    def _detect_installation_method(self) -> InstallMethod:
        """Detect how the package was installed."""
        executable = str(Path(sys.executable).resolve())

        # Check for development mode first
        try:
            import importlib.util

            spec = importlib.util.find_spec(self.package_name.replace("-", "_"))
            if spec and spec.origin:
                origin = str(spec.origin)
                if "/src/" in origin or "site-packages" not in origin:
                    return InstallMethod.DEVELOPMENT
        except Exception:
            pass

        # pipx detection
        if ".local/pipx/venvs" in executable or "/pipx/venvs/" in executable:
            return InstallMethod.PIPX

        # uv detection
        if "/uv/tools/" in executable or "/.local/share/uv/" in executable:
            return InstallMethod.UV

        # Homebrew detection (macOS)
        if "/Cellar/" in executable or "/homebrew/" in executable.lower():
            return InstallMethod.HOMEBREW

        # Default to pip
        return InstallMethod.PIP

    def get_upgrade_command(self) -> str:
        """Get the correct upgrade command for the installation method."""
        commands = {
            InstallMethod.PIP: f"pip install --upgrade {self.package_name}",
            InstallMethod.PIPX: f"pipx upgrade {self.package_name}",
            InstallMethod.UV: f"uv tool upgrade {self.package_name}",
            InstallMethod.HOMEBREW: f"brew upgrade {self.package_name}",
            InstallMethod.DEVELOPMENT: "git pull && uv sync",
        }
        return commands[self.install_method]

    def get_latest_version(self) -> Optional[str]:
        """Fetch latest version from PyPI."""
        url = self.PYPI_API_URL.format(package=self.package_name)
        try:
            with urllib.request.urlopen(url, timeout=10) as response:
                data = json.loads(response.read().decode())
                version: Optional[str] = data.get("info", {}).get("version")
                return version
        except Exception:
            return None

    def check_for_updates(self) -> UpdateCheckResult:
        """Check if an update is available.

        Returns:
            UpdateCheckResult with version info and upgrade command
        """
        latest = self.get_latest_version() or self.current_version
        current = self.current_version

        # Compare versions
        update_available = self._version_gt(latest, current)

        return UpdateCheckResult(
            package_name=self.package_name,
            current_version=current,
            latest_version=latest,
            update_available=update_available,
            install_method=self.install_method,
            upgrade_command=self.get_upgrade_command(),
            is_development=self.install_method == InstallMethod.DEVELOPMENT,
        )

    def _version_gt(self, v1: str, v2: str) -> bool:
        """Check if v1 > v2 using simple version comparison."""
        try:

            def parse_version(v: str) -> tuple[int, ...]:
                # Handle versions like "1.2.3" or "1.2.3a1"
                parts: list[int] = []
                for part in v.split("."):
                    # Extract numeric prefix
                    num = ""
                    for c in part:
                        if c.isdigit():
                            num += c
                        else:
                            break
                    parts.append(int(num) if num else 0)
                return tuple(parts)

            return parse_version(v1) > parse_version(v2)
        except Exception:
            return False

    def update(
        self,
        dry_run: bool = False,
        confirm: bool = True,
        confirm_callback: Optional[Callable[[], bool]] = None,
    ) -> bool:
        """Run the upgrade command.

        Args:
            dry_run: If True, only print what would be done
            confirm: If True, ask for confirmation before upgrading
            confirm_callback: Custom confirmation function (returns bool)
                             Default uses input() prompt

        Returns:
            True if upgrade succeeded, False otherwise
        """
        result = self.check_for_updates()

        if not result.update_available:
            return True  # Already up to date

        if result.is_development:
            print(f"Development mode detected. Run manually: {result.upgrade_command}")
            return False

        if dry_run:
            print(f"Would run: {result.upgrade_command}")
            return True

        if confirm:
            if confirm_callback:
                confirmed = confirm_callback()
            else:
                response = input(
                    f"Upgrade {self.package_name} "
                    f"{result.current_version} → {result.latest_version}? [Y/n] "
                )
                confirmed = response.lower() in ("", "y", "yes")

            if not confirmed:
                print("Upgrade cancelled.")
                return False

        # Run upgrade
        try:
            cmd = result.upgrade_command.split()
            subprocess.run(cmd, check=True)
            return True
        except subprocess.CalledProcessError:
            return False
