"""System tray menu bar application for monitor switching."""

import json
import sys
import traceback
from datetime import datetime
from pathlib import Path

import rumps

from constants import INPUT_MAP, DEFAULT_CONFIG_PATH, USB_CONFIG_PATH
from controllers import M1DDCController, DisplayController
from profile_manager import ProfileManager
from usb_monitor import create_usb_monitor

# Log file for tray app
LOG_FILE = Path.home() / ".config" / "monitor-watcher" / "tray_app.log"


def _log(message: str) -> None:
    """Write a timestamped log message."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {message}"
    print(log_message, file=sys.stderr)
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_FILE, "a") as f:
            f.write(log_message + "\n")
    except Exception:
        pass


class MonitorWatcherApp(rumps.App):
    """Menu bar application for monitor control."""

    def __init__(self) -> None:
        """Initialize the menu bar app."""
        super().__init__(
            name="M",
            icon=None,  # TODO: Add icon file or use text "M"
            quit_button="Quit"
        )

        self.controller: DisplayController = M1DDCController()
        self.manager = ProfileManager(DEFAULT_CONFIG_PATH)
        self.current_profile: str | None = None

        # USB monitoring
        self.usb_monitor = create_usb_monitor(on_connect=self._on_usb_connect)
        self.usb_config = self._load_usb_config()
        self.usb_monitoring_enabled = self.usb_config.get("enabled", False)

        # Flag for thread-safe menu rebuild
        self._needs_menu_rebuild = False

        # Start USB monitoring if enabled
        if self.usb_monitoring_enabled:
            vendor_id = self.usb_config.get("vendor_id")
            product_id = self.usb_config.get("product_id")
            if vendor_id and product_id:
                self.usb_monitor.set_target_device(vendor_id, product_id)
                self.usb_monitor.start_monitoring()

        self._build_menu()

        # Timer to check for pending menu rebuilds (runs on main thread)
        self._rebuild_timer = rumps.Timer(self._check_rebuild_menu, 1)
        self._rebuild_timer.start()

    def _check_rebuild_menu(self, _: rumps.Timer) -> None:
        """Check if menu needs rebuilding (called from main thread via timer)."""
        if self._needs_menu_rebuild:
            self._needs_menu_rebuild = False
            self._build_menu()

    def _build_menu(self) -> None:
        """Build the menu structure."""
        try:
            _log("Building menu...")
            # Clear existing menu items
            self.menu.clear()

            # Add profiles section
            self._add_profiles_menu()

            # Add separator
            self.menu.add(rumps.separator)

            # Add quick switch section
            self._add_quick_switch_menu()

            # Add separator
            self.menu.add(rumps.separator)

            # Add USB monitoring section
            self._add_usb_monitoring_menu()
        except Exception as e:
            _log(f"ERROR building menu: {e}")
            _log(traceback.format_exc())

        # Add separator
        self.menu.add(rumps.separator)

        # Add utility items
        self.menu.add(rumps.MenuItem("Refresh Monitors", callback=self.refresh_monitors))
        self.menu.add(rumps.MenuItem("Open Config", callback=self.open_config))

        # Add separator before quit
        self.menu.add(rumps.separator)

        # Re-add the Quit button (gets cleared by menu.clear())
        self.menu.add(rumps.MenuItem("Quit", callback=rumps.quit_application))

    def _add_profiles_menu(self) -> None:
        """Add profiles submenu."""
        profiles = self.manager.list_profiles()

        if not profiles:
            item = rumps.MenuItem("No Profiles (Create in Terminal)")
            item.set_callback(None)  # Disable the item
            self.menu.add(item)
            return

        profiles_menu = rumps.MenuItem("Profiles")

        for name, profile in profiles.items():
            description = profile.get("description", "")
            title = f"{name}" + (f" - {description}" if description else "")

            # Add checkmark if current profile
            if name == self.current_profile:
                title = f"✓ {title}"

            item = rumps.MenuItem(title, callback=self._create_profile_callback(name))
            profiles_menu.add(item)

        profiles_menu.add(rumps.separator)
        profiles_menu.add(rumps.MenuItem("Create New...", callback=self.create_profile))

        self.menu.add(profiles_menu)

    def _add_quick_switch_menu(self) -> None:
        """Add quick switch submenu for manual input switching."""
        quick_switch_menu = rumps.MenuItem("Quick Switch")

        try:
            # Get list of monitors
            monitors_output = self.controller.list_displays(detailed=False)

            # Parse monitor numbers from output
            import re
            monitor_pattern = r'\[(\d+)\]'
            available_displays = re.findall(monitor_pattern, monitors_output)

            if not available_displays:
                item = rumps.MenuItem("No Monitors Detected")
                item.set_callback(None)
                quick_switch_menu.add(item)
            else:
                for display_num in available_displays:
                    display_menu = self._create_display_menu(display_num)
                    quick_switch_menu.add(display_menu)

        except Exception as e:
            item = rumps.MenuItem(f"Error: {str(e)}")
            item.set_callback(None)
            quick_switch_menu.add(item)

        self.menu.add(quick_switch_menu)

    def _create_display_menu(self, display_num: str) -> rumps.MenuItem:
        """
        Create a submenu for a specific display.

        Args:
            display_num: Display number as string

        Returns:
            MenuItem with input options
        """
        display_menu = rumps.MenuItem(f"Display {display_num}")

        for input_name, input_code in INPUT_MAP.items():
            item = rumps.MenuItem(
                input_name.upper(),
                callback=self._create_input_callback(display_num, input_name, input_code)
            )
            display_menu.add(item)

        return display_menu

    def _add_usb_monitoring_menu(self) -> None:
        """Add USB monitoring menu items."""
        usb_menu = rumps.MenuItem("USB Auto-Switch")

        # Show current status
        if self.usb_monitoring_enabled and self.usb_config.get("device_name"):
            device = self.usb_config.get("device_name", "Unknown")
            profile = self.usb_config.get("profile", "Unknown")
            status_item = rumps.MenuItem(f"Monitoring: {device} → {profile}")
            status_item.set_callback(None)  # Disable clicking
            usb_menu.add(status_item)
            usb_menu.add(rumps.separator)

        # Toggle monitoring (with checkmark if enabled)
        toggle_item = rumps.MenuItem("Enable USB Monitoring", callback=self.toggle_usb_monitoring)
        if self.usb_monitoring_enabled:
            toggle_item.state = 1  # Checked
            toggle_item.title = "Disable USB Monitoring"
        usb_menu.add(toggle_item)

        # Configure option
        usb_menu.add(rumps.MenuItem("Configure Device...", callback=self.configure_usb))

        self.menu.add(usb_menu)

    def _create_profile_callback(self, profile_name: str):
        """
        Create a callback function for profile switching.

        Args:
            profile_name: Name of the profile to switch to

        Returns:
            Callback function
        """
        def callback(sender: rumps.MenuItem) -> None:
            try:
                # Try to show notification, but don't fail if it doesn't work
                try:
                    rumps.notification(
                        title="Monitor Watcher",
                        subtitle="Switching Profile",
                        message=f"Applying profile: {profile_name}"
                    )
                except Exception:
                    pass  # Notification failed, but continue

                self.manager.apply_profile(profile_name, self.controller, dry_run=False)
                self.current_profile = profile_name

                try:
                    rumps.notification(
                        title="Monitor Watcher",
                        subtitle="Success",
                        message=f"Applied profile: {profile_name}"
                    )
                except Exception:
                    pass  # Notification failed, but continue

                # Rebuild menu to update checkmarks
                self._build_menu()

            except Exception as e:
                rumps.alert(
                    title="Error Applying Profile",
                    message=str(e),
                    ok="OK"
                )

        return callback

    def _create_input_callback(self, display_num: str, input_name: str, input_code: int):
        """
        Create a callback function for input switching.

        Args:
            display_num: Display number
            input_name: Human-readable input name
            input_code: Input code for m1ddc

        Returns:
            Callback function
        """
        def callback(sender: rumps.MenuItem) -> None:
            try:
                self.controller.set_input(display_num, input_code)

                try:
                    rumps.notification(
                        title="Monitor Watcher",
                        subtitle=f"Display {display_num}",
                        message=f"Switched to {input_name.upper()}"
                    )
                except Exception:
                    pass  # Notification failed, but continue

                # Clear current profile since manual switch was made
                self.current_profile = None
                self._build_menu()

            except Exception as e:
                rumps.alert(
                    title="Error Switching Input",
                    message=str(e),
                    ok="OK"
                )

        return callback

    def refresh_monitors(self, sender: rumps.MenuItem) -> None:
        """Refresh the menu by rebuilding it."""
        self._build_menu()
        try:
            rumps.notification(
                title="Monitor Watcher",
                subtitle="Refreshed",
                message="Monitor list updated"
            )
        except Exception:
            pass  # Notification failed, but continue

    def open_config(self, sender: rumps.MenuItem) -> None:
        """Open the config file in default editor."""
        import subprocess
        try:
            subprocess.run(["open", str(DEFAULT_CONFIG_PATH)])
        except Exception as e:
            rumps.alert(
                title="Error Opening Config",
                message=str(e),
                ok="OK"
            )

    def create_profile(self, sender: rumps.MenuItem) -> None:
        """Launch the CLI wizard in a new terminal."""
        import subprocess
        import os

        # Get the directory of this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        main_py = os.path.join(script_dir, "main.py")

        # Open a new Terminal window and run the wizard
        script = f'''
        tell application "Terminal"
            do script "cd {script_dir} && uv run python {main_py} create-profile"
            activate
        end tell
        '''

        try:
            subprocess.run(["osascript", "-e", script])
        except Exception as e:
            rumps.alert(
                title="Error Launching Wizard",
                message=str(e),
                ok="OK"
            )

    def _load_usb_config(self) -> dict[str, str | bool]:
        """Load USB monitoring configuration."""
        if not USB_CONFIG_PATH.exists():
            return {"enabled": False}

        try:
            with open(USB_CONFIG_PATH, "r") as f:
                return json.load(f)
        except Exception:
            return {"enabled": False}

    def _save_usb_config(self) -> None:
        """Save USB monitoring configuration."""
        USB_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(USB_CONFIG_PATH, "w") as f:
                json.dump(self.usb_config, f, indent=2)
        except Exception:
            pass

    def _on_usb_connect(self, vendor_id: str, product_id: str) -> None:
        """
        Callback when monitored USB device connects.

        Args:
            vendor_id: USB vendor ID
            product_id: USB product ID
        """
        # Apply the configured profile
        profile_name = self.usb_config.get("profile", "work")

        try:
            self.manager.apply_profile(profile_name, self.controller, dry_run=False)
            self.current_profile = profile_name

            try:
                rumps.notification(
                    title="Monitor Watcher",
                    subtitle="USB Device Detected",
                    message=f"Auto-switched to '{profile_name}' profile"
                )
            except Exception:
                pass

            # Schedule menu rebuild on main thread (thread-safe)
            self._needs_menu_rebuild = True
        except Exception:
            pass  # Silently fail, don't interrupt monitoring

    def configure_usb(self, _sender: rumps.MenuItem) -> None:
        """Configure USB device monitoring."""
        try:
            # Get list of USB devices
            devices = self.usb_monitor.get_all_usb_devices()

            if not devices:
                rumps.alert(
                    title="No USB Devices",
                    message="No USB devices found",
                    ok="OK"
                )
                return

            # Create device selection dialog
            device_names = [f"{d['name']} ({d['vendor_id']}:{d['product_id']})" for d in devices]
            device_list = "\n".join(f"{i+1}. {name}" for i, name in enumerate(device_names))

            response = rumps.Window(
                message=f"Select USB device to monitor:\n\n{device_list}",
                title="USB Device Selection",
                default_text="1",
                ok="Select",
                cancel="Cancel",
                dimensions=(400, 200)
            ).run()

            if response.clicked:
                try:
                    index = int(response.text) - 1
                    if 0 <= index < len(devices):
                        device = devices[index]

                        # Ask for profile name
                        profiles = list(self.manager.list_profiles().keys())
                        profile_list = "\n".join(f"{i+1}. {name}" for i, name in enumerate(profiles))

                        profile_response = rumps.Window(
                            message=f"Select profile to auto-apply:\n\n{profile_list}",
                            title="Profile Selection",
                            default_text="1",
                            ok="Save",
                            cancel="Cancel"
                        ).run()

                        if profile_response.clicked:
                            profile_index = int(profile_response.text) - 1
                            if 0 <= profile_index < len(profiles):
                                profile_name = profiles[profile_index]

                                # Save configuration
                                self.usb_config = {
                                    "enabled": True,
                                    "vendor_id": device['vendor_id'],
                                    "product_id": device['product_id'],
                                    "device_name": device['name'],
                                    "profile": profile_name
                                }
                                self._save_usb_config()

                                # Start monitoring
                                self.usb_monitor.set_target_device(device['vendor_id'], device['product_id'])
                                self.usb_monitor.start_monitoring()
                                self.usb_monitoring_enabled = True

                                rumps.notification(
                                    title="USB Monitoring",
                                    subtitle="Configured",
                                    message=f"Monitoring {device['name']} → {profile_name}"
                                )

                                # Rebuild menu
                                self._build_menu()
                except (ValueError, IndexError):
                    rumps.alert(
                        title="Invalid Selection",
                        message="Please enter a valid number",
                        ok="OK"
                    )
        except Exception as e:
            print(f"ERROR in configure_usb: {e}")
            import traceback
            traceback.print_exc()
            rumps.alert(
                title="Configuration Error",
                message=f"An error occurred: {str(e)}",
                ok="OK"
            )

    def toggle_usb_monitoring(self, sender: rumps.MenuItem) -> None:
        """Toggle USB monitoring on/off."""
        self.usb_monitoring_enabled = not self.usb_monitoring_enabled
        self.usb_config["enabled"] = self.usb_monitoring_enabled
        self._save_usb_config()

        if self.usb_monitoring_enabled:
            vendor_id = self.usb_config.get("vendor_id")
            product_id = self.usb_config.get("product_id")
            if vendor_id and product_id:
                self.usb_monitor.set_target_device(vendor_id, product_id)
                self.usb_monitor.start_monitoring()
                sender.state = 1  # Checked
                try:
                    rumps.notification(
                        title="USB Monitoring",
                        subtitle="Enabled",
                        message="USB device monitoring is now active"
                    )
                except Exception:
                    pass
        else:
            self.usb_monitor.stop_monitoring()
            sender.state = 0  # Unchecked
            try:
                rumps.notification(
                    title="USB Monitoring",
                    subtitle="Disabled",
                    message="USB device monitoring is now inactive"
                )
            except Exception:
                pass


def run_app() -> None:
    """Run the menu bar application."""
    app = MonitorWatcherApp()
    app.run()
