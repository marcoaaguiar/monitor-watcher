# Auto-Start on Login

This guide explains how to set up Monitor Watcher to start automatically when you log in to macOS.

## Quick Install

Run the installation script:

```bash
cd ~/personal/monitor-watcher
./install_autostart.sh
```

That's it! The tray app will now:
- ✅ Start automatically when you log in
- ✅ Restart automatically if it crashes
- ✅ Run silently in the background
- ✅ Monitor USB devices and switch profiles

## What Gets Installed

The installation script creates a **LaunchAgent** that:
- Runs `uv run python run_tray.py` on login
- Sets the correct working directory
- Captures all output to log files
- Keeps the app running with auto-restart

### LaunchAgent Location

```
~/Library/LaunchAgents/com.monitor-watcher.app.plist
```

### Log Files

All output is captured to log files:

- **App output**: `~/.config/monitor-watcher/tray_app.log`
- **App errors**: `~/.config/monitor-watcher/tray_app.error.log`
- **USB monitoring**: `~/.config/monitor-watcher/usb_monitor.log`

View logs in real-time:
```bash
# Watch app output
tail -f ~/.config/monitor-watcher/tray_app.log

# Watch USB monitoring
tail -f ~/.config/monitor-watcher/usb_monitor.log

# Check for errors
tail -f ~/.config/monitor-watcher/tray_app.error.log
```

## Managing the Service

### Check Status

See if the service is running:
```bash
launchctl list | grep com.monitor-watcher.app
```

### Manual Start/Stop

Stop the service:
```bash
launchctl unload ~/Library/LaunchAgents/com.monitor-watcher.app.plist
```

Start the service:
```bash
launchctl load ~/Library/LaunchAgents/com.monitor-watcher.app.plist
```

### Restart the Service

```bash
launchctl unload ~/Library/LaunchAgents/com.monitor-watcher.app.plist
launchctl load ~/Library/LaunchAgents/com.monitor-watcher.app.plist
```

## Uninstall

To remove auto-start:

```bash
cd ~/personal/monitor-watcher
./uninstall_autostart.sh
```

This will:
- Stop the LaunchAgent
- Remove the plist file
- Leave all your profiles and configuration intact

You can still run the app manually with:
```bash
uv run python run_tray.py
```

## Troubleshooting

### App Not Starting

1. **Check the error log:**
   ```bash
   cat ~/.config/monitor-watcher/tray_app.error.log
   ```

2. **Verify the LaunchAgent is loaded:**
   ```bash
   launchctl list | grep com.monitor-watcher.app
   ```

3. **Check the plist file paths:**
   ```bash
   cat ~/Library/LaunchAgents/com.monitor-watcher.app.plist
   ```

4. **Test manual start:**
   ```bash
   cd ~/personal/monitor-watcher
   uv run python run_tray.py
   ```

### USB Monitoring Not Working

1. **Check USB monitoring is enabled:**
   ```bash
   uv run python run_cli.py show-usb-config
   ```

2. **Check USB monitoring logs:**
   ```bash
   tail -f ~/.config/monitor-watcher/usb_monitor.log
   ```

3. **Verify configuration:**
   ```bash
   cat ~/.config/monitor-watcher/usb_config.json
   ```

### Reinstall

If things aren't working, try reinstalling:

```bash
cd ~/personal/monitor-watcher
./uninstall_autostart.sh
./install_autostart.sh
```

## Alternative: Login Items (GUI Method)

If you prefer not to use LaunchAgents, you can add the app to Login Items manually:

1. Build the .app bundle:
   ```bash
   python setup.py py2app
   ```

2. Copy the app to Applications:
   ```bash
   cp -r dist/Monitor\ Watcher.app /Applications/
   ```

3. Add to Login Items:
   - System Settings → General → Login Items
   - Click the "+" button
   - Select "Monitor Watcher.app" from Applications

**Note:** LaunchAgent method (recommended) is more reliable and provides better logging.

## How It Works

The LaunchAgent is a macOS system service that:

1. **RunAtLoad**: Starts the app when you log in
2. **KeepAlive**: Restarts the app if it crashes
3. **WorkingDirectory**: Ensures correct file paths
4. **StandardOutPath/StandardErrorPath**: Captures all output
5. **EnvironmentVariables**: Sets up the correct PATH for uv

The plist file tells macOS:
- What command to run (`uv run python run_tray.py`)
- Where to run it from (`~/personal/monitor-watcher`)
- Where to log output (`~/.config/monitor-watcher/`)
- When to restart (on unexpected exit)
