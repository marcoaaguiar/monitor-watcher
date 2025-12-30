# Windows Setup Guide

Monitor Watcher now supports Windows! This guide will help you get started on Windows 11/10.

## Prerequisites

- Windows 10 or Windows 11
- Python 3.12 or higher
- [uv](https://github.com/astral-sh/uv) for dependency management
- Monitors that support DDC/CI (most modern monitors do)

## Installation

### 1. Install uv

```powershell
# Using PowerShell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Clone or Download the Project

```powershell
git clone https://github.com/yourusername/monitor-watcher.git
cd monitor-watcher
```

### 3. Install Dependencies

```powershell
# CLI only
uv sync --extra windows

# With system tray support (coming soon with pystray)
uv sync --extra windows
```

## Quick Start

### List Your Monitors

```powershell
uv run python run_cli.py list-monitors --detailed
```

### Create a Profile

```powershell
uv run python run_cli.py create-profile
```

Follow the interactive wizard to:
1. Name your profile (e.g., "work", "gaming")
2. Add a description
3. Select input for each monitor

### Apply a Profile

```powershell
uv run python run_cli.py apply-profile work
```

## USB Auto-Switching on Windows

The USB monitoring feature works on Windows using WMI (Windows Management Instrumentation).

### Configure USB Monitoring

```powershell
# List all USB devices
uv run python run_cli.py list-usb-devices

# Configure USB monitoring (interactive)
uv run python run_cli.py configure-usb

# Show current configuration
uv run python run_cli.py show-usb-config

# Enable/disable monitoring
uv run python run_cli.py toggle-usb-monitoring on
uv run python run_cli.py toggle-usb-monitoring off
```

## Configuration Files

On Windows, configuration files are stored in:

```
%USERPROFILE%\AppData\Local\MonitorWatcher\
├── profiles.json         # Monitor profiles
├── usb_config.json       # USB monitoring config
└── usb_monitor.log       # USB monitoring logs
```

## Input Codes

The same input codes work across all platforms:

| Input Name | Code | Description |
|------------|------|-------------|
| `hdmi1`    | 17   | HDMI port 1 |
| `hdmi2`    | 18   | HDMI port 2 |
| `dp1`      | 15   | DisplayPort 1 |
| `dp2`      | 16   | DisplayPort 2 |
| `usbc`     | 27   | USB-C |

**Note**: Your monitor may not support all inputs. Use `list-monitors --detailed` to see available inputs.

## Troubleshooting

### DDC/CI Not Working

**Problem**: Commands fail with "DDC communication error"

**Solutions**:
1. **Enable DDC/CI in monitor settings**:
   - Open your monitor's OSD menu
   - Look for "DDC/CI" or "External Control" setting
   - Enable it

2. **Run as Administrator** (some monitors require this):
   ```powershell
   # Right-click PowerShell and select "Run as Administrator"
   uv run python run_cli.py list-monitors
   ```

3. **Check monitor support**:
   - Not all monitors support DDC/CI
   - Try with a different monitor port (DP usually works better than HDMI)

### USB Monitoring Not Detecting Devices

**Problem**: USB devices not showing up in list

**Solutions**:
1. **Install WMI Python package** (should be automatic):
   ```powershell
   uv pip install wmi
   ```

2. **Check Windows Services**:
   - Open Services (services.msc)
   - Ensure "Windows Management Instrumentation" service is running

### Permission Errors

**Problem**: "Access Denied" errors

**Solution**:
- Run PowerShell as Administrator
- Some DDC/CI operations require elevated privileges

## Auto-Start on Windows (Coming Soon)

We're working on Windows auto-start support using Task Scheduler. For now, you can:

1. Create a batch script `start-monitor-watcher.bat`:
   ```batch
   @echo off
   cd C:\path\to\monitor-watcher
   uv run python run_tray.py
   ```

2. Add to Startup folder:
   - Press `Win+R`
   - Type `shell:startup`
   - Copy your batch script there

## System Tray App (Coming Soon)

We're working on cross-platform system tray support using `pystray`. This will provide:
- Windows system tray icon
- Quick profile switching
- USB monitoring control
- Right-click context menu

## Differences from macOS Version

| Feature | macOS | Windows | Notes |
|---------|-------|---------|-------|
| **Display Control** | m1ddc (Apple Silicon) | monitorcontrol (DDC/CI) | Both work great |
| **USB Monitoring** | system_profiler | WMI | Same functionality |
| **System Tray** | rumps (menu bar) | pystray (coming soon) | Different libraries, same features |
| **Config Location** | ~/.config/monitor-watcher | %APPDATA%/Local/MonitorWatcher | Platform standard |
| **Auto-Start** | LaunchAgent | Task Scheduler (coming soon) | Platform standard |

## Example Workflow

Here's a typical Windows workflow:

```powershell
# 1. Check your monitors
uv run python run_cli.py list-monitors --detailed

# 2. Create a "work" profile
uv run python run_cli.py create-profile
#   Name: work
#   Description: Work laptop via USB-C docking station
#   Monitor 1: usbc (code 27)
#   Monitor 2: dp1 (code 15)

# 3. Create a "gaming" profile
uv run python run_cli.py create-profile
#   Name: gaming
#   Description: Desktop gaming rig
#   Monitor 1: hdmi1 (code 17)
#   Monitor 2: dp2 (code 16)

# 4. Test with dry-run
uv run python run_cli.py apply-profile work --dry-run

# 5. Apply for real
uv run python run_cli.py apply-profile work

# 6. Set up USB auto-switching
uv run python run_cli.py configure-usb
#   Select your USB device (e.g., your mouse)
#   Choose profile to auto-apply (e.g., "work")

# 7. Enable USB monitoring
uv run python run_cli.py toggle-usb-monitoring on
```

Now when you plug in your USB device, Monitor Watcher will automatically switch to your "work" profile!

## Performance Notes

- **First Run**: May take a few seconds to query all monitors
- **Profile Switching**: ~500ms delay between monitors (prevents DDC timing issues)
- **USB Polling**: Checks every 2 seconds (low CPU usage)
- **Input Checking**: Skips unnecessary switches to avoid screen blackouts

## Getting Help

- Check logs: `%APPDATA%\Local\MonitorWatcher\usb_monitor.log`
- Use dry-run mode: `--dry-run` flag to test safely
- Detailed output: `--detailed` flag for more info
- GitHub Issues: [Report a bug](https://github.com/yourusername/monitor-watcher/issues)

## Known Limitations

- System tray support coming soon (use CLI for now)
- Some monitors don't support DDC/CI (check monitor manual)
- USB-C monitors may require specific drivers
- Multi-GPU setups may need additional configuration

## Tips

✅ **Use DisplayPort** - DP usually has better DDC/CI support than HDMI

✅ **Enable DDC/CI in monitor OSD** - Check your monitor's on-screen display settings

✅ **Test with dry-run** - Always use `--dry-run` first to verify configs

✅ **Check logs** - USB monitoring logs help debug connectivity issues

✅ **Monitor your USB hub** - USB switches/KVMs work great for auto-switching

## Next Steps

1. Create your profiles
2. Set up USB auto-switching
3. Test different input combinations
4. Share your configs with the community!

---

**The Windows version is fully functional! Let us know if you encounter any issues.** 🎉
