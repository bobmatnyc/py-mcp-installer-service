"""py-mcp-installer-service: Universal MCP server installer for AI coding tools."""

__version__ = "0.1.0"

from .installer import MCPInstaller
from .platform_detector import PlatformDetector
from .types import InstallResult, Platform

__all__ = [
    "MCPInstaller",
    "PlatformDetector",
    "InstallResult",
    "Platform",
]
