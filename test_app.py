#!/usr/bin/env python3
"""
Test script for WidgetWall application
Run this to verify the app structure is correct
"""

import sys
import os
from pathlib import Path

# Add project to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

def test_imports():
    """Test all imports."""
    print("Testing imports...")
    
    try:
        from PyQt6.QtWidgets import QApplication, QWidget
        print("✓ PyQt6 imported successfully")
    except ImportError as e:
        print(f"✗ PyQt6 import failed: {e}")
        return False
    
    try:
        from app.utils.logger import logger, setup_logger
        print("✓ Logger imported successfully")
    except ImportError as e:
        print(f"✗ Logger import failed: {e}")
        return False
    
    try:
        from app.utils.theme_manager import ThemeManager
        print("✓ Theme Manager imported successfully")
    except ImportError as e:
        print(f"✗ Theme Manager import failed: {e}")
        return False
    
    try:
        from app.native.macos_utils import get_macos_version, get_cpu_usage
        print("✓ macOS Utils imported successfully")
    except ImportError as e:
        print(f"✗ macOS Utils import failed: {e}")
        return False
    
    try:
        from app.widgets.base_widget import BaseWidget, WIDGET_REGISTRY, create_widget
        print(f"✓ Base Widget imported successfully ({len(WIDGET_REGISTRY)} widgets)")
    except ImportError as e:
        print(f"✗ Base Widget import failed: {e}")
        return False
    
    try:
        from app.widget_engine import WidgetEngine
        print("✓ Widget Engine imported successfully")
    except ImportError as e:
        print(f"✗ Widget Engine import failed: {e}")
        return False
    
    return True

def test_theme_manager():
    """Test theme manager functionality."""
    print("\nTesting Theme Manager...")
    
    try:
        from app.utils.theme_manager import ThemeManager
        
        theme_dir = PROJECT_ROOT / "data" / "themes"
        tm = ThemeManager(theme_dir)
        
        themes = tm.get_available_themes()
        print(f"✓ Found {len(themes)} themes: {', '.join(themes)}")
        
        # Test loading a theme
        tm.load_theme("minimal_dark")
        print(f"✓ Theme loaded: {tm.current_theme_name}")
        
        # Test color retrieval
        bg = tm.get_color("background")
        print(f"✓ Background color: {bg}")
        
        return True
        
    except Exception as e:
        print(f"✗ Theme Manager test failed: {e}")
        return False

def test_widget_creation():
    """Test widget creation."""
    print("\nTesting Widget Creation...")
    
    try:
        from app.widgets.base_widget import create_widget, WIDGET_REGISTRY
        
        # Check widget registry
        print(f"✓ Widget registry has {len(WIDGET_REGISTRY)} widgets")
        
        for widget_type, info in list(WIDGET_REGISTRY.items())[:3]:  # Test first 3
            print(f"  - {info['name']}: {info['description']}")
        
        return True
        
    except Exception as e:
        print(f"✗ Widget creation test failed: {e}")
        return False

def test_macos_utils():
    """Test macOS utilities."""
    print("\nTesting macOS Utilities...")
    
    try:
        from app.native.macos_utils import (
            get_macos_version,
            get_cpu_usage,
            get_memory_usage,
            get_battery_info
        )
        
        version = get_macos_version()
        print(f"✓ macOS Version: {version or 'Unknown'}")
        
        cpu = get_cpu_usage()
        print(f"✓ CPU Usage: {cpu:.1f}%")
        
        mem = get_memory_usage()
        print(f"✓ Memory: {mem.get('used_percent', 0):.1f}% used")
        
        battery = get_battery_info()
        print(f"✓ Battery: {battery}")
        
        return True
        
    except Exception as e:
        print(f"✗ macOS Utils test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("WidgetWall - Application Test")
    print("=" * 60)
    
    all_passed = True
    
    # Test imports
    if not test_imports():
        all_passed = False
    
    # Test theme manager
    if not test_theme_manager():
        all_passed = False
    
    # Test widgets
    if not test_widget_creation():
        all_passed = False
    
    # Test macOS utilities
    if not test_macos_utils():
        all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ All tests passed!")
        print("\nTo run the app:")
        print("  1. Install dependencies: pip install -r requirements.txt")
        print("  2. Run the app: python main.py")
    else:
        print("✗ Some tests failed. Please check the errors above.")
    print("=" * 60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())

