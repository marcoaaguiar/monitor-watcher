"""Profile management for monitor configurations."""

import sys
import json
from pathlib import Path
from typing import Any

import click

from constants import INPUT_MAP, DEFAULT_CONFIG_PATH
from controllers import DisplayController, MockDisplayController


class ProfileManager:
    """Manages monitor profiles from JSON configuration."""

    def __init__(self, config_path: Path = DEFAULT_CONFIG_PATH) -> None:
        """
        Initialize the profile manager.

        Args:
            config_path: Path to the profiles JSON file
        """
        self.config_path = config_path
        self.profiles: dict[str, dict[str, Any]] = {}
        self._load_profiles()

    def _load_profiles(self) -> None:
        """Load profiles from the JSON configuration file."""
        if not self.config_path.exists():
            self._create_default_config()
            return

        try:
            with open(self.config_path, "r") as f:
                data = json.load(f)
                self.profiles = data.get("profiles", {})
        except json.JSONDecodeError as e:
            click.echo(f"Error parsing config file: {e}", err=True)
            sys.exit(1)
        except Exception as e:
            click.echo(f"Error loading config: {e}", err=True)
            sys.exit(1)

    def _create_default_config(self) -> None:
        """Create a default configuration file with example profiles."""
        default_config: dict[str, dict[str, Any]] = {"profiles": {}}

        # Create config directory if it doesn't exist
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.config_path, "w") as f:
            json.dump(default_config, f, indent=2)

        self.profiles = default_config["profiles"]
        click.echo(f"Created default config at: {self.config_path}")

    def get_profile(self, name: str) -> dict[str, Any] | None:
        """
        Get a profile by name.

        Args:
            name: Profile name

        Returns:
            Profile configuration or None if not found
        """
        return self.profiles.get(name)

    def list_profiles(self) -> dict[str, dict[str, Any]]:
        """
        Get all profiles.

        Returns:
            Dictionary of all profiles
        """
        return self.profiles

    def save_profile(
        self, name: str, description: str, monitors: dict[str, str]
    ) -> None:
        """
        Save a new profile to the configuration file.

        Args:
            name: Profile name
            description: Profile description
            monitors: Dictionary of display number to input name

        Raises:
            SystemExit: If save fails
        """
        # Add to in-memory profiles
        self.profiles[name] = {"description": description, "monitors": monitors}

        # Save to file
        config_data = {"profiles": self.profiles}
        try:
            with open(self.config_path, "w") as f:
                json.dump(config_data, f, indent=2)
        except Exception as e:
            click.echo(f"Error saving config: {e}", err=True)
            sys.exit(1)

    def delete_profile(self, name: str) -> None:
        """
        Delete a profile from the configuration file.

        Args:
            name: Profile name to delete

        Raises:
            SystemExit: If profile not found or save fails
        """
        if name not in self.profiles:
            click.echo(f"Error: Profile '{name}' not found", err=True)
            sys.exit(1)

        del self.profiles[name]

        # Save to file
        config_data = {"profiles": self.profiles}
        try:
            with open(self.config_path, "w") as f:
                json.dump(config_data, f, indent=2)
        except Exception as e:
            click.echo(f"Error saving config: {e}", err=True)
            sys.exit(1)

    def apply_profile(
        self, name: str, controller: DisplayController, dry_run: bool = False
    ) -> None:
        """
        Apply a profile to all configured monitors.

        Args:
            name: Profile name
            controller: Display controller instance
            dry_run: If True, only show what would be done

        Raises:
            SystemExit: If profile not found or input invalid
        """
        profile = self.get_profile(name)
        if not profile:
            click.echo(f"Error: Profile '{name}' not found", err=True)
            sys.exit(1)

        monitors = profile.get("monitors", {})
        if not monitors:
            click.echo(
                f"Error: Profile '{name}' has no monitor configuration", err=True
            )
            sys.exit(1)

        click.echo(f"Applying profile: {name}")
        if description := profile.get("description"):
            click.echo(f"Description: {description}")

        for idx, (display_num, input_name) in enumerate(monitors.items()):
            input_name_lower = input_name.lower()
            if input_name_lower not in INPUT_MAP:
                click.echo(
                    f"Warning: Invalid input '{input_name}' for display {display_num}, skipping",
                    err=True,
                )
                continue

            input_code = INPUT_MAP[input_name_lower]

            # Check if monitor is already on the desired input
            current_input = controller.get_input(display_num)
            if current_input == input_code:
                click.echo(
                    f"  Display {display_num} → {input_name.upper()} (code {input_code}) [already set, skipping]"
                )
                continue

            click.echo(
                f"  Display {display_num} → {input_name.upper()} (code {input_code})"
            )
            controller.set_input(display_num, input_code)

            # Add delay between monitors to avoid DDC timing issues (except after last monitor)
            if idx < len(monitors) - 1:
                import time

                time.sleep(0.5)

        if dry_run and isinstance(controller, MockDisplayController):
            click.echo("\n" + controller.get_state_summary())

        click.echo("✓ Profile applied successfully!")
