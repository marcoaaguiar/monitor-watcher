# System Tray Design

## Overview

Add a macOS menu bar application for easy profile and monitor switching without using the terminal.

## Technology Choice

**rumps (Ridiculously Uncomplicated macOS Python Statusbar apps)**
- Designed specifically for macOS menu bar apps
- Simple, Pythonic API
- Good integration with macOS native features
- Active maintenance
- Easy nested menu support

## Menu Structure

```
┌─────────────────────────────────┐
│ 🖥️ Monitor Watcher              │
├─────────────────────────────────┤
│ Profiles                         │
│   ✓ Work                         │ <- Current profile (checkmark)
│     Personal                     │
│     Gaming                       │
│   ─────────────────              │
│     Create New Profile...        │
│     Manage Profiles...           │
├─────────────────────────────────┤
│ Quick Switch                     │
│   Display 1                      │
│     • HDMI1                      │ <- Current input (bullet)
│       HDMI2                      │
│       DP1                        │
│       DP2                        │
│       USB-C                      │
│   Display 2                      │
│     • DP1                        │
│       HDMI1                      │
│       ...                        │
├─────────────────────────────────┤
│ Refresh Monitors                 │
│ Settings...                      │
├─────────────────────────────────┤
│ Quit                             │
└─────────────────────────────────┘
```

## Features

### Phase 1: Basic Implementation
- [x] Menu bar icon with dropdown menu
- [x] List and apply profiles
- [x] Manual input switching per monitor
- [x] Visual indication of current state
- [x] Error handling with notifications

### Phase 2: Enhanced Features
- [ ] Current profile/input detection and display
- [ ] Profile creation via dialog
- [ ] Keyboard shortcuts
- [ ] Notifications on profile switch
- [ ] Auto-start on login

### Phase 3: Advanced Features
- [ ] USB device monitoring (detect when switch changes)
- [ ] Auto-switch profiles based on USB device
- [ ] Custom icons per profile
- [ ] Profile scheduling (switch at specific times)

## Implementation Details

### Dependencies
```toml
dependencies = [
    "click>=8.1.7",
    "rumps>=0.4.0",  # NEW: Menu bar app framework
]
```

### Module Structure

#### `tray_app.py`
Main menu bar application class:
- Inherits from `rumps.App`
- Manages menu state
- Handles user clicks
- Integrates with ProfileManager and Controllers
- Shows notifications

#### `tray.py`
Entry point for menu bar app:
- Initializes and runs the app
- Simple launcher script

### Code Integration

The tray app will **reuse existing modules**:
- `ProfileManager` - Load and apply profiles
- `M1DDCController` - Control monitors
- `constants.py` - Input mappings

No duplication of logic - just a new UI layer!

### Menu Item Actions

| Menu Item | Action |
|-----------|--------|
| Profile name (e.g., "Work") | `manager.apply_profile(name, controller)` |
| Input name (e.g., "HDMI1") | `controller.set_input(display, input_code)` |
| Create New Profile | Launch CLI wizard in Terminal |
| Manage Profiles | Open config file in default editor |
| Refresh Monitors | Rebuild menu from current state |
| Settings | Open preferences dialog |
| Quit | Exit application |

### State Management

The app needs to track:
1. **Current profile** - Which profile is active (if any)
2. **Current inputs** - What input each monitor is using
3. **Available monitors** - Dynamically updated list

**Approach:**
- Query monitors on startup and refresh
- Store last applied profile name
- No persistent state needed - always query hardware

### Error Handling

Wrap all operations in try-except:
```python
try:
    manager.apply_profile(name, controller)
    rumps.notification("Success", f"Applied profile: {name}", "")
except Exception as e:
    rumps.alert(title="Error", message=str(e))
```

### Launch Behavior

Two modes:
1. **GUI Mode**: `python tray.py` - Launch menu bar app
2. **CLI Mode**: `python main.py <command>` - Use terminal

### Auto-start on Login

**Phase 2 feature:**
- Create LaunchAgent plist file
- Copy to `~/Library/LaunchAgents/`
- Load with `launchctl load`

File: `~/Library/LaunchAgents/com.monitor-watcher.tray.plist`
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.monitor-watcher.tray</string>
    <key>ProgramArguments</key>
    <array>
        <string>/path/to/uv</string>
        <string>run</string>
        <string>python</string>
        <string>/path/to/tray.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
</dict>
</plist>
```

## Testing Strategy

1. **Manual Testing**: Run tray app and verify menu items work
2. **Dry-run Mode**: Add tray app support for MockDisplayController
3. **Error Scenarios**: Test with disconnected monitors, invalid profiles

## User Experience

### First Launch
1. App appears in menu bar with monitor icon
2. Shows notification: "Monitor Watcher started"
3. If no profiles exist, show "Create your first profile" message

### Profile Switch
1. User clicks profile name
2. Brief notification: "Switching to Work..."
3. Success notification: "Applied profile: Work"
4. Checkmark appears next to active profile

### Input Switch
1. User navigates to Display → Input
2. Click input name
3. Monitor switches immediately
4. Bullet point moves to selected input

## Distribution

### Development
```bash
uv run python tray.py
```

### Distribution Options
1. **py2app** - Package as standalone macOS app
2. **PyInstaller** - Create executable
3. **GitHub Releases** - Distribute app bundle

## Security Considerations

- App requires accessibility permissions (DDC/CI control)
- No network access needed
- Config file in user's home directory
- No telemetry or tracking

## Performance

- **Startup time**: < 1 second
- **Menu click response**: Instant
- **Profile switch**: 1-2 seconds (hardware dependent)
- **Memory usage**: ~30-50 MB (Python + rumps)

## Alternative Technologies Considered

| Technology | Pros | Cons | Decision |
|------------|------|------|----------|
| rumps | macOS native, simple API | macOS only | ✅ **Chosen** |
| pystray | Cross-platform | Less macOS integration | ❌ Not needed |
| PyObjC | Full native control | Complex, steep learning curve | ❌ Overkill |
| Electron | Modern, web tech | Large bundle size (100+ MB) | ❌ Too heavy |

## Implementation Timeline

| Phase | Effort | Features |
|-------|--------|----------|
| Phase 1 | 4-6 hours | Basic menu bar app with profile switching |
| Phase 2 | 2-3 hours | Enhanced UI, notifications, auto-start |
| Phase 3 | 4-8 hours | USB monitoring, auto-switching |

## Migration Path

Users can use both CLI and tray app:
- CLI for scripts/automation
- Tray app for interactive use
- Both use same config file
- No migration needed!
