"""USB device monitoring for automatic profile switching."""

import threading
import time
from typing import Callable, Optional
import subprocess
from pathlib import Path
from datetime import datetime


# Log file for USB monitoring
LOG_FILE = Path.home() / ".config" / "monitor-watcher" / "usb_monitor.log"


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


class USBMonitor:
    """Monitor USB devices and trigger callbacks on connection/disconnection."""

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

    def _get_connected_devices(self) -> set[tuple[str, str]]:
        """
        Get all currently connected USB devices.

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

    def get_all_usb_devices(self) -> list[dict[str, str]]:
        """
        Get a list of all currently connected USB devices.

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
