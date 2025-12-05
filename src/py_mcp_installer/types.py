"""Type definitions for py-mcp-installer-service."""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional


class Platform(str, Enum):
    """Supported AI coding platforms."""

    CLAUDE_CODE = "claude_code"
    CLAUDE_DESKTOP = "claude_desktop"
    CURSOR = "cursor"
    AUGGIE = "auggie"
    CODEX = "codex"
    GEMINI = "gemini"
    WINDSURF = "windsurf"
    ANTIGRAVITY = "antigravity"
    UNKNOWN = "unknown"


class InstallType(str, Enum):
    """Installation methods for MCP servers."""

    NPM = "npm"
    PIP = "pip"
    UVX = "uvx"
    DOCKER = "docker"


@dataclass
class InstallResult:
    """Result of an installation operation."""

    success: bool
    platform: Platform
    server_name: str
    message: str
    details: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
