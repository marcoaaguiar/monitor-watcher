"""Display controller classes for managing monitor inputs."""

import sys
import subprocess
from abc import ABC, abstractmethod

import click

from constants import INPUT_MAP


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
