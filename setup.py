"""
Setup script for building standalone macOS .app bundle.

Usage:
    python setup.py py2app
"""

from setuptools import setup
import sys
sys.path.insert(0, 'src')

APP = ['src/tray.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': False,
    'iconfile': None,  # TODO: Add icon file path here
    'plist': {
        'CFBundleName': 'Monitor Watcher',
        'CFBundleDisplayName': 'Monitor Watcher',
        'CFBundleIdentifier': 'com.monitor-watcher.app',
        'CFBundleVersion': '0.1.0',
        'CFBundleShortVersionString': '0.1.0',
        'LSUIElement': False,  # Set to True to hide from Dock
        'NSHumanReadableCopyright': 'Copyright © 2025',
    },
    'packages': ['rumps', 'click', 'src'],
    'includes': ['src.constants', 'src.controllers', 'src.profile_manager'],
}

setup(
    name='Monitor Watcher',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
