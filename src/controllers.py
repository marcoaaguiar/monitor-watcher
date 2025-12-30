"""Display controller classes for managing monitor inputs."""

import sys
import subprocess
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

import click

from constants import INPUT_MAP
from platform_utils import Platform, get_platform

if TYPE_CHECKING:
    from monitorcontrol import Monitor


class DisplayController(ABC):
    """Abstract base class for display controllers."""

    @abstractmethod
    def list_displays(self, detailed: bool = False) -> str:
        """List all available displays."""
        pass

    @abstractmethod
    def get_input(self, display: str | int) -> int | None:
        """Get the current input source for a specific display."""
        pass

    @abstractmethod
    def set_input(self, display: str | int, input_code: int) -> None:
        """Set the input source for a specific display."""
        pass

    @abstractmethod
    def set_luminance(self, display: str | int, value: int) -> None:
        """Set the brightness/luminance for a specific display."""
        pass

    @abstractmethod
    def get_luminance(self, display: str | int) -> str:
        """Get the current brightness/luminance for a specific display."""
        pass


class M1DDCController(DisplayController):
    """Wrapper for m1ddc command-line tool to control external displays."""

    def __init__(self) -> None:
        """Initialize the M1DDC controller."""
        self._check_availability()

    def _check_availability(self) -> None:
        """Check if m1ddc is installed and available."""
        try:
            subprocess.run(
                ["m1ddc", "--help"],
                capture_output=True,
                check=True,
                timeout=5
            )
        except FileNotFoundError:
            click.echo("Error: m1ddc not found. Please install it with: brew install m1ddc", err=True)
            sys.exit(1)
        except subprocess.TimeoutExpired:
            click.echo("Error: m1ddc timed out", err=True)
            sys.exit(1)

    def _run_command(self, args: list[str]) -> str:
        """
        Run m1ddc command and return output.

        Args:
            args: Command arguments to pass to m1ddc

        Returns:
            Command output as string

        Raises:
            RuntimeError: If command fails
        """
        try:
            result = subprocess.run(
                ["m1ddc"] + args,
                capture_output=True,
                text=True,
                check=True,
                timeout=10
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            # Build detailed error message
            error_parts = [f"m1ddc command failed (exit code {e.returncode})"]
            if e.stderr:
                error_parts.append(f"stderr: {e.stderr.strip()}")
            if e.stdout:
                error_parts.append(f"stdout: {e.stdout.strip()}")
            error_parts.append(f"command: m1ddc {' '.join(args)}")

            error_msg = "\n".join(error_parts)

            # When running from CLI, print and exit
            # When running from tray app, raise exception so it can be caught
            if sys.stdout.isatty():
                click.echo(f"Error: {error_msg}", err=True)
                sys.exit(1)
            else:
                raise RuntimeError(error_msg)
        except subprocess.TimeoutExpired:
            error_msg = f"m1ddc command timed out after 10 seconds\ncommand: m1ddc {' '.join(args)}"
            if sys.stdout.isatty():
                click.echo(f"Error: {error_msg}", err=True)
                sys.exit(1)
            else:
                raise RuntimeError(error_msg)

    def list_displays(self, detailed: bool = False) -> str:
        """
        List all available displays.

        Args:
            detailed: Whether to include detailed information

        Returns:
            Display list as string
        """
        args = ["display", "list"]
        if detailed:
            args.append("detailed")
        return self._run_command(args)

    def get_input(self, display: str | int) -> int | None:
        """
        Get the current input source for a specific display.

        Args:
            display: Display number or identifier

        Returns:
            Current input code or None if unable to determine
        """
        try:
            result = self._run_command([
                "display",
                str(display),
                "get",
                "input"
            ])
            return int(result.strip())
        except (ValueError, RuntimeError):
            # If we can't get the input, return None
            return None

    def set_input(self, display: str | int, input_code: int) -> None:
        """
        Set the input source for a specific display.

        Args:
            display: Display number (1, 2, etc.) or identifier
            input_code: Input source code (e.g., 15 for DP1, 17 for HDMI1)
        """
        self._run_command([
            "display",
            str(display),
            "set",
            "input",
            str(input_code)
        ])

    def set_luminance(self, display: str | int, value: int) -> None:
        """
        Set the brightness/luminance for a specific display.

        Args:
            display: Display number or identifier
            value: Brightness value (0-100)
        """
        self._run_command([
            "display",
            str(display),
            "set",
            "luminance",
            str(value)
        ])

    def get_luminance(self, display: str | int) -> str:
        """
        Get the current brightness/luminance for a specific display.

        Args:
            display: Display number or identifier

        Returns:
            Current luminance value
        """
        return self._run_command([
            "display",
            str(display),
            "get",
            "luminance"
        ])


class MockDisplayController(DisplayController):
    """Mock display controller for testing without affecting actual monitors."""

    def __init__(self) -> None:
        """Initialize the mock controller."""
        self.display_states: dict[str, int] = {}
        self.luminance_states: dict[str, int] = {}
        click.echo("🧪 [DRY RUN MODE] Mock controller initialized")

    def list_displays(self, detailed: bool = False) -> str:
        """
        Mock list of displays.

        Args:
            detailed: Whether to include detailed information

        Returns:
            Mock display list as string
        """
        if detailed:
            return """[1] DELL S2721DGF (Mock)
 - Product name:  DELL S2721DGF (Mock)
 - Manufacturer:  DEL
 - Display ID:    1
[2] DELL P2723DE (Mock)
 - Product name:  DELL P2723DE (Mock)
 - Manufacturer:  DEL
 - Display ID:    2
[3] Generic Monitor (Mock)
 - Product name:  Generic Monitor
 - Display ID:    3"""
        else:
            return """[1] DELL S2721DGF (Mock)
[2] DELL P2723DE (Mock)
[3] Generic Monitor (Mock)"""

    def get_input(self, display: str | int) -> int | None:
        """
        Mock getting current input source.

        Args:
            display: Display number

        Returns:
            Current input code or None if not set
        """
        display_str = str(display)
        current = self.display_states.get(display_str)
        if current:
            input_name = self._get_input_name(current)
            click.echo(f"🧪 [DRY RUN] Display {display} current input: {current} ({input_name})")
        return current

    def set_input(self, display: str | int, input_code: int) -> None:
        """
        Mock setting input source.

        Args:
            display: Display number
            input_code: Input source code
        """
        display_str = str(display)
        self.display_states[display_str] = input_code
        input_name = self._get_input_name(input_code)
        click.echo(f"🧪 [DRY RUN] Would set Display {display} to input {input_code} ({input_name})")

    def set_luminance(self, display: str | int, value: int) -> None:
        """
        Mock setting luminance.

        Args:
            display: Display number
            value: Brightness value
        """
        display_str = str(display)
        self.luminance_states[display_str] = value
        click.echo(f"🧪 [DRY RUN] Would set Display {display} luminance to {value}")

    def get_luminance(self, display: str | int) -> str:
        """
        Mock getting luminance.

        Args:
            display: Display number

        Returns:
            Mock luminance value
        """
        display_str = str(display)
        value = self.luminance_states.get(display_str, 50)
        click.echo(f"🧪 [DRY RUN] Would get Display {display} luminance: {value}")
        return str(value)

    def _get_input_name(self, code: int) -> str:
        """
        Get input name from code.

        Args:
            code: Input code

        Returns:
            Input name
        """
        for name, val in INPUT_MAP.items():
            if val == code:
                return name.upper()
        return "UNKNOWN"

    def get_state_summary(self) -> str:
        """
        Get a summary of all state changes made during dry run.

        Returns:
            Summary string
        """
        if not self.display_states:
            return "No display state changes recorded"

        lines = ["Display State Changes:"]
        for display, input_code in self.display_states.items():
            input_name = self._get_input_name(input_code)
            lines.append(f"  Display {display}: {input_name} (code {input_code})")

        if self.luminance_states:
            lines.append("\nLuminance Changes:")
            for display, value in self.luminance_states.items():
                lines.append(f"  Display {display}: {value}")

        return "\n".join(lines)


class WindowsDisplayController(DisplayController):
    """Display controller for Windows using monitorcontrol library."""

    def __init__(self) -> None:
        """Initialize the Windows controller."""
        try:
            from monitorcontrol import get_monitors
            self._get_monitors = get_monitors
            self._monitors_cache: list[Monitor] = []
            self._refresh_monitors()
        except ImportError:
            click.echo("Error: monitorcontrol not found. Please install it with: pip install monitorcontrol", err=True)
            sys.exit(1)

    def _refresh_monitors(self) -> None:
        """Refresh the list of available monitors."""
        self._monitors_cache = list(self._get_monitors())

    def _get_monitor_by_index(self, display: str | int) -> "Monitor":
        """
        Get monitor object by display index.

        Args:
            display: Display number (1-indexed like m1ddc)

        Returns:
            Monitor object

        Raises:
            RuntimeError: If display not found
        """
        display_idx = int(display) - 1  # Convert to 0-indexed
        if display_idx < 0 or display_idx >= len(self._monitors_cache):
            raise RuntimeError(f"Display {display} not found. Valid displays: 1-{len(self._monitors_cache)}")
        return self._monitors_cache[display_idx]

    def list_displays(self, detailed: bool = False) -> str:
        """
        List all available displays.

        Args:
            detailed: Whether to include detailed information

        Returns:
            Display list as string
        """
        self._refresh_monitors()
        lines = []

        for idx, monitor in enumerate(self._monitors_cache, start=1):
            with monitor:
                # Get basic info
                manufacturer = getattr(monitor, 'manufacturer', 'Unknown')
                model = getattr(monitor, 'model', 'Unknown')

                if detailed:
                    lines.append(f"[{idx}] {manufacturer} {model}")
                    lines.append(f" - Product name:  {manufacturer} {model}")
                    lines.append(f" - Manufacturer:  {manufacturer}")
                    lines.append(f" - Display ID:    {idx}")
                else:
                    lines.append(f"[{idx}] {manufacturer} {model}")

        return "\n".join(lines) if lines else "No displays found"

    def get_input(self, display: str | int) -> int | None:
        """
        Get the current input source for a specific display.

        Args:
            display: Display number

        Returns:
            Current input code or None if unable to determine
        """
        try:
            monitor = self._get_monitor_by_index(display)
            with monitor:
                # Get VCP code 0x60 (input source)
                from monitorcontrol import vcp
                current_input = monitor.get_vcp_feature(vcp.VCPCode.INPUT_SOURCE)
                return current_input
        except Exception:
            # If we can't get the input, return None
            return None

    def set_input(self, display: str | int, input_code: int) -> None:
        """
        Set the input source for a specific display.

        Args:
            display: Display number (1, 2, etc.)
            input_code: Input source code (e.g., 15 for DP1, 17 for HDMI1)
        """
        monitor = self._get_monitor_by_index(display)
        with monitor:
            from monitorcontrol import vcp
            monitor.set_vcp_feature(vcp.VCPCode.INPUT_SOURCE, input_code)

    def set_luminance(self, display: str | int, value: int) -> None:
        """
        Set the brightness/luminance for a specific display.

        Args:
            display: Display number
            value: Brightness value (0-100)
        """
        monitor = self._get_monitor_by_index(display)
        with monitor:
            from monitorcontrol import vcp
            monitor.set_vcp_feature(vcp.VCPCode.BRIGHTNESS, value)

    def get_luminance(self, display: str | int) -> str:
        """
        Get the current brightness/luminance for a specific display.

        Args:
            display: Display number

        Returns:
            Current luminance value as string
        """
        monitor = self._get_monitor_by_index(display)
        with monitor:
            from monitorcontrol import vcp
            brightness = monitor.get_vcp_feature(vcp.VCPCode.BRIGHTNESS)
            return str(brightness)


def create_display_controller(dry_run: bool = False) -> DisplayController:
    """
    Factory function to create the appropriate display controller for the current platform.

    Args:
        dry_run: If True, create a mock controller for testing

    Returns:
        DisplayController instance appropriate for the current platform

    Raises:
        RuntimeError: If platform is not supported
    """
    if dry_run:
        return MockDisplayController()

    platform = get_platform()

    if platform == Platform.MACOS:
        return M1DDCController()
    elif platform == Platform.WINDOWS:
        return WindowsDisplayController()
    elif platform == Platform.LINUX:
        # Linux can use the Windows controller (monitorcontrol supports Linux)
        return WindowsDisplayController()
    else:
        raise RuntimeError(f"Unsupported platform: {platform.value}. Supported platforms: macOS, Windows, Linux")
