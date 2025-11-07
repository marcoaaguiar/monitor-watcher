# Building a Standalone .app Bundle

## Why the .venv/bin/Info.plist Location Was Wrong

You're absolutely right - putting Info.plist in `.venv/bin/` is a bad practice because:
- The venv can be deleted/recreated (losing the file)
- It's not version controlled
- It's not the standard macOS app structure
- It's a workaround, not a proper solution

## Better Solutions

### Option 1: Development Mode (Current)

For development, I've moved Info.plist to the **project root**:
- [Info.plist](Info.plist) - Now version controlled and permanent
- Still works with `uv run python tray.py`
- Notifications may still be unreliable in development mode

### Option 2: Production .app Bundle (Recommended)

Build a proper macOS application bundle using **py2app**:

#### Setup

```bash
# Install py2app
uv sync --extra build

# Build the app bundle
python setup.py py2app
```

This creates:
```
dist/
└── Monitor Watcher.app/
    └── Contents/
        ├── Info.plist          ← Proper location!
        ├── MacOS/
        │   └── Monitor Watcher  ← Executable
        └── Resources/
            └── (your Python code)
```

#### Benefits

✅ **Info.plist in the right place** - `Monitor Watcher.app/Contents/Info.plist`
✅ **Notifications work reliably** - macOS recognizes it as a proper app
✅ **Double-click to run** - No need for `uv run`
✅ **Add to Login Items** - System Preferences integration
✅ **Distributable** - Share with others (no Python needed)
✅ **Icon support** - Add a custom menu bar icon

#### Usage

```bash
# Build the .app
python setup.py py2app

# Run it
open dist/Monitor\ Watcher.app

# Or move to Applications folder
mv dist/Monitor\ Watcher.app /Applications/
```

### Option 3: Alias Mode (Development)

For faster development iterations:

```bash
# Build in alias mode (faster, points to source code)
python setup.py py2app -A

# Changes to source code take effect immediately
# No need to rebuild each time
```

## Recommendation

**For now (testing):**
- Use the Info.plist in the project root
- Run with `uv run python tray.py`
- Notifications wrapped in try-except will handle failures

**For production use:**
- Build a proper .app bundle with py2app
- Move to /Applications/
- Add to Login Items for auto-start

## Building the .app Bundle

When you're ready to create a proper standalone app:

```bash
# 1. Install build dependencies
uv sync --extra build

# 2. Build the app
python setup.py py2app

# 3. Test it
open dist/Monitor\ Watcher.app

# 4. Install to Applications (optional)
cp -r dist/Monitor\ Watcher.app /Applications/
```

The app will work on any macOS system (Apple Silicon or Intel) without requiring Python to be installed!

## Customization

Edit [setup.py](setup.py) to:
- Add a custom icon: `'iconfile': 'icon.icns'`
- Hide from Dock: `'LSUIElement': True`
- Change bundle identifier
- Add additional resources

## Troubleshooting

**Build fails:**
```bash
# Make sure all dependencies are installed
uv sync --extra tray --extra build
```

**App won't run:**
```bash
# Check for errors
open -a Console
# Filter by "Monitor Watcher"
```

**Notifications still don't work:**
- System Settings → Notifications → Monitor Watcher
- Enable "Allow Notifications"

---

**Current Status:** Info.plist moved to project root. Ready to build .app bundle when needed!
