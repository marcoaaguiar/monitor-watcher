"""CLI commands for the monitor switcher application."""

import sys
import re
import json
from pathlib import Path

import click

from constants import INPUT_MAP, DEFAULT_CONFIG_PATH, USB_CONFIG_PATH
from controllers import DisplayController, MockDisplayController, create_display_controller
from profile_manager import ProfileManager
from usb_monitor import create_usb_monitor


@click.group()
@click.version_option(version="0.1.0")
def cli() -> None:
    """Monitor Input Switcher - Control monitor inputs with profiles."""
    pass


@cli.command(name="list-monitors")
@click.option("--detailed", is_flag=True, help="Show detailed monitor information")
@click.option("--dry-run", is_flag=True, help="Use mock controller for testing")
def list_monitors(detailed: bool, dry_run: bool) -> None:
    """List all connected monitors."""
    controller: DisplayController = create_display_controller(dry_run=dry_run)
    output = controller.list_displays(detailed=detailed)
    click.echo(output)


@cli.command(name="list-profiles")
@click.option(
    "--config",
    type=click.Path(path_type=Path),
    default=DEFAULT_CONFIG_PATH,
    help="Path to profiles config file"
)
def list_profiles(config: Path) -> None:
    """List all available profiles."""
    manager = ProfileManager(config)
    profiles = manager.list_profiles()

    if not profiles:
        click.echo("No profiles found. Create a profile in the config file:")
        click.echo(f"  {config}")
        return

    click.echo("Available profiles:\n")
    for name, profile in profiles.items():
        click.echo(f"  [{name}]")
        if description := profile.get("description"):
            click.echo(f"    Description: {description}")
        monitors = profile.get("monitors", {})
        if monitors:
            click.echo("    Monitors:")
            for display_num, input_name in monitors.items():
                click.echo(f"      Display {display_num} → {input_name.upper()}")
        click.echo()


@cli.command(name="apply-profile")
@click.argument("profile_name")
@click.option(
    "--config",
    type=click.Path(path_type=Path),
    default=DEFAULT_CONFIG_PATH,
    help="Path to profiles config file"
)
@click.option("--dry-run", is_flag=True, help="Show what would be done without executing")
def apply_profile(profile_name: str, config: Path, dry_run: bool) -> None:
    """Apply a profile to configure monitor inputs."""
    controller: DisplayController = create_display_controller(dry_run=dry_run)
    manager = ProfileManager(config)
    manager.apply_profile(profile_name, controller, dry_run)


@cli.command(name="show-config")
@click.option(
    "--config",
    type=click.Path(path_type=Path),
    default=DEFAULT_CONFIG_PATH,
    help="Path to profiles config file"
)
def show_config(config: Path) -> None:
    """Show the current configuration file."""
    if not config.exists():
        click.echo(f"Config file not found: {config}")
        click.echo("Run any command to create a default config file.")
        return

    click.echo(f"Config file: {config}\n")
    with open(config, "r") as f:
        click.echo(f.read())


@cli.command(name="switch")
@click.argument("display")
@click.argument("input_name")
@click.option("--dry-run", is_flag=True, help="Show what would be done without executing")
def switch_input(display: str, input_name: str, dry_run: bool) -> None:
    """
    Manually switch a display to a specific input.

    DISPLAY: Display number (e.g., 1, 2)
    INPUT_NAME: Input name (hdmi1, hdmi2, dp1, dp2, usbc)
    """
    input_name_lower = input_name.lower()
    if input_name_lower not in INPUT_MAP:
        click.echo(f"Error: Invalid input '{input_name}'", err=True)
        click.echo(f"Available inputs: {', '.join(INPUT_MAP.keys())}")
        sys.exit(1)

    controller: DisplayController = create_display_controller(dry_run=dry_run)
    input_code = INPUT_MAP[input_name_lower]
    click.echo(f"Switching Display {display} to {input_name.upper()} (code {input_code})...")
    controller.set_input(display, input_code)

    if dry_run and isinstance(controller, MockDisplayController):
        click.echo("\n" + controller.get_state_summary())

    click.echo("✓ Done!")


