# Monitor Watcher

A cross-platform CLI tool to control monitor inputs with profile-based configuration. Works on macOS, Windows, and Linux!

## Platform Support

| Platform | Display Control | USB Monitoring | System Tray | Status |
|----------|----------------|----------------|-------------|---------|
| **macOS** | m1ddc (Apple Silicon) | system_profiler | rumps (menu bar) | ✅ Fully Supported |
| **Windows** | monitorcontrol (DDC/CI) | WMI | pystray (coming soon) | ✅ Fully Supported (CLI) |
| **Linux** | monitorcontrol (DDC/CI) | system info | pystray (coming soon) | ⚠️ Experimental |

## Prerequisites

### macOS
- macOS with Apple Silicon (M1/M2/M3/M4)
- [m1ddc](https://github.com/waydabber/m1ddc) installed: `brew install m1ddc`
- Python 3.12+
- [uv](https://github.com/astral-sh/uv) for dependency management

### Windows
- Windows 10 or Windows 11
- Python 3.12+
- [uv](https://github.com/astral-sh/uv) for dependency management
- Monitors with DDC/CI support (most modern monitors)

### Linux
- Python 3.12+
- [uv](https://github.com/astral-sh/uv) for dependency management
- Monitors with DDC/CI support

## Installation

### macOS

```bash
# CLI only
uv sync

# With menu bar app (recommended)
uv sync --extra macos
```

### Windows

```powershell
# Install and set up dependencies
uv sync --extra windows
```

See [docs/WINDOWS_SETUP.md](docs/WINDOWS_SETUP.md) for detailed Windows setup instructions.

### Linux

```bash
# Install and set up dependencies
uv sync --extra linux
```

## Quick Start

### Command Line Interface
```bash
# List your monitors
uv run python run_cli.py list-monitors --detailed

# Create a profile interactively
uv run python run_cli.py create-profile

# Apply a profile
uv run python run_cli.py apply-profile work
```

### Menu Bar App 🆕
```bash
# Launch the menu bar app
uv run python run_cli.py tray
```

The "M" icon will appear in your menu bar for quick profile switching!
See [docs/QUICKSTART_TRAY.md](docs/QUICKSTART_TRAY.md) for detailed setup and usage instructions.

### Auto-Start on Login
```bash
# Install auto-start on login
./install_autostart.sh

# Uninstall auto-start
./uninstall_autostart.sh
```

The tray app will automatically start when you log in, with USB monitoring enabled!
See [docs/AUTOSTART.md](docs/AUTOSTART.md) for detailed setup, troubleshooting, and log locations.

## Usage

### List Connected Monitors

```bash
uv run python run_cli.py list-monitors
uv run python run_cli.py list-monitors --detailed
```

### Profile Management

Profiles allow you to configure multiple monitors with specific inputs and switch them all at once.

#### Create a Profile (Interactive Wizard)

Use the interactive wizard to create profiles easily:

```bash
uv run python run_cli.py create-profile
```

The wizard will guide you through:
1. Naming your profile
2. Adding a description
3. Viewing available monitors
4. Selecting inputs for each monitor
5. Confirming and saving

#### List Available Profiles

```bash
uv run python run_cli.py list-profiles
```

#### Apply a Profile

```bash
uv run python run_cli.py apply-profile work
uv run python run_cli.py apply-profile personal
```

#### Delete a Profile

```bash
# With confirmation prompt
uv run python run_cli.py delete-profile work

# Skip confirmation
uv run python run_cli.py delete-profile work --yes
```

#### View Configuration

```bash
uv run python run_cli.py show-config
```

### Manual Input Switching

Switch a specific display to a specific input:

```bash
uv run python run_cli.py switch 1 hdmi1
uv run python run_cli.py switch 1 dp1
uv run python run_cli.py switch 3 usbc
```

Available inputs: `hdmi1`, `hdmi2`, `dp1`, `dp2`, `usbc`

### USB Auto-Switching

Configure automatic profile switching when a USB device connects:

```bash
# List all connected USB devices
uv run python run_cli.py list-usb-devices

# Configure USB monitoring (interactive)
uv run python run_cli.py configure-usb

# Show current USB monitoring configuration
uv run python run_cli.py show-usb-config

# Enable/disable USB monitoring
uv run python run_cli.py toggle-usb-monitoring on
uv run python run_cli.py toggle-usb-monitoring off
```

For detailed USB monitoring documentation, see [docs/USB_MONITORING.md](docs/USB_MONITORING.md).

### Dry Run Mode

Test commands without affecting your actual monitors using the `--dry-run` flag:

```bash
# Test applying a profile
uv run python run_cli.py apply-profile work --dry-run

# Test switching an input
uv run python run_cli.py switch 1 dp1 --dry-run

# Test listing monitors
uv run python run_cli.py list-monitors --dry-run --detailed
```

Dry run mode will show exactly what would happen without making any changes to your monitors. Perfect for testing configurations before applying them!

## Configuration

The configuration file is located at `~/.config/monitor-watcher/profiles.json`

### Example Configuration

```json
{
  "profiles": {
    "work": {
      "description": "Work setup - laptop on left, external on right",
      "monitors": {
        "1": "hdmi1",
        "3": "dp1"
      }
    },
    "gaming": {
      "description": "Gaming setup - both on DisplayPort",
      "monitors": {
        "1": "dp1",
        "3": "dp2"
      }
    },
    "personal": {
      "description": "Personal laptop setup",
      "monitors": {
        "1": "usbc",
        "3": "hdmi1"
      }
    }
  }
}
```

### Monitor Numbers

To find your monitor numbers, run:

```bash
uv run python run_cli.py list-monitors --detailed
```

Look for the display number in brackets like `[1]`, `[2]`, `[3]`.

## Input Codes

| Input Name | Code | Description |
|------------|------|-------------|
| `hdmi1`    | 17   | HDMI port 1 |
| `hdmi2`    | 18   | HDMI port 2 |
| `dp1`      | 15   | DisplayPort 1 |
| `dp2`      | 16   | DisplayPort 2 |
| `usbc`     | 27   | USB-C |

## Example Workflow

Here's a typical workflow for setting up and using monitor profiles:

```bash
# 1. First, see what monitors are connected
uv run python run_cli.py list-monitors --detailed

# 2. Create a profile using the interactive wizard
uv run python run_cli.py create-profile
#   - Enter name: "work"
#   - Enter description: "Work laptop setup"
#   - Select inputs for each display

# 3. Create another profile for a different setup
uv run python run_cli.py create-profile
#   - Enter name: "personal"
#   - Enter description: "Personal desktop setup"
#   - Select different inputs

# 4. View all your profiles
uv run python run_cli.py list-profiles

# 5. Test a profile with dry-run mode first
uv run python run_cli.py apply-profile work --dry-run

# 6. Apply the profile for real
uv run python run_cli.py apply-profile work

# 7. Switch between profiles as needed
uv run python run_cli.py apply-profile personal
uv run python run_cli.py apply-profile work

# Or use the menu bar app for one-click switching!
uv run python run_cli.py tray
```

## Project Structure

```
monitor-watcher/
├── src/                      # Python source code
│   ├── main.py              # CLI entry point (for pip install)
│   ├── cli.py               # Unified CLI with all commands (including 'tray')
│   ├── tray_app.py          # Menu bar application (macOS)
│   ├── controllers.py       # Display controller implementations
│   │                        #   - M1DDCController (macOS)
│   │                        #   - WindowsDisplayController (Windows/Linux)
│   │                        #   - MockDisplayController (testing)
│   │                        #   - create_display_controller() factory
│   ├── profile_manager.py   # Profile management and persistence
│   ├── usb_monitor.py       # Cross-platform USB device monitoring
│   │                        #   - MacOSUSBMonitor (system_profiler)
│   │                        #   - WindowsUSBMonitor (WMI)
│   │                        #   - create_usb_monitor() factory
│   ├── platform_utils.py    # Platform detection utilities
│   └── constants.py         # Application constants
├── docs/                    # Documentation
│   ├── ARCHITECTURE.md      # Architecture and design decisions
│   ├── QUICKSTART_TRAY.md   # Quick start guide for tray app (macOS)
│   ├── TRAY_SETUP.md        # Detailed tray app setup (macOS)
│   ├── TRAY_DESIGN.md       # Tray app design document
│   ├── USB_MONITORING.md    # USB auto-switch setup guide
│   ├── AUTOSTART.md         # Auto-start on login setup (macOS)
│   ├── WINDOWS_SETUP.md     # Windows setup and usage guide
│   └── APP_BUNDLE.md        # Building standalone .app (macOS)
├── run_cli.py               # Unified CLI entry point (includes 'tray' command)
├── install_autostart.sh     # Install auto-start on login (macOS)
├── uninstall_autostart.sh   # Uninstall auto-start (macOS)
├── com.monitor-watcher.app.plist  # LaunchAgent configuration (macOS)
├── pyproject.toml           # Project configuration (cross-platform)
├── setup.py                 # py2app build configuration (macOS)
└── README.md                # This file
```

For detailed architecture documentation, see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Features

✅ **Cross-Platform** - Works on macOS, Windows, and Linux with automatic platform detection
✅ **CLI Interface** - Full command-line control on all platforms
✅ **Menu Bar App** - One-click profile switching with "M" icon (macOS)
✅ **Profile Management** - Save and switch between monitor configurations
✅ **USB Auto-Switch** - Automatically switch profiles when USB devices connect
✅ **Auto-Start on Login** - Tray app starts automatically (macOS with LaunchAgent, Windows coming soon)
✅ **Input Checking** - Skips unnecessary switches (no screen blackouts!)
✅ **Dry Run Mode** - Test configurations safely
✅ **Interactive Wizard** - Easy profile creation
✅ **Error Handling** - Clear error messages with detailed debugging info
✅ **Platform Detection** - Automatically uses the right controller for your OS
