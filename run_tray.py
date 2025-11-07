#!/usr/bin/env python3
"""Convenience entry point for the tray app."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from tray_app import run_app

if __name__ == "__main__":
    run_app()
