"""Platform detection logic."""

import os
import platform
from pathlib import Path
from typing import Optional

from .types import Platform


class PlatformDetector:
    """Detect the current AI coding platform."""

    @staticmethod
    def detect() -> Platform:
        """
        Auto-detect the current AI coding platform.

        Returns:
            Detected Platform enum value
        """
        # Check environment variables first
        if os.getenv("CLAUDE_CODE_ENV"):
            return Platform.CLAUDE_CODE

        # Check for platform-specific directories
        home = Path.home()

        # Claude Code
        if (home / ".config" / "claude-code").exists():
            return Platform.CLAUDE_CODE

        # Claude Desktop
        if (home / ".config" / "Claude").exists():
            return Platform.CLAUDE_DESKTOP

        # Cursor
        if (home / ".cursor").exists():
            return Platform.CURSOR

        # Default to unknown
        return Platform.UNKNOWN

    @staticmethod
    def get_config_path(platform: Platform) -> Optional[Path]:
        """
        Get the configuration path for a platform.

        Args:
            platform: The platform to get config path for

        Returns:
            Path to config directory or None if unknown
        """
        home = Path.home()
        system = platform.system()

        config_paths = {
            Platform.CLAUDE_CODE: {
                "Darwin": home / ".config" / "claude-code",
                "Linux": home / ".config" / "claude-code",
                "Windows": home / "AppData" / "Roaming" / "claude-code",
            },
            Platform.CLAUDE_DESKTOP: {
                "Darwin": home / "Library" / "Application Support" / "Claude",
                "Linux": home / ".config" / "Claude",
                "Windows": home / "AppData" / "Roaming" / "Claude",
            },
            Platform.CURSOR: {
                "Darwin": home / "Library" / "Application Support" / "Cursor",
                "Linux": home / ".cursor",
                "Windows": home / "AppData" / "Roaming" / "Cursor",
            },
        }

        return config_paths.get(platform, {}).get(system)
