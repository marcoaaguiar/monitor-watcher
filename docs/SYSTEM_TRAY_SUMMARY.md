# System Tray Implementation Summary

## Question
> What if we want to make it an icon in the systray that can be accessed for easy switching monitors input or switching profiles. How would you do it?

## Answer

I've implemented a **macOS menu bar application** using **rumps** (Ridiculously Uncomplicated macOS Python Statusbar apps). Here's the approach:

## Implementation Overview

### Technology Choice: **rumps**

**Why rumps?**
- ✅ Designed specifically for macOS menu bar apps
- ✅ Simple, Pythonic API
- ✅ Good macOS native integration (notifications, alerts)
- ✅ Easy nested menu support
- ✅ Active maintenance
- ❌ macOS-only (but that's our target platform)

**Alternatives Considered:**
- `pystray` - Cross-platform but less macOS integration
- `PyObjC` - Full native control but very complex
- `Electron` - Modern but 100+ MB bundle size

### Architecture: Reuse Existing Modules

**Key Design Decision:** The tray app **reuses all existing code**

```
tray.py (entry point)
    ↓
tray_app.py (menu bar UI)
    ↓
┌───────────────┬──────────────────┬─────────────┐
│ controllers.py│ profile_manager.py│ constants.py│
└───────────────┴──────────────────┴─────────────┘
         ↓                 ↓               ↓
   M1DDCController   ProfileManager   INPUT_MAP
```

**Benefits:**
- No code duplication
- Same config file as CLI
- Same validation logic
- Changes benefit both CLI and tray
- Consistent behavior

### File Structure

```
monitor-watcher/
├── tray.py           # Entry point for tray app
├── tray_app.py       # Menu bar app implementation
├── main.py           # Entry point for CLI
├── cli.py            # CLI commands
├── controllers.py    # Reused: M1DDCController
├── profile_manager.py# Reused: ProfileManager
└── constants.py      # Reused: INPUT_MAP, paths
```

### Installation

```bash
# Install with tray support
uv sync --extra tray

# Run the tray app
uv run python tray.py
```

The `rumps` dependency is **optional** - users who only want CLI don't need to install it.

## Features Implemented

### Phase 1 (Current Implementation) ✅

```
🖥️ Monitor Watcher
├─ Profiles
│  ├─ ✓ work          <- Checkmark for active profile
│  ├─  personal
│  ├─ ───────────
│  └─  Create New...  <- Launches CLI wizard
├─ ───────────
├─ Quick Switch
│  ├─ Display 1
│  │  ├─  HDMI1
│  │  ├─  DP1
│  │  └─  ...
│  └─ Display 2
│     └─  ...
├─ ───────────
├─ Refresh Monitors   <- Rebuild menu
├─ Open Config        <- Edit JSON file
└─ Quit
```

**Features:**
- Apply profiles with one click
- Manual input switching per display
- Visual feedback (checkmarks, notifications)
- Error handling with native alerts
- Profile creation via Terminal launch
- Dynamic monitor detection

### Phase 2 (Planned)

- Current input detection (show bullet on active input)
- Keyboard shortcuts (e.g., Cmd+1 for profile1)
- Profile creation dialog (native macOS)
- Better notifications
- Auto-start on login setup

### Phase 3 (Future)

- USB device monitoring
- Auto-switch profiles on USB device change
- Profile scheduling
- Custom profile icons

## How It Works

### 1. Menu Building

```python
class MonitorWatcherApp(rumps.App):
    def _build_menu(self):
        # Dynamic menu construction
        # Queries M1DDCController for monitors
        # Loads profiles from ProfileManager
```

### 2. Profile Switching

```python
def callback(sender):
    # Uses existing ProfileManager.apply_profile()
    manager.apply_profile(name, controller)
    # Shows macOS notification
    rumps.notification(title, subtitle, message)
```

### 3. Input Switching

```python
def callback(sender):
    # Uses existing M1DDCController.set_input()
    controller.set_input(display_num, input_code)
    # Shows feedback
```

### 4. Integration

- **Same config file**: `~/.config/monitor-watcher/profiles.json`
- **Same controllers**: M1DDCController for hardware
- **Same validation**: ProfileManager checks
- **Different UX**: Menu bar vs terminal

## User Experience

### Typical Workflow

1. **Setup (once)**: Use CLI to create profiles
   ```bash
   uv run python main.py create-profile
   ```

2. **Daily use**: Use tray app
   - Click icon in menu bar
   - Select profile or input
   - Get instant visual feedback

3. **Automation**: Use CLI in scripts
   ```bash
   uv run python main.py apply-profile work
   ```

### Benefits vs CLI

| Aspect | CLI | Tray App |
|--------|-----|----------|
| Access | Need to open terminal | Always visible |
| Speed | Type command | Single click |
| Feedback | Text output | Native notifications |
| Discovery | Need to know commands | Visual menu |
| Automation | ✅ Perfect | ❌ Not suitable |
| Scripting | ✅ Yes | ❌ No |

## Auto-Start on Login

Two options:

### Option 1: Login Items (Easy)
System Settings → General → Login Items → Add script

### Option 2: LaunchAgent (Advanced)
Create `~/Library/LaunchAgents/com.monitor-watcher.tray.plist`

## Distribution Options

### Development
```bash
uv run python tray.py
```

### Future Distribution
- **py2app**: Create standalone macOS .app bundle
- **PyInstaller**: Alternative bundler
- **GitHub Releases**: Distribute .app file
- **Homebrew Cask**: For easy installation

Example with py2app:
```bash
# Creates Monitor Watcher.app
py2applet --make-setup tray.py
python setup.py py2app
```

Result: Double-clickable app in `dist/Monitor Watcher.app`

## Code Quality

### Type Safety
- Full type hints in tray_app.py
- `rumps` has limited type stubs (expected warnings)
- Runtime behavior is correct

### Error Handling
- All operations wrapped in try-except
- Native macOS alert dialogs for errors
- Graceful degradation (e.g., no monitors detected)

### Testing
- Manual testing with `uv run python tray.py`
- Dry-run mode not needed (menu is read-only until click)
- Can use MockDisplayController for testing

## Documentation

Created comprehensive docs:
- **TRAY_DESIGN.md**: Detailed design decisions and architecture
- **TRAY_SETUP.md**: User-friendly setup and troubleshooting guide
- **README.md**: Updated with menu bar app section

## Next Steps to Try It

1. **Install dependencies:**
   ```bash
   uv sync --extra tray
   ```

2. **Run the app:**
   ```bash
   uv run python tray.py
   ```

3. **Test features:**
   - Click profiles to switch
   - Use Quick Switch for individual displays
   - Create new profile via Terminal
   - Refresh monitors
   - Open config file

4. **Set up auto-start** (optional):
   - Add to Login Items
   - Or create LaunchAgent

## Summary

The tray app provides a **user-friendly GUI** while maintaining the **power of the CLI**:

- ✅ One-click profile switching
- ✅ No terminal needed for daily use
- ✅ Native macOS integration
- ✅ Reuses all existing logic
- ✅ Optional dependency (CLI still works standalone)
- ✅ Easy to extend with more features

The implementation is **clean, maintainable, and follows the same architectural principles** as the rest of the codebase (single responsibility, dependency injection, reusability).
