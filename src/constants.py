"""Constants used throughout the application."""

from pathlib import Path
from platform_utils import is_windows

INPUT_MAP: dict[str, int] = {
    "hdmi1": 17,
    "hdmi2": 18,
    "dp1": 15,
    "dp2": 16,
    "usbc": 27,
}


def _get_config_dir() -> Path:
    """Get the appropriate config directory for the current platform."""
    if is_windows():
        # Windows: Use AppData\Local
        return Path.home() / "AppData" / "Local" / "MonitorWatcher"
    else:
        # macOS/Linux: Use .config
        return Path.home() / ".config" / "monitor-watcher"


DEFAULT_CONFIG_PATH = _get_config_dir() / "profiles.json"
USB_CONFIG_PATH = _get_config_dir() / "usb_config.json"
