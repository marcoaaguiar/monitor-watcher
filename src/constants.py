"""Constants used throughout the application."""

from pathlib import Path

INPUT_MAP: dict[str, int] = {
    "hdmi1": 17,
    "hdmi2": 18,
    "dp1": 15,
    "dp2": 16,
    "usbc": 27,
}

DEFAULT_CONFIG_PATH = Path.home() / ".config" / "monitor-watcher" / "profiles.json"
USB_CONFIG_PATH = Path.home() / ".config" / "monitor-watcher" / "usb_config.json"
