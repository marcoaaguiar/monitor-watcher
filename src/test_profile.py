#!/usr/bin/env python3
"""Test profile application to debug errors."""

import sys
from controllers import M1DDCController
from profile_manager import ProfileManager
from constants import DEFAULT_CONFIG_PATH

def main():
    """Test applying a profile."""
    if len(sys.argv) < 2:
        print("Usage: python test_profile.py <profile_name>")
        print("\nAvailable profiles:")
        manager = ProfileManager(DEFAULT_CONFIG_PATH)
        for name in manager.list_profiles():
            print(f"  - {name}")
        sys.exit(1)

    profile_name = sys.argv[1]

    print(f"Testing profile: {profile_name}\n")
    print("=" * 60)

    try:
        controller = M1DDCController()
        manager = ProfileManager(DEFAULT_CONFIG_PATH)

        print("✓ Controller and manager initialized\n")

        manager.apply_profile(profile_name, controller, dry_run=False)

        print("\n" + "=" * 60)
        print("✓ SUCCESS: Profile applied without errors!")

    except Exception as e:
        print("\n" + "=" * 60)
        print(f"✗ ERROR: {e}")
        import traceback
        print("\nFull traceback:")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
