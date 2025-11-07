#!/bin/bash
# Uninstall monitor-watcher auto-start

set -e

LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
INSTALLED_PLIST="$LAUNCH_AGENTS_DIR/com.monitor-watcher.app.plist"

echo "Monitor Watcher - Auto-Start Uninstallation"
echo "==========================================="
echo ""

if [ ! -f "$INSTALLED_PLIST" ]; then
    echo "LaunchAgent is not installed."
    exit 0
fi

# Stop and unload the LaunchAgent
if launchctl list | grep -q "com.monitor-watcher.app"; then
    echo "Stopping LaunchAgent..."
    launchctl unload "$INSTALLED_PLIST"
fi

# Remove the plist file
echo "Removing LaunchAgent..."
rm "$INSTALLED_PLIST"

echo ""
echo "✓ Uninstallation complete!"
echo ""
echo "Monitor Watcher will no longer start automatically."
echo "You can still run it manually with: uv run python run_tray.py"
