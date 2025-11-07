#!/bin/bash
# Install monitor-watcher to start automatically on login

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLIST_FILE="$SCRIPT_DIR/com.monitor-watcher.app.plist"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
INSTALLED_PLIST="$LAUNCH_AGENTS_DIR/com.monitor-watcher.app.plist"

echo "Monitor Watcher - Auto-Start Installation"
echo "=========================================="
echo ""

# Create LaunchAgents directory if it doesn't exist
if [ ! -d "$LAUNCH_AGENTS_DIR" ]; then
    echo "Creating LaunchAgents directory..."
    mkdir -p "$LAUNCH_AGENTS_DIR"
fi

# Stop any existing instance
if launchctl list | grep -q "com.monitor-watcher.app"; then
    echo "Stopping existing instance..."
    launchctl unload "$INSTALLED_PLIST" 2>/dev/null || true
fi

# Copy plist file
echo "Installing LaunchAgent..."
cp "$PLIST_FILE" "$INSTALLED_PLIST"

# Load the LaunchAgent
echo "Loading LaunchAgent..."
launchctl load "$INSTALLED_PLIST"

echo ""
echo "✓ Installation complete!"
echo ""
echo "Monitor Watcher will now:"
echo "  - Start automatically on login"
echo "  - Restart automatically if it crashes"
echo "  - Run in the background"
echo ""
echo "Logs:"
echo "  - App output: ~/.config/monitor-watcher/tray_app.log"
echo "  - App errors: ~/.config/monitor-watcher/tray_app.error.log"
echo "  - USB monitoring: ~/.config/monitor-watcher/usb_monitor.log"
echo ""
echo "To uninstall:"
echo "  ./uninstall_autostart.sh"
