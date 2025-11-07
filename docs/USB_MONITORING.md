# USB Auto-Switch Feature

## Overview

The USB Auto-Switch feature automatically applies a profile when your USB device (like your USB switch or mouse) connects. This is perfect for setups where you switch between computers using a USB switch.

## How It Works

The tray app monitors USB devices in the background. When your configured device connects, it automatically applies your chosen profile (e.g., "work" profile).

## Setup Guide

### Step 1: Open the Tray App Menu

Click the **"M"** icon in your menu bar.

### Step 2: Navigate to USB Auto-Switch

Find the **"USB Auto-Switch"** submenu.

### Step 3: Configure Device

1. Click **"Configure Device..."**
2. You'll see a list of all USB devices with numbers
3. Find your device (e.g., "ROCCAT Kone Pro Air (0x1e7d:0x2c92)")
4. Enter the number for your device and click "Select"

### Step 4: Select Profile

1. You'll see a list of your profiles
2. Enter the number for the profile you want to auto-apply (e.g., "work")
3. Click "Save"

### Step 5: Monitoring is Now Active!

You'll see a notification confirming the setup. The menu will now show:
- **Monitoring: [Device Name] → [Profile]** - Current monitoring status
- **✓ Enable USB Monitoring** - Checked (active)

## Using the Feature

### Enable/Disable Monitoring

Click **"USB Auto-Switch" → "Enable USB Monitoring"** to toggle monitoring on/off.

### How It Triggers

When your configured USB device connects:
1. The app detects the connection
2. Automatically applies your profile
3. Shows a notification: "Auto-switched to '[profile]' profile"
4. Updates the menu with a checkmark on the active profile

## Quick Setup for ROCCAT Kone Pro Air

Your mouse details:
- **Device**: ROCCAT Kone Pro Air
- **Vendor ID**: 0x1e7d
- **Product ID**: 0x2c92

**Quick steps:**
1. Menu → USB Auto-Switch → Configure Device...
2. Find "ROCCAT Kone Pro Air" in the list
3. Select it and choose "work" profile
4. Done! It will auto-switch when the mouse connects

## Configuration File

Settings are saved in: `~/.config/monitor-watcher/usb_config.json`

Example configuration:
```json
{
  "enabled": true,
  "vendor_id": "0x1e7d",
  "product_id": "0x2c92",
  "device_name": "ROCCAT Kone Pro Air",
  "profile": "work"
}
```

## Troubleshooting

### Device Not Detected

**Problem**: USB device not showing in the list

**Solutions**:
- Make sure the device is plugged in
- Try refreshing by reopening the configuration dialog
- Check System Profiler: `system_profiler SPUSBDataType`

### Auto-Switch Not Triggering

**Problem**: Device connects but profile doesn't switch

**Solutions**:
1. Check if monitoring is enabled (should have checkmark)
2. Verify the correct device is configured
3. Test manually by unplugging and replugging the device
4. Check notifications are enabled for the app

### Wrong Profile Applied

**Problem**: Different profile than expected is applied

**Solution**:
- Reconfigure: USB Auto-Switch → Configure Device...
- Select the correct profile when prompted

## How It Works Behind the Scenes

1. **Polling**: Checks USB devices every 2 seconds
2. **Detection**: Compares current devices with previous snapshot
3. **Trigger**: When target device appears, calls the callback
4. **Application**: Applies the configured profile
5. **Notification**: Shows success notification

## Technical Details

### Monitored Device Format

Devices are identified by:
- **Vendor ID**: Manufacturer identifier (e.g., 0x1e7d for ROCCAT)
- **Product ID**: Product identifier (e.g., 0x2c92 for Kone Pro Air)

### Background Thread

- Runs as a daemon thread (stops when app quits)
- Non-blocking (won't freeze the UI)
- Safe error handling (continues monitoring even if errors occur)

### Profile Application

- Uses the same logic as manual profile switching
- Checks current input before switching (avoids unnecessary blackouts)
- Updates menu UI with checkmark
- Respects 500ms delay between monitors

## Tips

✅ **Use your mouse/keyboard** - Monitor a device that's always connected to your USB switch (like your Kone Pro Air)

✅ **Test with dry-run** - Before setting up, you can test your profile with:
```bash
uv run python run_cli.py apply-profile work --dry-run
```

✅ **Multiple setups** - You can only monitor one device at a time, but you can change it anytime

✅ **Disable when not needed** - Toggle off monitoring if you don't want auto-switching

## Example Workflow

### Home Office Setup

**Scenario**: You have a personal laptop and work laptop sharing one monitor via USB switch

**Setup**:
1. Create two profiles:
   - "work": HDMI1 for display
   - "personal": DP1 for display
2. Configure USB monitoring for your mouse
3. Set profile to "work"

**Result**: When you switch the USB between laptops, your monitor automatically switches to match!

### Multi-Monitor KVM

**Scenario**: Two monitors and KVM switch

**Setup**:
1. Profile "work": Display 1 → HDMI1, Display 3 → USB-C
2. Profile "personal": Display 1 → DP1, Display 3 → DP1
3. Monitor your keyboard/mouse through KVM

**Result**: Both monitors automatically switch inputs when you use the KVM!

## Future Enhancements (Not Yet Implemented)

- Monitor multiple devices
- Different profiles for different devices
- Schedule-based switching
- Disconnect detection (switch back on disconnect)

---

**The USB Auto-Switch feature is ready to use! Configure it from the "M" menu bar icon.** 🎉
