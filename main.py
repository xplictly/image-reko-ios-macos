#!/usr/bin/env python3
"""
WidgetWall Clone - macOS Desktop Widgets Application
Premium widgets for macOS 10.15+ without subscription
"""

import sys
import os
import json
import argparse
import signal
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

# Add app directory to path
APP_DIR = Path(__file__).parent
sys.path.insert(0, str(APP_DIR))

# Check PyQt6 availability FIRST
try:
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt
    PYQT6_AVAILABLE = True
except ImportError:
    print("Error: PyQt6 is required but not installed.")
    print("")
    print("To install PyQt6, run:")
    print("  python3 -m pip install PyQt6")
    print("")
    print("Or using pip3:")
    print("  pip3 install PyQt6")
    print("")
    sys.exit(1)

# Import core modules
try:
    from app.main_window import WidgetWallApp
    from app.utils.logger import setup_logger, logger
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure all dependencies are installed: python3 -m pip install -r requirements.txt")
    sys.exit(1)


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="WidgetWall - Desktop Widgets for macOS",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Start app normally
  python main.py --debug            # Start with debug mode
  python main.py --reset            # Reset all settings
  python main.py --install          # Install as login item
  python main.py --uninstall        # Remove from login items
        """
    )
    
    parser.add_argument(
        "--debug", 
        action="store_true",
        help="Enable debug mode with verbose logging"
    )
    parser.add_argument(
        "--reset", 
        action="store_true",
        help="Reset all settings and widget positions"
    )
    parser.add_argument(
        "--install", 
        action="store_true",
        help="Install app to run at login"
    )
    parser.add_argument(
        "--uninstall", 
        action="store_true",
        help="Remove app from login items"
    )
    parser.add_argument(
        "--config", 
        type=str,
        default=str(APP_DIR / "data"),
        help="Custom configuration directory (default: data)"
    )
    parser.add_argument(
        "--theme",
        type=str,
        default="minimal_dark",
        help="Default theme (minimal_dark, minimal_light)"
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="Show version information"
    )
    
    return parser.parse_args()


def setup_signal_handlers():
    """Setup signal handlers for graceful shutdown."""
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


def check_macos_compatibility():
    """Check macOS version compatibility."""
    import platform
    
    version = platform.mac_ver()[0]
    if not version:
        print("Warning: This app is designed for macOS only.")
        return False
    
    major, minor = version.split('.')[:2]
    major, minor = int(major), int(minor)
    
    if major < 10 or (major == 10 and minor < 15):
        print(f"Error: macOS 10.15 (Catalina) or later is required.")
        print(f"Current version: macOS {version}")
        sys.exit(1)
    
    if major > 15:
        print(f"Warning: This app may not be fully tested on macOS {version}.")
        print("Some features may not work as expected.")
    
    logger.info(f"Running on macOS {version}")
    return True


def reset_all_settings(config_dir: Path):
    """Reset all settings and widget positions."""
    settings_file = config_dir / "settings.json"
    positions_file = config_dir / "widget_positions.json"
    cache_dir = config_dir / "cache"
    
    files_to_remove = [settings_file, positions_file]
    
    # Backup old settings
    backup_dir = config_dir / "backups"
    if settings_file.exists() or positions_file.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = backup_dir / f"backup_{timestamp}"
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        if settings_file.exists():
            import shutil
            shutil.copy2(settings_file, backup_dir / "settings.json")
            print(f"Backed up settings to: {backup_dir / 'settings.json'}")
        
        if positions_file.exists():
            import shutil
            shutil.copy2(positions_file, backup_dir / "widget_positions.json")
            print(f"Backed up positions to: {backup_dir / 'widget_positions.json'}")
    
    # Remove settings files
    for f in files_to_remove:
        if f.exists():
            f.unlink()
            print(f"Removed: {f}")
    
    # Clear cache
    if cache_dir.exists():
        import shutil
        shutil.rmtree(cache_dir)
        print(f"Cleared cache: {cache_dir}")
    
    print("\nSettings have been reset. Starting fresh...")
    print(f"Backup saved to: {backup_dir}" if backup_dir.exists() else "")


def setup_config_directory(config_dir: Path):
    """Ensure configuration directory exists."""
    config_dir.mkdir(parents=True, exist_ok=True)
    
    # Create subdirectories
    (config_dir / "cache").mkdir(exist_ok=True)
    (config_dir / "backups").mkdir(exist_ok=True)
    (config_dir / "themes" / "custom").mkdir(parents=True, exist_ok=True)
    
    # Create default settings if not exists
    settings_file = config_dir / "settings.json"
    if not settings_file.exists():
        default_settings = {
            "version": "1.0.0",
            "first_run": True,
            "theme": "minimal_dark",
            "language": "en",
            "widgets": {},
            "global_settings": {
                "click_through": False,
                "always_on_top": True,
                "show_menu_bar_icon": True,
                "start_at_login": False,
                "auto_update": False,
                "notifications_enabled": True
            },
            "window_settings": {
                "width": 1920,
                "height": 1080,
                "primary_monitor": 0
            },
            "last_updated": datetime.now().isoformat()
        }
        
        with open(settings_file, 'w', encoding='utf-8') as f:
            json.dump(default_settings, f, indent=2, ensure_ascii=False)
        
        print(f"Created default settings: {settings_file}")


def main():
    """Main application entry point."""
    args = parse_arguments()
    
    # Setup logging
    log_level = "DEBUG" if args.debug else "INFO"
    log_file = APP_DIR / "widgetwall.log"
    setup_logger(log_file, log_level)
    
    logger.info("=" * 60)
    logger.info("WidgetWall - Starting Application")
    logger.info("=" * 60)
    
    # Check macOS compatibility
    if not check_macos_compatibility():
        return
    
    # Setup signal handlers
    setup_signal_handlers()
    
    # Setup configuration directory
    config_dir = Path(args.config)
    setup_config_directory(config_dir)
    
    # Handle special commands
    if args.reset:
        reset_all_settings(config_dir)
        return
    
    if args.version:
        from app import __version__
        print(f"WidgetWall Version: {__version__}")
        print(f"Python: {sys.version}")
        return
    
    if args.install:
        from app.utils.macos_utils import install_login_item
        install_login_item()
        return
    
    if args.uninstall:
        from app.utils.macos_utils import uninstall_login_item
        uninstall_login_item()
        return
    
    # Initialize and run application
    try:
        app = WidgetWallApp(
            config_dir=config_dir,
            debug=args.debug,
            default_theme=args.theme
        )
        
        # Run the application
        exit_code = app.run()
        sys.exit(exit_code)
        
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        print(f"\nError: {e}")
        print("\nPlease check the log file for details:")
        print(f"  {log_file}")
        sys.exit(1)


if __name__ == "__main__":
    main()

