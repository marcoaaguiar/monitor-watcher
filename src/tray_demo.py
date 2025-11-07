"""Demo/test version of the tray app using MockDisplayController.

This version is safe to run as it won't affect your actual monitors.
It will show you the menu structure and test all the functionality.
"""

import rumps

from constants import INPUT_MAP, DEFAULT_CONFIG_PATH
from controllers import MockDisplayController, DisplayController
from profile_manager import ProfileManager


class MonitorWatcherDemoApp(rumps.App):
    """Demo menu bar application for monitor control (uses mock controller)."""

    def __init__(self) -> None:
        """Initialize the demo menu bar app."""
        super().__init__(
            name="M (DEMO)",
            icon=None,
            quit_button="Quit Demo"
        )

        # Use MockDisplayController instead of M1DDCController
        self.controller: DisplayController = MockDisplayController()
        self.manager = ProfileManager(DEFAULT_CONFIG_PATH)
        self.current_profile: str | None = None

        self._build_menu()

        # Show welcome notification
        rumps.notification(
            title="Monitor Watcher Demo",
            subtitle="Demo Mode Active",
            message="Using mock controller - won't affect real monitors"
        )

    def _build_menu(self) -> None:
        """Build the menu structure."""
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

        # Add utility items
        self.menu.add(rumps.MenuItem("Refresh Monitors", callback=self.refresh_monitors))
        self.menu.add(rumps.MenuItem("Open Config", callback=self.open_config))

    def _add_profiles_menu(self) -> None:
        """Add profiles submenu."""
        profiles = self.manager.list_profiles()

        if not profiles:
            item = rumps.MenuItem("No Profiles (Create in Terminal)")
            item.set_callback(None)
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
        """Create a submenu for a specific display."""
        display_menu = rumps.MenuItem(f"Display {display_num}")

        for input_name, input_code in INPUT_MAP.items():
            item = rumps.MenuItem(
                input_name.upper(),
                callback=self._create_input_callback(display_num, input_name, input_code)
            )
            display_menu.add(item)

        return display_menu

    def _create_profile_callback(self, profile_name: str):
        """Create a callback function for profile switching."""
        def callback(_sender: rumps.MenuItem) -> None:
            try:
                rumps.notification(
                    title="Monitor Watcher Demo",
                    subtitle="Switching Profile (Demo)",
                    message=f"Applying profile: {profile_name}"
                )

                self.manager.apply_profile(profile_name, self.controller, dry_run=True)
                self.current_profile = profile_name

                rumps.notification(
                    title="Monitor Watcher Demo",
                    subtitle="Success (Demo)",
                    message=f"Applied profile: {profile_name}"
                )

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
        """Create a callback function for input switching."""
        def callback(_sender: rumps.MenuItem) -> None:
            try:
                self.controller.set_input(display_num, input_code)

                rumps.notification(
                    title="Monitor Watcher Demo",
                    subtitle=f"Display {display_num} (Demo)",
                    message=f"Switched to {input_name.upper()}"
                )

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

    @rumps.clicked("Refresh Monitors")
    def refresh_monitors(self, _sender: rumps.MenuItem) -> None:
        """Refresh the menu by rebuilding it."""
        self._build_menu()
        rumps.notification(
            title="Monitor Watcher Demo",
            subtitle="Refreshed",
            message="Monitor list updated"
        )

    @rumps.clicked("Open Config")
    def open_config(self, _sender: rumps.MenuItem) -> None:
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

    @rumps.clicked("Create New...")
    def create_profile(self, _sender: rumps.MenuItem) -> None:
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


def run_demo() -> None:
    """Run the demo menu bar application."""
    print("="*60)
    print("Monitor Watcher - DEMO MODE")
    print("="*60)
    print("\nThis demo uses MockDisplayController and won't affect your")
    print("actual monitors. You can safely test all menu features.")
    print("\nLook for the 'Monitor Watcher (DEMO)' icon in your menu bar.")
    print("\nTo quit: Use Cmd+Q or select 'Quit Demo' from the menu.")
    print("="*60)
    print("\nStarting demo app...")

    app = MonitorWatcherDemoApp()
    app.run()


if __name__ == "__main__":
    run_demo()