@cli.command(name="create-profile")
@click.option(
    "--config",
    type=click.Path(path_type=Path),
    default=DEFAULT_CONFIG_PATH,
    help="Path to profiles config file"
)
def create_profile_wizard(config: Path) -> None:
    """Interactive wizard to create a new monitor profile."""
    manager = ProfileManager(config)
    controller = create_display_controller()

    click.echo("=== Monitor Profile Creation Wizard ===\n")

    # Step 1: Get profile name
    profile_name = click.prompt("Enter profile name (e.g., 'work', 'gaming', 'personal')", type=str)
    profile_name = profile_name.strip()

    # Check if profile already exists
    if manager.get_profile(profile_name):
        if not click.confirm(f"Profile '{profile_name}' already exists. Overwrite?", default=False):
            click.echo("Cancelled.")
            return

    # Step 2: Get description
    description = click.prompt("Enter profile description", type=str, default="")

    # Step 3: Show available monitors
    click.echo("\n--- Available Monitors ---")
    monitors_output = controller.list_displays(detailed=False)
    click.echo(monitors_output)

    # Step 4: Configure monitors
    click.echo("\n--- Configure Monitor Inputs ---")
    click.echo(f"Available inputs: {', '.join(INPUT_MAP.keys())}")
    click.echo("Press Enter to skip a monitor.\n")

    monitor_configs: dict[str, str] = {}

    # Parse available monitors from output
    monitor_pattern = r'\[(\d+)\]'
    available_displays = re.findall(monitor_pattern, monitors_output)

    for display_num in available_displays:
        input_name = click.prompt(
            f"Input for Display {display_num}",
            type=click.Choice(list(INPUT_MAP.keys()) + [""]),
            default="",
            show_choices=True,
            show_default=False
        )

        if input_name:
            monitor_configs[display_num] = input_name

    if not monitor_configs:
        click.echo("Error: No monitors configured. Profile creation cancelled.", err=True)
        return

    # Step 5: Show summary and confirm
    click.echo("\n--- Profile Summary ---")
    click.echo(f"Name: {profile_name}")
    click.echo(f"Description: {description}")
    click.echo("Monitors:")
    for display, input_name in monitor_configs.items():
        click.echo(f"  Display {display} → {input_name.upper()}")

    if click.confirm("\nSave this profile?", default=True):
        manager.save_profile(profile_name, description, monitor_configs)
        click.echo(f"✓ Profile '{profile_name}' saved successfully!")
        click.echo(f"Config saved to: {config}")
    else:
        click.echo("Cancelled.")


@cli.command(name="delete-profile")
@click.argument("profile_name")
@click.option(
    "--config",
    type=click.Path(path_type=Path),
    default=DEFAULT_CONFIG_PATH,
    help="Path to profiles config file"
)
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompt")
def delete_profile(profile_name: str, config: Path, yes: bool) -> None:
    """Delete a profile from the configuration."""
    manager = ProfileManager(config)

    # Check if profile exists
    if not manager.get_profile(profile_name):
        click.echo(f"Error: Profile '{profile_name}' not found", err=True)
        sys.exit(1)

    # Confirm deletion
    if not yes:
        if not click.confirm(f"Delete profile '{profile_name}'?", default=False):
            click.echo("Cancelled.")
            return

    manager.delete_profile(profile_name)
    click.echo(f"✓ Profile '{profile_name}' deleted successfully!")


@cli.command(name="list-usb-devices")
def list_usb_devices() -> None:
    """List all connected USB devices."""
    monitor = create_usb_monitor()
    devices = monitor.get_all_usb_devices()

    if not devices:
        click.echo("No USB devices found")
        return

    click.echo("Connected USB devices:\n")
    for i, device in enumerate(devices, 1):
        click.echo(f"  {i}. {device['name']}")
        click.echo(f"     Vendor ID:  {device['vendor_id']}")
        click.echo(f"     Product ID: {device['product_id']}")
        click.echo()


