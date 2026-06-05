"""
Setup script for WidgetWall macOS app
Usage: python setup.py py2app
"""

from setuptools import setup

APP_NAME = "WidgetWall"
APP = "main.py"

DATA_FILES = [
    ("resources", ["data/resources/icon.icns"]),
]

OPTIONS = {
    "py2app": {
        "app": APP,
        "name": APP_NAME,
        "version": "1.0.0",
        "description": "Desktop widgets for macOS 10.15+",
        "author": "Maanas",
        "author_email": "maanas@example.com",
        "url": "https://github.com/maanas/widgetwall",
        "license": "MIT",
        "resources": ["data/resources"],
        "packages": [
            "app",
            "app.utils",
            "app.native",
            "app.widgets",
            "app.ui"
        ],
        "includes": [
            "PyQt6",
            "PyQt6.QtCore",
            "PyQt6.QtWidgets",
            "PyQt6.QtGui",
            "objc",
            "Foundation",
            "AppKit",
            "Quartz"
        ],
        "excludes": [
            "Tkinter",
            "tkinter"
        ],
        "plist": {
            "CFBundleName": APP_NAME,
            "CFBundleDisplayName": APP_NAME,
            "CFBundleIdentifier": "com.widgetwall.app",
            "CFBundleVersion": "1.0.0",
            "CFBundleShortVersionString": "1.0.0",
            "CFBundlePackageType": "APPL",
            "CFBundleExecutable": APP_NAME,
            "LSUIElement": "1",
            "NSHumanReadableCopyright": "Copyright 2024. All rights reserved.",
            "NSPrincipalClass": "NSApplication",
            "LSMinimumSystemVersion": "10.15.0",
        },
        "semi-standalone": True,
        "site-packages": True,
        "strip": True,
        "dist-dir": "dist",
        "build-dir": "build",
    }
}

setup(
    name=APP_NAME,
    app=[APP],
    data_files=DATA_FILES,
    options=OPTIONS,
    setup_requires=["py2app", "PyQt6"],
    install_requires=["PyQt6>=6.4.0"],
)

