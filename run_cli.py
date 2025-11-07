#!/usr/bin/env python3
"""Convenience entry point for the CLI."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from cli import cli

if __name__ == "__main__":
    cli()
