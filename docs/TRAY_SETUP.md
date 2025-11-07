# System Tray App Setup Guide

This guide explains how to set up and use the macOS menu bar (system tray) application.

## Installation

### 1. Install the tray dependencies:

```bash
# Install with the tray extra
uv sync --extra tray
```

This installs the `rumps` library which provides the menu bar functionality.

### 2. Run the tray app:

```bash
uv run python tray.py
```

The Monitor Watcher icon will appear in your menu bar!

## Features

### Current Implementation (Phase 1) ✅

- **Profile Switching**: Click a profile name to apply it
- **Quick Switch**: Manually change inputs for individual displays
- **Visual Feedback**:
  - Checkmark (✓) shows current active profile
  - macOS notifications on success/error
- **Profile Management**:
  - Launch CLI wizard to create new profiles
  - Open config file in default editor
- **Refresh**: Update monitor list dynamically

### Menu Structure

```
🖥️ Monitor Watcher
├─ Profiles
│  ├─ ✓ work          <- Active profile
│  ├─  personal
│  ├─ ───────────
│  └─  Create New...
├─ ───────────
├─ Quick Switch
│  ├─ Display 1
│  │  ├─  HDMI1
│  │  ├─  HDMI2
│  │  ├─  DP1        <- Current
│  │  ├─  DP2
│  │  └─  USB-C
│  └─ Display 2
│     └─ ...
├─ ───────────
├─ Refresh Monitors
├─ Open Config
└─ Quit
```

## Usage Examples

### Apply a Profile
1. Click the Monitor Watcher icon in menu bar
2. Hover over "Profiles"
3. Click the profile name (e.g., "work")
4. Notification appears showing success

### Switch Individual Display
1. Click the Monitor Watcher icon
2. Hover over "Quick Switch"
3. Select display (e.g., "Display 1")
4. Click desired input (e.g., "HDMI1")

### Create New Profile
1. Click "Profiles" → "Create New..."
2. Terminal opens with the interactive wizard
3. Follow prompts to create profile
4. New profile appears in menu immediately

## Auto-Start on Login (Optional)

To launch the tray app automatically when you log in:

### Option 1: System Preferences (Easiest)
1. Open System Settings → General → Login Items
2. Click "+" under "Open at Login"
3. Create a simple script:
   ```bash
   #!/bin/bash
   cd /path/to/monitor-watcher
   uv run python tray.py
   ```
4. Save as `start-monitor-watcher.sh`
5. Make executable: `chmod +x start-monitor-watcher.sh`
6. Add the script to Login Items

### Option 2: LaunchAgent (Advanced)

Create `~/Library/LaunchAgents/com.monitor-watcher.tray.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.monitor-watcher.tray</string>

    <key>ProgramArguments</key>
    <array>
        <string>/Users/YOUR_USERNAME/.local/bin/uv</string>
        <string>run</string>
        <string>python</string>
        <string>/Users/YOUR_USERNAME/path/to/monitor-watcher/tray.py</string>
    </array>

    <key>WorkingDirectory</key>
    <string>/Users/YOUR_USERNAME/path/to/monitor-watcher</string>

    <key>RunAtLoad</key>
    <true/>

    <key>KeepAlive</key>
    <false/>

    <key>StandardOutPath</key>
    <string>/tmp/monitor-watcher.log</string>

    <key>StandardErrorPath</key>
    <string>/tmp/monitor-watcher-error.log</string>
</dict>
</plist>
```

Then load it:
```bash
launchctl load ~/Library/LaunchAgents/com.monitor-watcher.tray.plist
```

## Troubleshooting

### App doesn't appear in menu bar
- Check if Python process is running: `ps aux | grep tray.py`
- Check for errors: `uv run python tray.py` (run in terminal to see output)
- Ensure m1ddc is installed: `which m1ddc`

### "No Monitors Detected"
- Verify m1ddc can see monitors: `m1ddc display list`
- Check monitor connections (USB-C required for DDC/CI)
- Try "Refresh Monitors" menu item

### Profile doesn't apply
- Check config file syntax: `uv run python main.py show-config`
- Verify display numbers match: `m1ddc display list`
- Check Terminal output for errors

### Notifications not showing
- Go to System Settings → Notifications
- Find "Python" or "Terminal" in the list
- Enable notifications

## Architecture

The tray app **reuses all existing modules**:
- `controllers.py` - M1DDCController for hardware control
- `profile_manager.py` - Profile loading and application
- `constants.py` - Input mappings

This means:
- Same config file as CLI (`~/.config/monitor-watcher/profiles.json`)
- Same behavior and validation
- Changes in one affect both (CLI and tray)

## Development

### Testing
```bash
# Run with visible output
uv run python tray.py

# The app will print errors to terminal
# Use Cmd+Q to quit
```

### Adding Features
See `TRAY_DESIGN.md` for planned features and implementation details.

### Type Hints
The `rumps` library has limited type stub support, so you'll see type warnings in the IDE. This is expected and doesn't affect functionality.

## CLI vs Tray App

| Feature | CLI | Tray App |
|---------|-----|----------|
| Apply profiles | ✅ | ✅ |
| Create profiles | ✅ Interactive wizard | ✅ Launches CLI wizard |
| Switch inputs | ✅ | ✅ |
| List monitors | ✅ | ✅ |
| Dry-run mode | ✅ | ❌ Not needed |
| Scripting/automation | ✅ Perfect for | ❌ |
| Quick access | ❌ | ✅ Always available |
| Visual feedback | ❌ | ✅ Notifications |
| USB monitoring | ❌ Future | ✅ Future |

## Recommended Workflow

1. **Setup**: Use CLI to create initial profiles
   ```bash
   uv run python main.py create-profile
   ```

2. **Daily Use**: Use tray app for quick switching
   - Click icon → Select profile
   - No terminal needed!

3. **Automation**: Use CLI in scripts
   ```bash
   uv run python main.py apply-profile work
   ```

4. **Advanced**: Run both simultaneously
   - Tray app for interactive use
   - CLI for scripts/shortcuts

## Next Steps

After getting comfortable with the tray app, consider:

1. **Phase 2 Features** (see TRAY_DESIGN.md):
   - Keyboard shortcuts
   - Better current state detection
   - Enhanced notifications

2. **Phase 3 Features**:
   - USB device monitoring
   - Auto-switch based on USB device
   - Profile scheduling

3. **Packaging**:
   - Create standalone .app bundle
   - Distribute on GitHub Releases
   - Auto-update support

## Support

If you encounter issues:
1. Check the Terminal output when running `uv run python tray.py`
2. Review logs if using LaunchAgent
3. Test CLI commands to ensure m1ddc is working
4. Create an issue with error details
