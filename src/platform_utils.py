"""Platform detection and utilities for cross-platform support."""

import sys
from enum import Enum


class Platform(Enum):
    """Supported platforms."""
    MACOS = "darwin"
    WINDOWS = "win32"
    LINUX = "linux"
    UNKNOWN = "unknown"


def get_platform() -> Platform:
    """
    Detect the current platform.

    Returns:
        Platform enum value for the current operating system
    """
    system = sys.platform.lower()

    if system == "darwin":
        return Platform.MACOS
    elif system.startswith("win"):
        return Platform.WINDOWS
    elif system.startswith("linux"):
        return Platform.LINUX
    else:
        return Platform.UNKNOWN


def is_macos() -> bool:
    """Check if running on macOS."""
    return get_platform() == Platform.MACOS


def is_windows() -> bool:
    """Check if running on Windows."""
    return get_platform() == Platform.WINDOWS


def is_linux() -> bool:
    """Check if running on Linux."""
    return get_platform() == Platform.LINUX


def get_config_dir_name() -> str:
    """
    Get the appropriate config directory name for the platform.

    Returns:
        ".config/monitor-watcher" for Unix-like systems
        "MonitorWatcher" for Windows (to be used in AppData)
    """
    if is_windows():
        return "MonitorWatcher"
    else:
        return ".config/monitor-watcher"


def get_platform_name() -> str:
    """Get a human-readable platform name."""
    p = get_platform()
    if p == Platform.MACOS:
        return "macOS"
    elif p == Platform.WINDOWS:
        return "Windows"
    elif p == Platform.LINUX:
        return "Linux"
    else:
        return "Unknown"
