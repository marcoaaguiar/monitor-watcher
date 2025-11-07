# 🚀 Quick Start - Menu Bar App

## TL;DR

```bash
# Test it safely first (demo mode - won't affect monitors)
uv run python tray_demo.py

# Then run the real thing
uv run python tray.py
```

Press `Cmd+Q` to quit.

## What You Get

A menu bar icon that lets you:
- Apply profiles with one click
- Switch monitor inputs instantly
- Get native macOS notifications
- No terminal needed!

## First Time Setup

Already done! ✅ Dependencies are installed.

## Try It Now

### Step 1: Run the Demo (Safe)
```bash
uv run python tray_demo.py
```

Look for "Monitor Watcher (DEMO)" in your menu bar (top right).

Click it and explore:
- Profiles submenu
- Quick Switch submenu
- Try clicking things!

### Step 2: Run for Real
```bash
uv run python tray.py
```

Now it actually controls your monitors!

## Common Actions

| Action | How |
|--------|-----|
| Apply profile | Click icon → Profiles → Select profile |
| Switch input | Click icon → Quick Switch → Display X → Input |
| Create profile | Click icon → Profiles → Create New... |
| Edit config | Click icon → Open Config |
| Quit | Press Cmd+Q or select Quit |

## Tips

- ✅ Run demo first to learn the menu
- ✅ Use Cmd+Q to quit (or menu)
- ✅ Notifications may not work in dev mode (that's OK - app still works!)
- ✅ Refresh monitors if you plug/unplug displays

## Building a Proper .app (Optional)

For production use with reliable notifications:

```bash
# Install build tools
uv sync --extra build

# Build standalone app
python setup.py py2app

# Run it
open dist/Monitor\ Watcher.app
```

See [APP_BUNDLE.md](APP_BUNDLE.md) for details.

## Need Help?

- App bundle guide: [APP_BUNDLE.md](APP_BUNDLE.md)
- Full guide: [TRAY_SETUP.md](TRAY_SETUP.md)
- Design docs: [TRAY_DESIGN.md](TRAY_DESIGN.md)
- Complete info: [IMPLEMENTATION_COMPLETE.md](IMPLEMENTATION_COMPLETE.md)

---

**That's it! Enjoy your new menu bar app! 🎉**