@cli.command(name="configure-usb")
@click.option(
    "--config",
    type=click.Path(path_type=Path),
    default=DEFAULT_CONFIG_PATH,
    help="Path to profiles config file"
)
def configure_usb(config: Path) -> None:
    """Configure USB device monitoring for automatic profile switching."""
    manager = ProfileManager(config)
    monitor = create_usb_monitor()

    # Get list of USB devices
    devices = monitor.get_all_usb_devices()

    if not devices:
        click.echo("Error: No USB devices found", err=True)
        sys.exit(1)

    # Display devices
    click.echo("Connected USB devices:\n")
    for i, device in enumerate(devices, 1):
        click.echo(f"  {i}. {device['name']} ({device['vendor_id']}:{device['product_id']})")

    # Get user selection
    click.echo()
    device_idx = click.prompt("Select device number", type=int) - 1

    if device_idx < 0 or device_idx >= len(devices):
        click.echo("Error: Invalid device number", err=True)
        sys.exit(1)

    selected_device = devices[device_idx]

    # Get list of profiles
    profiles = list(manager.list_profiles().keys())

    if not profiles:
        click.echo("\nError: No profiles found. Create a profile first.", err=True)
        sys.exit(1)

    click.echo("\nAvailable profiles:\n")
    for i, profile in enumerate(profiles, 1):
        click.echo(f"  {i}. {profile}")

    # Get profile selection
    click.echo()
    profile_idx = click.prompt("Select profile number to auto-apply", type=int) - 1

    if profile_idx < 0 or profile_idx >= len(profiles):
        click.echo("Error: Invalid profile number", err=True)
        sys.exit(1)

    selected_profile = profiles[profile_idx]

    # Save configuration
    usb_config = {
        "enabled": True,
        "vendor_id": selected_device['vendor_id'],
        "product_id": selected_device['product_id'],
        "device_name": selected_device['name'],
        "profile": selected_profile
    }

    USB_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(USB_CONFIG_PATH, "w") as f:
        json.dump(usb_config, f, indent=2)

    click.echo(f"\n✓ USB monitoring configured!")
    click.echo(f"  Device:  {selected_device['name']}")
    click.echo(f"  Profile: {selected_profile}")
    click.echo(f"  Config:  {USB_CONFIG_PATH}")
    click.echo("\nMonitoring is now enabled. Restart the tray app for changes to take effect.")


@cli.command(name="show-usb-config")
def show_usb_config() -> None:
    """Show current USB monitoring configuration."""
    if not USB_CONFIG_PATH.exists():
        click.echo("No USB monitoring configuration found")
        click.echo(f"Config would be at: {USB_CONFIG_PATH}")
        return

    try:
        with open(USB_CONFIG_PATH, "r") as f:
            config = json.load(f)

        click.echo("USB Monitoring Configuration:\n")
        click.echo(f"  Status:      {'Enabled' if config.get('enabled', False) else 'Disabled'}")
        click.echo(f"  Device:      {config.get('device_name', 'Unknown')}")
        click.echo(f"  Vendor ID:   {config.get('vendor_id', 'Unknown')}")
        click.echo(f"  Product ID:  {config.get('product_id', 'Unknown')}")
        click.echo(f"  Profile:     {config.get('profile', 'Unknown')}")
        click.echo(f"\n  Config file: {USB_CONFIG_PATH}")
    except Exception as e:
        click.echo(f"Error reading config: {e}", err=True)
        sys.exit(1)


@cli.command(name="toggle-usb-monitoring")
@click.argument("enabled", type=click.Choice(["on", "off"]))
def toggle_usb_monitoring(enabled: str) -> None:
    """Enable or disable USB monitoring."""
    if not USB_CONFIG_PATH.exists():
        click.echo("Error: No USB monitoring configuration found", err=True)
        click.echo("Run 'configure-usb' first to set up USB monitoring", err=True)
        sys.exit(1)

    try:
        with open(USB_CONFIG_PATH, "r") as f:
            config = json.load(f)

        config["enabled"] = (enabled == "on")

        with open(USB_CONFIG_PATH, "w") as f:
            json.dump(config, f, indent=2)

        status = "enabled" if enabled == "on" else "disabled"
        click.echo(f"✓ USB monitoring {status}")
        click.echo("\nRestart the tray app for changes to take effect.")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command(name="tray")
def tray() -> None:
    """Launch the menu bar/system tray application."""
    from platform_utils import is_macos

    if is_macos():
        # macOS: Use rumps-based menu bar app
        try:
            from tray_app import MonitorWatcherApp
            app = MonitorWatcherApp()
            app.run()
        except ImportError:
            click.echo("Error: Tray app dependencies not installed.", err=True)
            click.echo("Install with: uv sync --extra macos", err=True)
            sys.exit(1)
    else:
        # Windows/Linux: pystray-based system tray (coming soon)
        click.echo("Error: System tray support is currently macOS-only.", err=True)
        click.echo("Windows/Linux system tray support coming soon with pystray.", err=True)
        click.echo("\nFor now, you can use the CLI commands:", err=True)
        click.echo("  uv run python run_cli.py list-profiles", err=True)
        click.echo("  uv run python run_cli.py apply-profile <name>", err=True)
        sys.exit(1)
