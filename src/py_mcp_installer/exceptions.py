"""Custom exceptions for py-mcp-installer-service."""


class MCPInstallerError(Exception):
    """Base exception for all installer errors."""

    pass


class PlatformNotDetectedError(MCPInstallerError):
    """Platform could not be detected."""

    pass


class InstallationError(MCPInstallerError):
    """Installation failed."""

    pass


class ConfigurationError(MCPInstallerError):
    """Configuration error."""

    pass
