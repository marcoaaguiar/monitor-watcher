"""USB device monitoring for automatic profile switching with platform-specific implementations."""

import threading
import time
from typing import Callable, Optional
from abc import ABC, abstractmethod
import subprocess
from pathlib import Path
from datetime import datetime

from platform_utils import Platform, get_platform, is_windows


# Log file for USB monitoring
def _get_log_file() -> Path:
    """Get the appropriate log file path for the current platform."""
    if is_windows():
        # Windows: Use AppData
        return Path.home() / "AppData" / "Local" / "MonitorWatcher" / "usb_monitor.log"
    else:
        # macOS/Linux: Use .config
        return Path.home() / ".config" / "monitor-watcher" / "usb_monitor.log"


LOG_FILE = _get_log_file()


def _log(message: str) -> None:
    """Write a timestamped log message to both stdout and log file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {message}"

    # Print to stdout (for CLI usage)
    print(log_message)

    # Write to log file
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_FILE, "a") as f:
            f.write(log_message + "\n")
    except Exception:
        pass  # Silently fail if logging doesn't work


class USBMonitor(ABC):
    """Abstract base class for USB device monitoring."""

    def __init__(self, on_connect: Optional[Callable[[str, str], None]] = None):
        """
        Initialize USB monitor.

        Args:
            on_connect: Callback function called when monitored device connects.
                       Receives (vendor_id, product_id) as arguments.
        """
        self.on_connect = on_connect
        self.monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.target_vendor_id: Optional[str] = None
        self.target_product_id: Optional[str] = None
        self._last_devices: set[tuple[str, str]] = set()

    def set_target_device(self, vendor_id: str, product_id: str) -> None:
        """
        Set the target USB device to monitor.

        Args:
            vendor_id: USB vendor ID (e.g., "0x05e3")
            product_id: USB product ID (e.g., "0x0610")
        """
        self.target_vendor_id = vendor_id
        self.target_product_id = product_id

    def start_monitoring(self) -> None:
        """Start monitoring USB devices in a background thread."""
        if self.monitoring:
            _log("[USB Monitor] Already monitoring, ignoring start request")
            return

        _log(f"[USB Monitor] Starting monitoring for {self.target_vendor_id}:{self.target_product_id}")
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()

    def stop_monitoring(self) -> None:
        """Stop monitoring USB devices."""
        if not self.monitoring:
            _log("[USB Monitor] Not monitoring, ignoring stop request")
            return

        _log(f"[USB Monitor] Stopping monitoring for {self.target_vendor_id}:{self.target_product_id}")
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
            self.monitor_thread = None

    @abstractmethod
    def _get_connected_devices(self) -> set[tuple[str, str]]:
        """
        Get all currently connected USB devices.

        Returns:
            Set of (vendor_id, product_id) tuples
        """
        pass

    @abstractmethod
    def get_all_usb_devices(self) -> list[dict[str, str]]:
        """
        Get a list of all currently connected USB devices.

        Returns:
            List of dicts with 'vendor_id', 'product_id', and 'name'
        """
        pass

    def _monitor_loop(self) -> None:
        """Main monitoring loop that checks for USB device changes."""
        # Initialize with current devices
        self._last_devices = self._get_connected_devices()
        _log(f"[USB Monitor] Monitor loop started for device {self.target_vendor_id}:{self.target_product_id}")

        while self.monitoring:
            try:
                current_devices = self._get_connected_devices()

                # Check for newly connected devices
                new_devices = current_devices - self._last_devices

                # If target device connected, trigger callback
                if self.target_vendor_id and self.target_product_id:
                    target = (self.target_vendor_id, self.target_product_id)
                    if target in new_devices and self.on_connect:
                        _log(f"[USB Monitor] Device connected: {self.target_vendor_id}:{self.target_product_id} - triggering callback")
                        self.on_connect(self.target_vendor_id, self.target_product_id)

                self._last_devices = current_devices

                # Check every 2 seconds
                time.sleep(2)

            except Exception as e:
                # Continue monitoring even if there's an error
                _log(f"[USB Monitor] Error in monitoring loop: {e}")
                time.sleep(2)


class MacOSUSBMonitor(USBMonitor):
    """USB monitoring implementation for macOS using system_profiler."""

    def _get_connected_devices(self) -> set[tuple[str, str]]:
        """
        Get all currently connected USB devices on macOS.

        Returns:
            Set of (vendor_id, product_id) tuples
        """
        devices: set[tuple[str, str]] = set()
        try:
            result = subprocess.run(
                ["system_profiler", "SPUSBDataType"],
                capture_output=True,
                text=True,
                timeout=5
            )

            current_vendor = None
            current_product = None

            for line in result.stdout.split('\n'):
                line = line.strip()
                if 'Vendor ID:' in line:
                    # Extract vendor ID like "0x05e3"
                    parts = line.split('Vendor ID:')[1].strip()
                    vendor_id = parts.split()[0]
                    current_vendor = vendor_id
                elif 'Product ID:' in line:
                    # Extract product ID like "0x0610"
                    parts = line.split('Product ID:')[1].strip()
                    product_id = parts.split()[0]
                    current_product = product_id

                    # Add device when we have both IDs
                    if current_vendor and current_product:
                        devices.add((current_vendor, current_product))
                        current_vendor = None
                        current_product = None

        except Exception:
            pass  # Silently fail, will retry next cycle

        return devices

    def get_all_usb_devices(self) -> list[dict[str, str]]:
        """
        Get a list of all currently connected USB devices on macOS.

        Returns:
            List of dicts with 'vendor_id', 'product_id', and 'name'
        """
        devices: list[dict[str, str]] = []
        try:
            result = subprocess.run(
                ["system_profiler", "SPUSBDataType"],
                capture_output=True,
                text=True,
                timeout=5
            )

            current_vendor = None
            current_product = None
            current_name = None

            for line in result.stdout.split('\n'):
                stripped = line.strip()

                # Look for device name (not indented lines that end with colon)
                if ':' in line and not stripped.startswith('Product ID') and not stripped.startswith('Vendor ID'):
                    # This might be a device name
                    potential_name = stripped.rstrip(':')
                    if potential_name and len(potential_name) < 100:
                        current_name = potential_name

                if 'Vendor ID:' in stripped:
                    parts = stripped.split('Vendor ID:')[1].strip()
                    vendor_id = parts.split()[0]
                    current_vendor = vendor_id

                elif 'Product ID:' in stripped:
                    parts = stripped.split('Product ID:')[1].strip()
                    product_id = parts.split()[0]
                    current_product = product_id

                    if current_vendor and current_product:
                        devices.append({
                            'vendor_id': current_vendor,
                            'product_id': current_product,
                            'name': current_name or 'Unknown Device'
                        })
                        current_vendor = None
                        current_product = None
                        current_name = None

        except Exception:
            pass

        return devices


class WindowsUSBMonitor(USBMonitor):
    """USB monitoring implementation for Windows using WMI."""

    def _get_connected_devices(self) -> set[tuple[str, str]]:
        """
        Get all currently connected USB devices on Windows using WMI.

        Returns:
            Set of (vendor_id, product_id) tuples
        """
        devices: set[tuple[str, str]] = set()
        try:
            import wmi
            c = wmi.WMI()
            for usb in c.Win32_PnPEntity():
                if usb.DeviceID and 'USB\\VID_' in usb.DeviceID:
                    # Parse DeviceID like "USB\VID_1E7D&PID_2C92\..."
                    device_id = usb.DeviceID
                    if 'VID_' in device_id and 'PID_' in device_id:
                        # Extract VID and PID
                        vid_start = device_id.index('VID_') + 4
                        vid_end = vid_start + 4
                        pid_start = device_id.index('PID_') + 4
                        pid_end = pid_start + 4

                        vendor_id = f"0x{device_id[vid_start:vid_end].lower()}"
                        product_id = f"0x{device_id[pid_start:pid_end].lower()}"
                        devices.add((vendor_id, product_id))

        except Exception:
            pass  # Silently fail, will retry next cycle

        return devices

    def get_all_usb_devices(self) -> list[dict[str, str]]:
        """
        Get a list of all currently connected USB devices on Windows.

        Returns:
            List of dicts with 'vendor_id', 'product_id', and 'name'
        """
        devices: list[dict[str, str]] = []
        try:
            import wmi
            c = wmi.WMI()
            for usb in c.Win32_PnPEntity():
                if usb.DeviceID and 'USB\\VID_' in usb.DeviceID:
                    device_id = usb.DeviceID
                    if 'VID_' in device_id and 'PID_' in device_id:
                        # Extract VID and PID
                        vid_start = device_id.index('VID_') + 4
                        vid_end = vid_start + 4
                        pid_start = device_id.index('PID_') + 4
                        pid_end = pid_start + 4

                        vendor_id = f"0x{device_id[vid_start:vid_end].lower()}"
                        product_id = f"0x{device_id[pid_start:pid_end].lower()}"

                        # Get device name
                        name = usb.Name if usb.Name else 'Unknown Device'

                        devices.append({
                            'vendor_id': vendor_id,
                            'product_id': product_id,
                            'name': name
                        })

        except Exception:
            pass

        return devices


def create_usb_monitor(on_connect: Optional[Callable[[str, str], None]] = None) -> USBMonitor:
    """
    Factory function to create the appropriate USB monitor for the current platform.

    Args:
        on_connect: Optional callback function called when monitored device connects

    Returns:
        USBMonitor instance appropriate for the current platform

    Raises:
        RuntimeError: If platform is not supported
    """
    platform = get_platform()

    if platform == Platform.MACOS:
        return MacOSUSBMonitor(on_connect=on_connect)
    elif platform == Platform.WINDOWS:
        return WindowsUSBMonitor(on_connect=on_connect)
    elif platform == Platform.LINUX:
        # Linux can use similar approach to macOS or Windows depending on what's available
        # For now, try macOS-style first (many Linux distros have similar tools)
        return MacOSUSBMonitor(on_connect=on_connect)
    else:
        raise RuntimeError(f"Unsupported platform: {platform.value}. Supported platforms: macOS, Windows, Linux")
