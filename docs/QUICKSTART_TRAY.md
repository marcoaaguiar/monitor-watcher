# 🚀 Quick Start - Menu Bar App

## TL;DR

```bash
# Test profiles safely first (dry-run mode - won't affect monitors)
uv run python run_cli.py apply-profile work --dry-run

# Then launch the tray app
uv run python run_cli.py tray
```

Press `Cmd+Q` to quit.

## What You Get

A menu bar icon that lets you:
- Apply profiles with one click
- Switch monitor inputs instantly
- Get native macOS notifications
- USB auto-switching support
- No terminal needed!

## First Time Setup

Already done! ✅ Dependencies are installed.

## Try It Now

### Step 1: Test Your Profiles (Safe)
```bash
# Test with dry-run to see what would happen (won't affect monitors)
uv run python run_cli.py apply-profile work --dry-run
```

This shows you what changes would be made without actually switching your monitors.

Click it and explore:
- Profiles submenu
- Quick Switch submenu
- Try clicking things!

### Step 2: Launch the Tray App
```bash
uv run python run_cli.py tray
```

Look for the "M" icon in your menu bar (top right). Now it actually controls your monitors!

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
