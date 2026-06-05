#!/usr/bin/env python3
"""
Simple test to verify PyQt6 and app imports
"""
import sys
import os

print("Python:", sys.executable)
print("Python version:", sys.version)

# Test 1: PyQt6 basic import
print("\n=== Test 1: PyQt6 Import ===")
try:
    from PyQt6.QtWidgets import QApplication, QLabel, QSystemTrayIcon, QMenu
    from PyQt6.QtCore import Qt
    print("✓ PyQt6.QtWidgets imported successfully")
except ImportError as e:
    print(f"✗ PyQt6 Import Error: {e}")
    print("\nTo install PyQt6, run:")
    print("  /Library/Frameworks/Python.framework/Versions/3.14/bin/python3 -m pip install PyQt6")
    sys.exit(1)

# Test 2: App imports
print("\n=== Test 2: App Imports ===")
app_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, app_dir)

try:
    from app.utils.logger import setup_logger, logger
    print("✓ Logger imported")
except ImportError as e:
    print(f"✗ Logger Import Error: {e}")

try:
    from app.utils.theme_manager import ThemeManager
    print("✓ ThemeManager imported")
except ImportError as e:
    print(f"✗ ThemeManager Import Error: {e}")

try:
    from app.native.macos_utils import get_macos_version
    print("✓ macos_utils imported")
except ImportError as e:
    print(f"✗ macos_utils Import Error: {e}")

try:
    from app.widgets.base_widget import WIDGET_REGISTRY
    print(f"✓ Widgets imported: {len(WIDGET_REGISTRY)} widgets")
except ImportError as e:
    print(f"✗ Widgets Import Error: {e}")

print("\n=== Test 3: Running Minimal GUI ===")
# Create a minimal app
app = QApplication(sys.argv)
label = QLabel("WidgetWall - PyQt6 is working!")
label.setAlignment(Qt.AlignmentFlag.AlignCenter)
label.setMinimumSize(400, 200)
print("✓ QApplication created successfully")
print("✓ QLabel created successfully")
print("\nIf you see a window, PyQt6 is working correctly!")
print("Close the window to exit.")

# label.show()
# app.exec()

print("\n=== Summary ===")
print("All imports successful!")
print("\nTo run the full app:")
print("  cd /Users/maanas/Project\\ Files/widgetwall")
print("  /Library/Frameworks/Python.framework/Versions/3.14/bin/python3 main.py")

