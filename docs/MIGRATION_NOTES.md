# Migration Notes

## Project Reorganization (Nov 2025)

The project has been reorganized with a cleaner structure:

### What Changed

**Before:**
```
monitor-watcher/
├── main.py
├── cli.py
├── controllers.py
├── ...
└── ARCHITECTURE.md
```

**After:**
```
monitor-watcher/
├── src/              # All Python source code
├── docs/             # All documentation
├── run_cli.py        # CLI entry point
└── run_tray.py       # Tray app entry point
```

### Updated Commands

All commands now use the new entry points:

| Old Command | New Command |
|------------|-------------|
| `uv run python main.py ...` | `uv run python run_cli.py ...` |
| `uv run python tray.py` | `uv run python run_tray.py` |

### Why Keep setup.py?

You might notice we still have `setup.py` even though it's deprecated in favor of `pyproject.toml`. This is intentional:

- **pyproject.toml** - Used for modern Python packaging and dependency management
- **setup.py** - Required by py2app for building macOS .app bundles (py2app hasn't fully migrated yet)

When py2app fully supports pyproject.toml configuration, we can remove setup.py entirely.

## Backward Compatibility

The old file locations still exist in `src/`, so any scripts or automation that directly import from the source files will continue to work with updated import paths.
