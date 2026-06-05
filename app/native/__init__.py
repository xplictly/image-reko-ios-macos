# Native macOS utilities package

from app.native.macos_utils import (
    get_macos_version,
    get_macos_major_version,
    get_permission_status,
    request_screen_recording_permission,
    request_accessibility_permission,
    show_notification,
    set_app_nap_inhibition,
    get_active_window_info,
    get_screen_info,
    install_login_item,
    uninstall_login_item,
    get_battery_info,
    get_cpu_usage,
    get_memory_usage,
    ClickThroughManager
)

__all__ = [
    'get_macos_version',
    'get_macos_major_version',
    'get_permission_status',
    'request_screen_recording_permission',
    'request_accessibility_permission',
    'show_notification',
    'set_app_nap_inhibition',
    'get_active_window_info',
    'get_screen_info',
    'install_login_item',
    'uninstall_login_item',
    'get_battery_info',
    'get_cpu_usage',
    'get_memory_usage',
    'ClickThroughManager'
]

