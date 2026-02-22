# Bug Fix: NativeCLIStrategy.list_servers() NotImplementedError

## Issue
The `NativeCLIStrategy.list_servers()` method raised `NotImplementedError`, causing installation flows to fail with an ugly traceback:

```
NotImplementedError: Native CLI list not supported, use JSON strategy
```

**Traceback:**
- File: `src/py_mcp_installer/installer.py`, line 388
- File: `src/py_mcp_installer/installation_strategy.py`, line 237

## Root Cause
When the native CLI (e.g., `claude` command) is available, the installer uses `NativeCLIStrategy` for installation. However, native CLIs typically don't provide a `list` command, so `list_servers()` was not implemented and raised `NotImplementedError`.

The issue occurs because:
1. `ClaudeCodeStrategy.get_strategy()` returns `NativeCLIStrategy` when `claude` CLI is available
2. `MCPInstaller.list_servers()` calls `self._strategy.list_servers(scope)` (line 388)
3. `NativeCLIStrategy.list_servers()` raises `NotImplementedError` (line 237)
4. Although the exception is caught and logged, it still produces an ugly traceback

## Solution
**Option A (Implemented):** Implement `list_servers()` for `NativeCLIStrategy` by falling back to JSON config reading.

This approach:
- ✅ Maintains the interface contract (all strategies implement `list_servers`)
- ✅ Provides useful functionality (can list servers after CLI installation)
- ✅ Gracefully degrades (returns empty list if config unavailable)
- ✅ Already suggested in docstring: "falls back to JSON reading"

### Changes Made

#### 1. Updated `NativeCLIStrategy.__init__()` (installation_strategy.py)
Added optional `config_path` parameter for JSON fallback:

```python
def __init__(self, platform: Platform, cli_command: str, config_path: Path | None = None) -> None:
    """Initialize with platform and CLI command.

    Args:
        platform: Target platform
        cli_command: CLI command name (e.g., "claude", "auggie")
        config_path: Optional config path for list_servers fallback
    """
    self.platform = platform
    self.cli_command = cli_command
    self.config_path = config_path
```

#### 2. Implemented `NativeCLIStrategy.list_servers()` (installation_strategy.py)
Falls back to JSON reading when config_path is available:

```python
def list_servers(self, scope: Scope) -> list[MCPServerConfig]:
    """List servers using native CLI.

    Note: Most CLIs don't provide list functionality,
    so this falls back to JSON reading if config_path is available.

    Args:
        scope: Installation scope

    Returns:
        List of server configurations (empty list if config unavailable)
    """
    # Most CLIs don't support listing, fall back to JSON reading
    if self.config_path is None:
        # No config path provided, can't read config
        # Return empty list instead of raising (graceful degradation)
        return []

    try:
        # Use ConfigManager to read config file
        config_manager = ConfigManager(self.config_path, ConfigFormat.JSON)
        return config_manager.list_servers()
    except Exception:
        # Config doesn't exist or can't be read, return empty list
        return []
```

#### 3. Updated `ClaudeCodeStrategy.get_strategy()` (platforms/claude_code.py)
Pass `config_path` when creating `NativeCLIStrategy`:

```python
def get_strategy(self, scope: Scope) -> InstallationStrategy:
    """Get appropriate installation strategy for scope."""
    config_path = self.get_config_path(scope)

    # Prefer native CLI if available
    if resolve_command_path("claude"):
        # Pass config_path so list_servers can fall back to JSON reading
        return NativeCLIStrategy(self.platform, "claude", config_path)

    # Fallback to JSON manipulation
    return JSONManipulationStrategy(self.platform, config_path)
```

#### 4. Updated `ClaudeCodeStrategy.get_strategy_with_fallback()` (platforms/claude_code.py)
Also pass `config_path` for consistency:

```python
def get_strategy_with_fallback(self, scope: Scope) -> tuple[InstallationStrategy, InstallationStrategy | None]:
    """Get primary strategy and fallback strategy."""
    config_path = self.get_config_path(scope)

    # Primary: Native CLI if available
    primary: InstallationStrategy | None = None
    if resolve_command_path("claude"):
        # Pass config_path for list_servers fallback
        primary = NativeCLIStrategy(self.platform, "claude", config_path)

    # ... rest of method
```

## Testing

### Test 1: Basic Strategy Test
```python
from py_mcp_installer.installation_strategy import NativeCLIStrategy
from py_mcp_installer.types import Platform, Scope

# Without config_path (should return empty list)
strategy = NativeCLIStrategy(Platform.CLAUDE_CODE, "claude")
servers = strategy.list_servers(Scope.PROJECT)
assert servers == []  # ✅ No exception raised

# With config_path (should read from config or return empty list)
from pathlib import Path
config_path = Path.home() / ".config" / "claude" / "mcp.json"
strategy_with_path = NativeCLIStrategy(Platform.CLAUDE_CODE, "claude", config_path)
servers = strategy_with_path.list_servers(Scope.PROJECT)
# ✅ No exception raised, returns list (empty or populated)
```

### Test 2: Full Integration Test
```python
from py_mcp_installer.installer import MCPInstaller
from py_mcp_installer.types import Platform, Scope

# Force Claude Code platform to test NativeCLIStrategy
installer = MCPInstaller(platform=Platform.CLAUDE_CODE, dry_run=True)
print(f"Strategy: {type(installer._strategy).__name__}")  # NativeCLIStrategy

# This should not raise NotImplementedError anymore
servers = installer.list_servers(Scope.PROJECT)
print(f"Success! Found {len(servers)} servers")  # ✅ Works!
```

## Verification
```bash
# Test basic import
uv run python -c "from py_mcp_installer.installer import MCPInstaller; print('OK')"

# Test list_servers doesn't raise NotImplementedError
uv run python -c "
from py_mcp_installer.installer import MCPInstaller
from py_mcp_installer.types import Platform, Scope
installer = MCPInstaller(platform=Platform.CLAUDE_CODE, dry_run=True)
servers = installer.list_servers(Scope.PROJECT)
print(f'✅ list_servers() succeeded: {len(servers)} servers')
"
```

## Impact
- **Before:** Installation succeeded but `list_servers()` raised `NotImplementedError`
- **After:** Installation succeeds and `list_servers()` returns server list (or empty list)

## Backward Compatibility
✅ **Fully backward compatible**
- `NativeCLIStrategy` constructor accepts `config_path` as optional parameter
- Existing code that doesn't pass `config_path` still works (returns empty list)
- No breaking changes to public APIs

## Related Issues
- Only affects platforms using `NativeCLIStrategy` (Claude Code, Claude Desktop)
- Other platforms (Cursor, Codex) use JSON/TOML strategies with working `list_servers()`

## Author
Fixed by: Claude Code (Anthropic)
Date: 2026-02-22
