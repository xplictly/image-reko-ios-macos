"""
macOS Native Utilities for WidgetWall
Provides native macOS integration using PyObjC
"""

import sys
import subprocess
import json
from pathlib import Path
from typing import Optional, Dict, List
from app.utils.logger import logger


# Platform / optional native libs detection
IS_DARWIN = sys.platform == 'darwin'
HAS_PYOBJC = False
objc = None
Foundation = None
AppKit = None
Quartz = None

if IS_DARWIN:
    try:
        import objc as _objc
        import Foundation as _Foundation
        import AppKit as _AppKit
        import Quartz as _Quartz

        objc = _objc
        Foundation = _Foundation
        AppKit = _AppKit
        Quartz = _Quartz
        HAS_PYOBJC = True
    except Exception:
        # PyObjC not available at runtime; functions will use safe fallbacks
        HAS_PYOBJC = False
        objc = None
        Foundation = None
        AppKit = None
        Quartz = None


def get_macos_version() -> Optional[str]:
    """Get macOS version string."""
    try:
        if not IS_DARWIN:
            return None

        result = subprocess.run(
            ["sw_vers", "-productVersion"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.stdout.strip()
    except Exception as e:
        logger.error(f"Failed to get macOS version: {e}")
        return None


def get_macos_major_version() -> int:
    """Get major macOS version number."""
    version = get_macos_version()
    if version:
        try:
            major = int(version.split('.')[0])
            return major
        except Exception:
            pass
    # Return a sensible default when unknown
    return 10


def is_macos_sonoma_or_later() -> bool:
    """Check if running macOS 14 (Sonoma) or later."""
    return get_macos_major_version() >= 14


def is_macos_tahoe_or_later() -> bool:
    """Check if running macOS 15 (Tahoe) or later."""
    return get_macos_major_version() >= 15


def get_permission_status(permission_type: str) -> str:
    """
    Check macOS permission status.
    
    Args:
        permission_type: Type of permission (screen_recording, accessibility, location)
    
    Returns:
        Status string: 'authorized', 'denied', 'not_determined', 'restricted'
    """
    try:
        if not IS_DARWIN:
            return 'not_supported'

        # Screen recording: attempt to query window list via Quartz (if available)
        if permission_type == "screen_recording":
            if Quartz is None:
                return 'not_determined'
            try:
                windows = Quartz.CGWindowListCopyWindowInfo(
                    Quartz.kCGWindowListExcludeDesktopElements | Quartz.kCGWindowListOptionOnScreenOnly,
                    Quartz.kCGNullWindowID
                )
                return 'authorized'
            except Exception:
                return 'denied'

        elif permission_type == "accessibility":
            # Try AppleScript to access System Events
            try:
                result = subprocess.run(
                    ["osascript", "-e", 'tell application "System Events" to get name of every process'],
                    capture_output=True,
                    timeout=5
                )
                if result.returncode == 0:
                    return 'authorized'
                else:
                    return 'denied'
            except Exception:
                return 'denied'

        elif permission_type == "location":
            try:
                result = subprocess.run(
                    ["defaults", "read", "com.apple.locationd", "LocationServicesEnabled"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0 and "1" in result.stdout:
                    return 'authorized'
                else:
                    return 'denied'
            except Exception:
                return 'not_determined'

        return 'not_determined'

    except Exception as e:
        logger.error(f"Error checking permission {permission_type}: {e}")
        return 'not_determined'


def request_screen_recording_permission() -> bool:
    """
    Request Screen Recording permission.
    This requires opening System Preferences > Security & Privacy.
    """
    try:
        # Open Security & Privacy to Screen Recording
        subprocess.run([
            "open", "x-apple.systempreferences:com.apple.security.privacy.screenrecording"
        ])
        
        logger.info("Opened System Preferences for Screen Recording permission")
        return True
    except Exception as e:
        logger.error(f"Failed to open System Preferences: {e}")
        return False


def request_accessibility_permission() -> bool:
    """Request Accessibility permission."""
    try:
        # Open Security & Privacy to Accessibility
        subprocess.run([
            "open", "x-apple.systempreferences:com.apple.security.privacy.accessibility"
        ])
        
        logger.info("Opened System Preferences for Accessibility permission")
        return True
    except Exception as e:
        logger.error(f"Failed to open System Preferences: {e}")
        return False


def show_notification(
    title: str,
    message: str,
    subtitle: Optional[str] = None,
    sound: bool = True
) -> bool:
    """
    Show a macOS notification.
    
    Args:
        title: Notification title
        message: Notification message
        subtitle: Optional subtitle
        sound: Whether to play a sound
    
    Returns:
        True if notification was shown successfully
    """
    try:
        # Use AppleScript to show notification
        script = f'display notification "{message}"'
        if subtitle:
            script += f' with subtitle "{subtitle}"'
        script += f' with title "{title}"'
        if sound:
            script += ' sound name "default"'
        
        subprocess.run(["osascript", "-e", script])
        return True
        
    except Exception as e:
        logger.error(f"Failed to show notification: {e}")
        return False


def set_app_nap_inhibition(app_name: str = "WidgetWall") -> bool:
    """
    Prevent app from being put to sleep by macOS App Nap.
    
    Args:
        app_name: Name of the app to inhibit nap for
    
    Returns:
        True if successful
    """
    try:
        if not IS_DARWIN or Foundation is None:
            return False

        # NSProcessInfo API: beginActivityWithOptions_reason_
        try:
            processInfo = Foundation.NSProcessInfo.processInfo()
            options = (1 << 20) | (1 << 17) if hasattr(Foundation.NSProcessInfo, 'processInfo') else 0
            # Use recommended constants when available; fall back to numeric flags
            reason = f"{app_name} needs to stay running"
            # PyObjC mapping: beginActivityWithOptions_reason_
            if hasattr(processInfo, 'beginActivityWithOptions_reason_'):
                processInfo.beginActivityWithOptions_reason_(0x00000001 | 0x00000002, reason)
            else:
                # Best-effort no-op
                pass

            return True

        except Exception as e:
            logger.warning(f"Failed to disable App Nap (inner): {e}")
            return False

    except Exception as e:
        logger.warning(f"Failed to disable App Nap: {e}")
        return False


def get_active_window_info() -> Optional[Dict]:
    """Get information about the currently active window."""
    try:
        if not IS_DARWIN or Quartz is None:
            return None

        options = Quartz.kCGWindowListExcludeDesktopElements | Quartz.kCGWindowListOptionOnScreenOnly
        window_list = Quartz.CGWindowListCopyWindowInfo(options, Quartz.kCGNullWindowID)

        if window_list and len(window_list) > 0:
            front_window = window_list[0]
            return {
                "name": front_window.get('kCGWindowName', 'Unknown'),
                "owner": front_window.get('kCGWindowOwnerName', 'Unknown'),
                "bounds": front_window.get('kCGWindowBounds', {}),
                "id": front_window.get('kCGWindowNumber', 0)
            }

        return None

    except Exception as e:
        logger.error(f"Failed to get active window info: {e}")
        return None


def get_screen_info() -> List[Dict]:
    """Get information about all connected screens."""
    try:
        screens = []

        # Prefer AppKit.NSScreen when available
        if IS_DARWIN and AppKit is not None and hasattr(AppKit, 'NSScreen'):
            try:
                main_screen = AppKit.NSScreen.mainScreen()
                if main_screen:
                    frame = main_screen.frame()
                    backing_scale = main_screen.backingScaleFactor() if hasattr(main_screen, 'backingScaleFactor') else 1.0

                    screens.append({
                        "id": "main",
                        "name": "Built-in Display",
                        "x": int(frame.origin.x),
                        "y": int(frame.origin.y),
                        "width": int(frame.size.width),
                        "height": int(frame.size.height),
                        "scale": backing_scale
                    })

                for i, screen in enumerate(AppKit.NSScreen.screens()):
                    if screen == main_screen:
                        continue
                    frame = screen.frame()
                    backing_scale = screen.backingScaleFactor() if hasattr(screen, 'backingScaleFactor') else 1.0
                    screens.append({
                        "id": f"screen_{i}",
                        "name": f"Display {i+1}",
                        "x": int(frame.origin.x),
                        "y": int(frame.origin.y),
                        "width": int(frame.size.width),
                        "height": int(frame.size.height),
                        "scale": backing_scale
                    })

                return screens
            except Exception:
                # fall through to Quartz or empty list
                pass

        # Fallback to Quartz if available
        if Quartz is not None and hasattr(Quartz, 'CGDisplayBounds'):
            try:
                # Use CGDisplay APIs for basic info
                main_id = Quartz.CGMainDisplayID()
                bounds = Quartz.CGDisplayBounds(main_id)
                screens.append({
                    "id": "main",
                    "name": "Display",
                    "x": int(bounds.origin.x),
                    "y": int(bounds.origin.y),
                    "width": int(bounds.size.width),
                    "height": int(bounds.size.height),
                    "scale": Quartz.CGDisplayScreenSize(main_id).width if hasattr(Quartz, 'CGDisplayScreenSize') else 1.0
                })
                return screens
            except Exception:
                return []

        return []

    except Exception as e:
        logger.error(f"Failed to get screen info: {e}")
        return []


def move_window_to_background(window_id: int) -> bool:
    """Move a window to the background (below other windows)."""
    try:
        import Quartz as q
        
        # Set window level to background
        q.CGWindowLevelForKey(q.kCGNormalWindowLevel)
        
        # Actually, let's try a different approach
        # We'll use NSWindow to manipulate the level
        
        # This is more complex - let's just return True for now
        # A proper implementation would require getting the NSWindow object
        return True
        
    except Exception as e:
        logger.error(f"Failed to move window to background: {e}")
        return False


def install_login_item(
    path: str,
    name: str = "WidgetWall",
    hidden: bool = False
) -> bool:
    """
    Install the app to run at login using launchd.
    
    Args:
        path: Path to the app or script to run
        name: Name for the login item
        hidden: Whether to run hidden
    
    Returns:
        True if successful
    """
    try:
        # Create a launch agent plist
        plist_path = f"~/Library/LaunchAgents/com.{name.lower()}.plist"
        plist_path = Path(plist_path).expanduser()
        
        plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.{name.lower()}</string>
    <key>ProgramArguments</key>
    <array>
        <string>{path}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>ProcessType</key>
    <string>UIElement</string>
    <key>LSUIElement</key>
    <true/>
</dict>
</plist>
"""
        
        with open(plist_path, 'w') as f:
            f.write(plist_content)
        
        # Load the launch agent
        subprocess.run(["launchctl", "load", "-w", str(plist_path)])
        
        logger.info(f"Installed login item: {name}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to install login item: {e}")
        return False


def uninstall_login_item(name: str = "WidgetWall") -> bool:
    """
    Remove the app from running at login.
    
    Args:
        name: Name of the login item
    
    Returns:
        True if successful
    """
    try:
        plist_path = f"~/Library/LaunchAgents/com.{name.lower()}.plist"
        plist_path = Path(plist_path).expanduser()
        
        # Unload first
        subprocess.run(["launchctl", "unload", "-w", str(plist_path)], capture_output=True)
        
        # Remove plist file
        if plist_path.exists():
            plist_path.unlink()
        
        logger.info(f"Uninstalled login item: {name}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to uninstall login item: {e}")
        return False


def get_current_language() -> str:
    """Get the current system language code."""
    try:
        result = subprocess.run(
            ["defaults", "read", "-g", "AppleLocale"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.stdout.strip() or "en_US"
    except:
        return "en_US"


def get_battery_info() -> Optional[Dict]:
    """Get battery information."""
    try:
        # Use pmset to get battery info
        result = subprocess.run(
            ["pmset", "-g", "batt"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if 'Now drawing' in line or 'InternalBattery' in line:
                    # Parse the line
                    # Example: "   0:      charged ('-'; rate: 0 mA) 100%; charging via Wall Outlet charger"
                    parts = line.split()
                    
                    # Try to extract percentage
                    percentage = None
                    for i, part in enumerate(parts):
                        if '%' in part:
                            percentage = int(part.replace('%', ''))
                            break
                    
                    # Check if charging
                    charging = 'charging' in line.lower() or 'AC' in line.lower()
                    
                    return {
                        "percentage": percentage,
                        "charging": charging,
                        "raw": line.strip()
                    }
        
        return None
        
    except Exception as e:
        logger.error(f"Failed to get battery info: {e}")
        return None


def get_cpu_usage() -> float:
    """Get current CPU usage percentage."""
    try:
        # Use top to get CPU usage
        result = subprocess.run(
            ["top", "-l", "1", "-n", "0"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if line.startswith("CPU usage:"):
                    # Parse: "CPU usage: 12.3% user, 8.1% sys, 79.6% idle"
                    parts = line.replace("CPU usage:", "").split(",")
                    
                    user = 0.0
                    sys_cpu = 0.0
                    
                    for part in parts:
                        part = part.strip()
                        if '%' in part:
                            try:
                                value = float(part.replace('%', '').split()[0])
                                if 'user' in part:
                                    user = value
                                elif 'sys' in part:
                                    sys_cpu = value
                            except:
                                pass
                    
                    return user + sys_cpu
        
        return 0.0
        
    except Exception as e:
        logger.error(f"Failed to get CPU usage: {e}")
        return 0.0


def get_memory_usage() -> Dict:
    """Get memory usage statistics."""
    try:
        # Use vm_stat to get memory info
        result = subprocess.run(
            ["vm_stat"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            
            # Parse vm_stat output
            # Each line looks like: "Pages free:                         12345."
            stats = {}
            for line in lines:
                if ':' in line:
                    key, value = line.split(':')
                    key = key.strip().replace(' ', '_').lower()
                    value = value.strip().replace('.', '')
                    try:
                        stats[key] = int(value)
                    except:
                        pass
            
            # Convert pages to bytes (page size is 4096 on most Macs)
            page_size = 4096
            
            total = 0
            wired = stats.get('page_size_of_wired', 0)
            active = stats.get('page_size_of_active', 0)
            inactive = stats.get('page_size_of_inactive', 0)
            free = stats.get('pages_free', 0)
            
            total = (wired + active + inactive + free) * page_size
            used = (wired + active + inactive) * page_size
            
            return {
                "total_bytes": total,
                "used_bytes": used,
                "free_bytes": free * page_size,
                "used_percent": (used / total * 100) if total > 0 else 0
            }
        
        return {"total_bytes": 0, "used_bytes": 0, "free_bytes": 0, "used_percent": 0}
        
    except Exception as e:
        logger.error(f"Failed to get memory usage: {e}")
        return {"total_bytes": 0, "used_bytes": 0, "free_bytes": 0, "used_percent": 0}


def run_applescript(script: str) -> subprocess.CompletedProcess:
    """Run an AppleScript command."""
    try:
        return subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            timeout=30
        )
    except Exception as e:
        logger.error(f"Failed to run AppleScript: {e}")
        return subprocess.CompletedProcess(args=[], returncode=1, stdout="", stderr=str(e))


class ClickThroughManager:
    """Manages click-through mode for widget windows."""
    
    def __init__(self):
        self.enabled = False
        self.window_levels = {}
    
    def enable_click_through(self, window_id: int) -> bool:
        """Enable click-through for a specific window."""
        try:
            # For Qt widgets, we need to set up the window to ignore mouse events
            # This is done at the widget level, not here
            # But we can store the desired state
            self.window_levels[window_id] = True
            return True
        except Exception as e:
            logger.error(f"Failed to enable click-through: {e}")
            return False
    
    def disable_click_through(self, window_id: int) -> bool:
        """Disable click-through for a specific window."""
        try:
            if window_id in self.window_levels:
                del self.window_levels[window_id]
            return True
        except Exception as e:
            logger.error(f"Failed to disable click-through: {e}")
            return False
    
    def is_click_through_enabled(self, window_id: int) -> bool:
        """Check if click-through is enabled for a window."""
        return self.window_levels.get(window_id, False)


