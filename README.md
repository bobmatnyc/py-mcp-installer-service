# py-mcp-installer-service

Universal MCP server installer for AI coding tools (Claude Code, Cursor, Windsurf, etc.)

## Overview

`py-mcp-installer-service` is a self-contained Python library that provides a unified interface for installing and configuring MCP (Model Context Protocol) servers across multiple AI coding platforms.

## Supported Platforms

- Claude Code
- Claude Desktop
- Cursor
- Auggie
- Codex
- Gemini
- Windsurf
- Antigravity

## Features

- 🎯 **Platform Detection**: Automatically detects the AI coding environment
- 🔧 **Universal Interface**: Single API for all platforms
- 📦 **Installation Strategies**: Support for npm, pip, uvx, and Docker
- 🔍 **MCP Inspector**: Validates installed MCP servers
- ⚙️ **Configuration Management**: Platform-specific config handling
- 🧩 **Extensible**: Easy to add new platforms

## Quick Start

```python
from py_mcp_installer import MCPInstaller

# Auto-detect platform and install MCP server
installer = MCPInstaller()
result = installer.install_mcp_server(
    server_name="filesystem",
    install_type="npm",
    package_name="@modelcontextprotocol/server-filesystem"
)

print(f"Installation successful: {result.success}")
```

## Installation

### As a library dependency:
```bash
pip install py-mcp-installer
```

### For development:
```bash
git clone https://github.com/bobmatnyc/py-mcp-installer-service.git
cd py-mcp-installer-service
make install-dev
```

## Documentation

Comprehensive documentation is available in the [docs/](docs/) directory:

- [Architecture](docs/ARCHITECTURE.md) - System design and components
- [Implementation Plan](docs/IMPLEMENTATION-PLAN.md) - Development roadmap
- [Project Structure](docs/PROJECT-STRUCTURE.md) - Code organization
- [Quick Reference](docs/QUICK-REFERENCE.md) - Common usage patterns
- [Design Summary](docs/design/SUMMARY.md) - Design decisions

## Development

### Running Tests
```bash
make test
```

### Linting
```bash
make lint
```

### Type Checking
```bash
make type-check
```

### Formatting
```bash
make format
```

## Architecture

The library is organized into several key components:

- **Installer**: Main orchestration layer
- **Platform Detector**: Identifies the current AI coding environment
- **Installation Strategy**: Handles npm, pip, uvx, Docker installations
- **Config Manager**: Platform-specific configuration management
- **MCP Inspector**: Validates and inspects MCP servers
- **Command Builder**: Constructs platform-specific commands

See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for details.

## Contributing

Contributions are welcome! Please see the [IMPLEMENTATION-PLAN.md](docs/IMPLEMENTATION-PLAN.md) for development roadmap and guidelines.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Project Status

This library is currently in active development (v0.1.0-alpha). The API may change between versions.

## Usage in mcp-ticketer

This library is used as a git submodule in the [mcp-ticketer](https://github.com/bobmatnyc/mcp-ticketer) project to provide MCP server installation capabilities.

## Links

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/bobmatnyc/py-mcp-installer-service/issues)
- **Repository**: [GitHub](https://github.com/bobmatnyc/py-mcp-installer-service)
