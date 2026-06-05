"""
WidgetWall Main Window - Menu Bar Application Controller
Handles the menu bar app and widget management
"""

import sys
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

try:
    from PyQt6.QtWidgets import (
        QApplication, QSystemTrayIcon, QMenu, QMessageBox,
        QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
        QListWidget, QListWidgetItem, QDialog, QDialogButtonBox,
        QInputDialog, QLineEdit, QFileDialog, QColorDialog,
        QFrame, QSlider, QCheckBox, QComboBox, QGroupBox,
        QScrollArea, QGridLayout, QStackedWidget, QToolButton,
        QGraphicsDropShadowEffect
    )
    from PyQt6.QtCore import (
        Qt, QSize, QPoint, QTimer, QSettings, QObject,
        pyqtSignal, QThread, QPropertyAnimation, QSequentialAnimationGroup, QEasingCurve,
        QRect, QMargins, QByteArray, QBuffer, QIODevice
    )
    from PyQt6.QtGui import (
        QIcon, QPixmap, QImage, QColor, QPainter, QPen,
        QBrush, QFont, QFontDatabase, QAction, QCursor,
        QScreen, QTransform, QPainterPath, QLinearGradient,
        QRadialGradient, QPalette
    )
except ImportError:
    print("Error: PyQt6 is required. Install with: pip install PyQt6")
    sys.exit(1)

try:
    import objc
    from Foundation import NSObject, NSApplication, NSMenu, NSMenuItem
    from AppKit import (
        NSApplication, NSMenu, NSMenuItem, NSImage,
        NSStatusBar, NSRunningApplication,
        NSWindow, NSBackingStoreBuffered,
        NSClosableWindowMask, NSMiniaturizableWindowMask,
        NSTitledWindowMask, NSResizableWindowMask,
        NSAlert, NSInformationalAlertStyle,
        NSPredicate, NSSortDescriptor,
        NSNotificationCenter, NSDefaultRunLoopMode
    )
    HAS_PYOBJC = True
except ImportError:
    HAS_PYOBJC = False
    print("Warning: PyObjC not available. Some macOS features disabled.")

from app.utils.logger import logger
from app.utils.theme_manager import ThemeManager
from app.widget_engine import WidgetEngine
from app.native.macos_utils import (
    get_macos_version, set_app_nap_inhibition,
    show_notification, get_permission_status,
    request_screen_recording_permission
)
from app.widgets.base_widget import WIDGET_REGISTRY


class WidgetWallApp(QApplication):
    """
    Main application class for WidgetWall.
    Provides menu bar integration and widget management.
    """
    
    # Signals
    widget_added = pyqtSignal(str)
    widget_removed = pyqtSignal(str)
    theme_changed = pyqtSignal(str)
    settings_changed = pyqtSignal(dict)
    
    def __init__(
        self,
        config_dir: Path = Path("data"),
        debug: bool = False,
        default_theme: str = "minimal_dark"
    ):
        super().__init__(["WidgetWall"])
        
        # Application properties
        self.config_dir = config_dir
        self.debug = debug
        self.default_theme = default_theme
        self.is_running = False
        
        # Managers
        self.theme_manager = None
        self.widget_engine = None
        self.settings = {}
        
        # Menu bar icon
        self.tray_icon = None
        self.tray_menu = None
        
        # Widget registry
        self.widgets: Dict[str, Dict] = {}
        self.widget_instances: Dict[str, QWidget] = {}
        
        # Initialize
        self._init_application()
        self._load_settings()
        self._init_theme()
        self._init_widget_engine()
        self._create_menu_bar()
        self._create_main_window()
        self._start_swift_helper()
        
        logger.info("WidgetWall application initialized")
    
    def _init_application(self):
        """Initialize application-wide settings."""
        self.setApplicationName("WidgetWall")
        self.setApplicationVersion("1.0.0")
        self.setOrganizationName("WidgetWall")
        self.setOrganizationDomain("com.widgetwall.app")
        
        # High DPI support
        # High DPI support (guarded for different PyQt versions)
        try:
            attr_scaling = getattr(Qt.ApplicationAttribute, 'AA_EnableHighDpiScaling', None)
            attr_pixmaps = getattr(Qt.ApplicationAttribute, 'AA_UseHighDpiPixmaps', None)
            if attr_scaling is not None:
                self.setAttribute(attr_scaling, True)
            if attr_pixmaps is not None:
                self.setAttribute(attr_pixmaps, True)
        except Exception:
            # Some Qt bindings may not expose these attributes; ignore
            pass
        
        # Style settings
        self.setStyle("macOS")
        
        # Keep application running in menu bar
        self.setQuitOnLastWindowClosed(False)
        
        # Request necessary permissions
        self._request_permissions()
    
    def _start_swift_helper(self):
        """Find and launch the compiled Swift helper executable in the background."""
        import subprocess
        self.swift_process = None
        
        try:
            # Find the WidgetWallSwift binary
            project_root = Path(__file__).parent.parent
            binary_matches = list(project_root.glob("native-swift/.build/**/debug/WidgetWallSwift"))
            
            if binary_matches:
                binary_path = binary_matches[0]
                logger.info(f"Launching native Swift helper: {binary_path}")
                self.swift_process = subprocess.Popen(
                    [str(binary_path)],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    text=True,
                    bufsize=1
                )
                
                # Start telemetry timer
                self.telemetry_timer = QTimer(self)
                self.telemetry_timer.timeout.connect(self._send_stats_to_swift)
                self.telemetry_timer.start(1000)
            else:
                logger.warning("native-swift helper binary not found. Run 'swift build' inside native-swift directory to compile it.")
        except Exception as e:
            logger.error(f"Failed to start Swift helper process: {e}")

    def _send_stats_to_swift(self):
        """Send mock telemetry data to the native Swift UI over JSON IPC."""
        if not self.swift_process or not self.swift_process.stdin:
            return
            
        try:
            import psutil
            cpu = psutil.cpu_percent()
            mem = psutil.virtual_memory().percent
        except ImportError:
            import random
            cpu = round(random.uniform(5.0, 35.0), 1)
            mem = round(random.uniform(40.0, 70.0), 1)
            
        try:
            payload = {
                "action": "update_stats",
                "cpu": cpu,
                "mem": mem
            }
            self.swift_process.stdin.write(json.dumps(payload) + "\n")
            self.swift_process.stdin.flush()
        except Exception as e:
            logger.error(f"IPC sending failed: {e}")

    def _request_permissions(self):
        """Request necessary macOS permissions."""
        # Check and request screen recording permission for click-through
        perm_status = get_permission_status("screen_recording")
        if perm_status != "authorized":
            logger.info("Requesting screen recording permission...")
            request_screen_recording_permission()
    
    def _load_settings(self):
        """Load application settings."""
        settings_file = self.config_dir / "settings.json"
        
        if settings_file.exists():
            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    self.settings = json.load(f)
                logger.info(f"Loaded settings from {settings_file}")
            except Exception as e:
                logger.error(f"Failed to load settings: {e}")
                self.settings = self._get_default_settings()
        else:
            self.settings = self._get_default_settings()
            self._save_settings()
    
    def _get_default_settings(self) -> dict:
        """Get default settings."""
        return {
            "version": "1.0.0",
            "theme": self.default_theme,
            "global": {
                "click_through": False,
                "always_on_top": True,
                "show_menu_bar_icon": True,
                "start_at_login": False,
                "auto_update": False,
                "notifications_enabled": True,
                "animations_enabled": True,
                "snap_to_grid": True,
                "grid_size": 20
            },
            "widgets": {},
            "window_positions": {},
            "custom_widgets": {},
            "last_backup": None
        }
    
    def _save_settings(self):
        """Save application settings."""
        settings_file = self.config_dir / "settings.json"
        
        try:
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved settings to {settings_file}")
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
    
    def _init_theme(self):
        """Initialize theme manager."""
        theme_dir = self.config_dir / "themes"
        self.theme_manager = ThemeManager(theme_dir)
        
        # Load theme
        theme_name = self.settings.get("theme", self.default_theme)
        self.theme_manager.load_theme(theme_name)
        
        # Apply theme colors
        self._apply_theme()
    
    def _apply_theme(self):
        """Apply current theme to application."""
        theme = self.theme_manager.current_theme
        
        if not theme:
            return
        
        # Color scheme
        palette = self.palette()
        
        # Window/Background
        bg_color = theme.get("colors", {}).get("background", "#1a1a1a")
        palette.setColor(QPalette.ColorRole.Window, QColor(bg_color))
        
        # Text
        text_color = theme.get("colors", {}).get("text", "#ffffff")
        palette.setColor(QPalette.ColorRole.WindowText, QColor(text_color))
        
        # Accent
        accent_color = theme.get("colors", {}).get("accent", "#007AFF")
        
        self.setPalette(palette)
        
        # CSS stylesheet
        self._apply_stylesheet(theme)
    
    def _apply_stylesheet(self, theme: dict):
        """Apply CSS stylesheet based on theme."""
        colors = theme.get("colors", {})
        
        css = f"""
        QMainWindow, QWidget {{
            background-color: {colors.get('background', '#1a1a1a')};
            color: {colors.get('text', '#ffffff')};
            font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif;
        }}
        
        QMenuBar {{
            background-color: {colors.get('background', '#1a1a1a')};
            color: {colors.get('text', '#ffffff')};
            border-bottom: 1px solid {colors.get('border', '#3d3d3d')};
        }}
        
        QMenu {{
            background-color: {colors.get('background', '#1a1a1a')};
            color: {colors.get('text', '#ffffff')};
            border: 1px solid {colors.get('border', '#3d3d3d')};
            border-radius: 6px;
            padding: 4px;
        }}
        
        QMenu::item {{
            padding: 8px 16px;
            border-radius: 4px;
            margin: 2px;
        }}
        
        QMenu::item:selected {{
            background-color: {colors.get('accent', '#007AFF')};
        }}
        
        QListWidget {{
            background-color: {colors.get('surface', '#2d2d2d')};
            color: {colors.get('text', '#ffffff')};
            border: 1px solid {colors.get('border', '#3d3d3d')};
            border-radius: 8px;
        }}
        
        QPushButton {{
            background-color: {colors.get('surface', '#2d2d2d')};
            color: {colors.get('text', '#ffffff')};
            border: 1px solid {colors.get('border', '#3d3d3d')};
            border-radius: 6px;
            padding: 8px 16px;
            font-size: 13px;
        }}
        
        QPushButton:hover {{
            background-color: {colors.get('hover', '#3d3d3d')};
        }}
        
        QPushButton:checked, QPushButton:pressed {{
            background-color: {colors.get('accent', '#007AFF')};
        }}
        
        QComboBox {{
            background-color: {colors.get('surface', '#2d2d2d')};
            color: {colors.get('text', '#ffffff')};
            border: 1px solid {colors.get('border', '#3d3d3d')};
            border-radius: 6px;
            padding: 6px 12px;
        }}
        
        QSlider::groove:horizontal {{
            background-color: {colors.get('border', '#3d3d3d')};
            height: 4px;
            border-radius: 2px;
        }}
        
        QSlider::handle:horizontal {{
            background-color: {colors.get('accent', '#007AFF')};
            width: 16px;
            height: 16px;
            margin: -6px 0;
            border-radius: 8px;
        }}
        
        QCheckBox {{
            color: {colors.get('text', '#ffffff')};
            spacing: 8px;
        }}
        
        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border-radius: 4px;
            border: 1px solid {colors.get('border', '#3d3d3d')};
        }}
        
        QCheckBox::indicator:checked {{
            background-color: {colors.get('accent', '#007AFF')};
        }}
        
        QGroupBox {{
            border: 1px solid {colors.get('border', '#3d3d3d')};
            border-radius: 8px;
            margin-top: 12px;
            padding-top: 12px;
            font-weight: 500;
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 12px;
            padding: 0 8px;
        }}
        
        QLabel {{
            color: {colors.get('text', '#ffffff')};
        }}
        
        QDialogButtonBox {{
            spacing: 8px;
        }}
        
        QDialogButtonBox button {{
            min-width: 80px;
        }}
        """
        
        self.setStyleSheet(css)
    
    def _init_widget_engine(self):
        """Initialize widget engine."""
        self.widget_engine = WidgetEngine(
            parent=self,
            config_dir=self.config_dir,
            theme_manager=self.theme_manager,
            settings=self.settings
        )
    
    def _create_menu_bar(self):
        """Create menu bar icon and menu."""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            logger.warning("System tray not available")
            return
        
        # Create tray icon
        self.tray_icon = QSystemTrayIcon(self)
        
        # Load icon
        icon_path = self.config_dir / "resources" / "icon.png"
        if icon_path.exists():
            icon = QIcon(str(icon_path))
            self.tray_icon.setIcon(icon)
        else:
            # Create default icon
            self.tray_icon.setIcon(self._create_default_icon())
        
        self.tray_icon.setToolTip("WidgetWall - Desktop Widgets")
        
        # Create menu
        self.tray_menu = QMenu()
        self._build_tray_menu()
        
        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.show()
        
        # Tray icon activation handler
        self.tray_icon.activated.connect(self._on_tray_activated)
    
    def _create_default_icon(self) -> QIcon:
        """Create a default application icon."""
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw widget icon
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor("#007AFF")))
        painter.drawRoundedRect(2, 6, 28, 20, 4, 4)
        
        # Draw dots
        painter.setBrush(QBrush(QColor("#ffffff")))
        painter.drawEllipse(8, 13, 4, 4)
        painter.drawEllipse(16, 13, 4, 4)
        painter.drawEllipse(24, 13, 4, 4)
        
        painter.end()
        
        return QIcon(pixmap)
    
    def _build_tray_menu(self):
        """Build the tray menu."""
        self.tray_menu.clear()
        
        # Widget management header
        header = QAction("WidgetWall", self)
        header.setEnabled(False)
        self.tray_menu.addAction(header)
        
        self.tray_menu.addSeparator()
        
        # Add widgets submenu
        add_menu = self.tray_menu.addMenu("Add Widget")
        
        # Add widget actions
        from app.widgets.base_widget import WIDGET_REGISTRY
        for widget_name, widget_info in WIDGET_REGISTRY.items():
            action = QAction(widget_info.get("icon", "") + " " + widget_info.get("name", widget_name), self)
            action.setData(widget_name)
            action.triggered.connect(lambda checked, w=widget_name: self._add_widget(w))
            add_menu.addAction(action)
        
        self.tray_menu.addSeparator()
        
        # View all widgets
        view_action = QAction("View All Widgets", self)
        view_action.triggered.connect(self._show_main_window)
        self.tray_menu.addAction(view_action)
        
        # Show active widgets submenu
        if self.widget_instances:
            active_menu = self.tray_menu.addMenu("Active Widgets")
            for widget_id, widget in self.widget_instances.items():
                if widget.isVisible():
                    name = self.settings.get("widgets", {}).get(widget_id, {}).get("name", widget_id)
                    action = QAction(name, self)
                    action.setData(widget_id)
                    action.triggered.connect(lambda checked, w=widget_id: self._show_widget(w))
                    active_menu.addAction(action)
            
            # Hide all action
            hide_action = QAction("Hide All Widgets", self)
            hide_action.triggered.connect(self._hide_all_widgets)
            self.tray_menu.addAction(hide_action)
        else:
            no_widgets = QAction("No active widgets", self)
            no_widgets.setEnabled(False)
            self.tray_menu.addAction(no_widgets)
        
        # Groups submenu (manage groups of widgets)
        groups_menu = self.tray_menu.addMenu("Groups")

        manage_groups_action = QAction("Manage Groups...", self)
        manage_groups_action.triggered.connect(self._show_group_manager)
        groups_menu.addAction(manage_groups_action)

        # Quick show/hide groups if any exist
        existing_groups = list(self.widget_engine.groups.keys()) if self.widget_engine else []
        if existing_groups:
            groups_menu.addSeparator()
            for g in existing_groups:
                g_show = QAction(f"Show '{g}'", self)
                g_show.triggered.connect(lambda checked, gn=g: self.widget_engine.show_group(gn))
                groups_menu.addAction(g_show)

                g_hide = QAction(f"Hide '{g}'", self)
                g_hide.triggered.connect(lambda checked, gn=g: self.widget_engine.hide_group(gn))
                groups_menu.addAction(g_hide)
        self.tray_menu.addSeparator()
        
        # Settings submenu
        settings_menu = self.tray_menu.addMenu("Settings")
        
        # Theme selector
        theme_action = QAction("Change Theme", self)
        theme_action.triggered.connect(self._show_theme_selector)
        settings_menu.addAction(theme_action)
        
        # Global settings
        global_action = QAction("Global Settings", self)
        global_action.triggered.connect(self._show_global_settings)
        settings_menu.addAction(global_action)
        
        # Click-through toggle
        ct_action = QAction("Enable Click-Through", self)
        ct_action.setCheckable(True)
        ct_action.setChecked(self.settings.get("global", {}).get("click_through", False))
        ct_action.triggered.connect(lambda: self._toggle_click_through())
        settings_menu.addAction(ct_action)
        
        self.tray_menu.addSeparator()
        
        # Help/About
        help_action = QAction("Help", self)
        help_action.triggered.connect(self._show_help)
        self.tray_menu.addAction(help_action)
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self._show_about)
        self.tray_menu.addAction(about_action)
        
        self.tray_menu.addSeparator()
        
        # Quit
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.quit)
        self.tray_menu.addAction(quit_action)
    
    def _create_main_window(self):
        """Create the main management window."""
        from app.ui.main_window_ui import MainManagementWindow
        
        # MainManagementWindow expects a QWidget parent; QApplication is not valid as parent
        self.main_window = MainManagementWindow(
            parent=None,
            widget_engine=self.widget_engine,
            theme_manager=self.theme_manager
        )
        # Refresh groups UI immediately
        try:
            self.main_window.refresh_groups()
        except Exception:
            pass

        # Connect engine group change signal to persist and refresh UI
        try:
            self.widget_engine.groups_changed.connect(self._on_groups_changed)
        except Exception:
            pass
        # Connect widget add/remove signals so UI stays in sync
        try:
            self.widget_added.connect(self._on_widget_added)
        except Exception:
            pass

        try:
            self.widget_engine.widget_closed.connect(self._on_engine_widget_closed)
        except Exception:
            pass

        try:
            # If engine creates widgets directly, make sure the UI tracks them
            self.widget_engine.widget_created.connect(self._on_engine_widget_created)
        except Exception:
            pass

    def _on_groups_changed(self):
        """Handle groups changed: persist to settings and refresh UI/menu."""
        try:
            if isinstance(self.settings, dict) and self.widget_engine:
                self.settings.setdefault("groups", {})
                for name, members in self.widget_engine.groups.items():
                    self.settings["groups"][name] = list(members)
                # remove any stale groups
                for name in list(self.settings.get("groups", {}).keys()):
                    if name not in self.widget_engine.groups:
                        self.settings.get("groups", {}).pop(name, None)

                self._save_settings()
                # rebuild tray menu to reflect quick group actions
                try:
                    self._build_tray_menu()
                except Exception:
                    pass

                try:
                    if hasattr(self, 'main_window') and self.main_window:
                        self.main_window.refresh_groups()
                except Exception:
                    pass
        except Exception:
            logger.exception("Failed to persist groups on change")
    
    def _on_tray_activated(self, reason):
        """Handle tray icon activation."""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self._show_main_window()

    def _on_widget_added(self, widget_id: str):
        """Handle local widget_added signal: refresh UI lists."""
        try:
            if hasattr(self, 'main_window') and self.main_window:
                self.main_window.refresh_active_widgets()
                self.main_window.refresh_groups()
        except Exception:
            pass

    def _on_engine_widget_created(self, widget_id: str, widget: QWidget):
        """Engine reported a widget created (ensure main stores instance)."""
        try:
            self.widget_instances[widget_id] = widget
            if hasattr(self, 'main_window') and self.main_window:
                self.main_window.refresh_active_widgets()
        except Exception:
            pass

    def _on_engine_widget_closed(self, widget_id: str):
        """Engine reported a widget closed; remove references and refresh UI."""
        try:
            if widget_id in self.widget_instances:
                try:
                    self.widget_instances[widget_id].close()
                except Exception:
                    pass
                del self.widget_instances[widget_id]

            # ensure engine removal already happened; refresh UI
            if hasattr(self, 'main_window') and self.main_window:
                self.main_window.refresh_active_widgets()
                self.main_window.refresh_groups()

            # emit removal signal
            try:
                self.widget_removed.emit(widget_id)
            except Exception:
                pass
        except Exception:
            pass
    
    def _add_widget(self, widget_type: str):
        """Add a new widget."""
        widget_id = f"{widget_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Default widget configuration
        widget_config = {
            "type": widget_type,
            "name": WIDGET_REGISTRY.get(widget_type, {}).get("name", widget_type),
            "position": {"x": 100, "y": 100},
            "size": {"width": 300, "height": 200},
            "theme": self.settings.get("theme", "minimal_dark"),
            "settings": {}
        }
        
        # Save widget config
        if "widgets" not in self.settings:
            self.settings["widgets"] = {}
        self.settings["widgets"][widget_id] = widget_config
        self._save_settings()
        
        # Create widget instance
        self._create_widget_instance(widget_id, widget_config)
        
        # Emit signal
        self.widget_added.emit(widget_id)
        
        logger.info(f"Added widget: {widget_type} ({widget_id})")
    
    def _create_widget_instance(self, widget_id: str, config: dict):
        """Create a widget instance."""
        widget_type = config.get("type", "generic")
        position = config.get("position", {"x": 100, "y": 100})
        size = config.get("size", {"width": 300, "height": 200})
        
        # Create widget using engine
        widget = self.widget_engine.create_widget(
            widget_type=widget_type,
            widget_id=widget_id,
            position=QPoint(position.get("x", 100), position.get("y", 100)),
            size=QSize(size.get("width", 300), size.get("height", 200)),
            theme=self.theme_manager.current_theme
        )
        
        if widget:
            self.widget_instances[widget_id] = widget
            widget.show()
            
            # Restore settings
            widget.load_settings(config.get("settings", {}))
    
    def _show_widget(self, widget_id: str):
        """Show a specific widget."""
        if widget_id in self.widget_instances:
            widget = self.widget_instances[widget_id]
            widget.show()
            widget.raise_()
            widget.activateWindow()
    
    def _hide_all_widgets(self):
        """Hide all active widgets."""
        for widget in self.widget_instances.values():
            widget.hide()
    
    def _show_main_window(self):
        """Show the main management window."""
        self.main_window.show()
        self.main_window.raise_()
        self.main_window.activateWindow()
    
    def _show_theme_selector(self):
        """Show theme selection dialog."""
        themes = self.theme_manager.get_available_themes()
        
        dialog = QDialog(self.main_window)
        dialog.setWindowTitle("Select Theme")
        dialog.setMinimumWidth(300)
        
        layout = QVBoxLayout(dialog)
        
        label = QLabel("Choose a theme:")
        layout.addWidget(label)
        
        combo = QComboBox()
        for theme in themes:
            combo.addItem(theme)
        combo.setCurrentText(self.settings.get("theme", self.default_theme))
        layout.addWidget(combo)
        
        preview = QLabel()
        preview.setFixedHeight(100)
        preview.setStyleSheet("background-color: #2d2d2d; border-radius: 8px;")
        layout.addWidget(preview)
        
        def update_preview(index):
            theme_name = combo.currentText()
            theme = self.theme_manager.get_theme(theme_name)
            if theme:
                bg = theme.get("colors", {}).get("background", "#1a1a1a")
                preview.setStyleSheet(f"background-color: {bg}; border-radius: 8px;")
        
        combo.currentIndexChanged.connect(update_preview)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            theme_name = combo.currentText()
            self.settings["theme"] = theme_name
            self.theme_manager.load_theme(theme_name)
            self._apply_theme()
            self._save_settings()
            self.theme_changed.emit(theme_name)
            
            # Update all widgets
            for widget in self.widget_instances.values():
                widget.apply_theme(self.theme_manager.current_theme)
    
    def _show_global_settings(self):
        """Show global settings dialog."""
        dialog = QDialog(self.main_window)
        dialog.setWindowTitle("Global Settings")
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout(dialog)
        
        global_settings = self.settings.get("global", {})
        
        # Click-through
        ct_check = QCheckBox("Enable Click-Through Mode")
        ct_check.setChecked(global_settings.get("click_through", False))
        layout.addWidget(ct_check)
        
        # Always on top
        aot_check = QCheckBox("Always on Top")
        aot_check.setChecked(global_settings.get("always_on_top", True))
        layout.addWidget(aot_check)
        
        # Notifications
        notif_check = QCheckBox("Enable Notifications")
        notif_check.setChecked(global_settings.get("notifications_enabled", True))
        layout.addWidget(notif_check)
        
        # Animations
        anim_check = QCheckBox("Enable Animations")
        anim_check.setChecked(global_settings.get("animations_enabled", True))
        layout.addWidget(anim_check)
        
        # Snap to grid
        snap_check = QCheckBox("Snap to Grid")
        snap_check.setChecked(global_settings.get("snap_to_grid", True))
        layout.addWidget(snap_check)
        
        # Grid size
        grid_layout = QHBoxLayout()
        grid_label = QLabel("Grid Size:")
        grid_layout.addWidget(grid_label)
        grid_slider = QSlider(Qt.Orientation.Horizontal)
        grid_slider.setMinimum(10)
        grid_slider.setMaximum(100)
        grid_slider.setValue(global_settings.get("grid_size", 20))
        grid_layout.addWidget(grid_slider)
        grid_value = QLabel(str(global_settings.get("grid_size", 20)))
        grid_layout.addWidget(grid_value)
        grid_slider.valueChanged.connect(lambda v: grid_value.setText(str(v)))
        layout.addLayout(grid_layout)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.settings["global"] = {
                "click_through": ct_check.isChecked(),
                "always_on_top": aot_check.isChecked(),
                "notifications_enabled": notif_check.isChecked(),
                "animations_enabled": anim_check.isChecked(),
                "snap_to_grid": snap_check.isChecked(),
                "grid_size": grid_slider.value()
            }
            self._save_settings()
            self.settings_changed.emit(self.settings)

    def _show_group_manager(self):
        """Dialog to manage widget groups (create/delete/show/hide/add visible)."""
        dialog = QDialog(self.main_window)
        dialog.setWindowTitle("Manage Groups")
        dialog.setMinimumWidth(400)

        layout = QVBoxLayout(dialog)

        groups_label = QLabel("Groups:")
        layout.addWidget(groups_label)

        group_list = QListWidget()
        group_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)

        # Load groups from engine (or settings fallback)
        groups = list(self.widget_engine.groups.keys()) if self.widget_engine else []
        if not groups:
            # load from settings if present
            groups = list(self.settings.get("groups", {}).keys())

        for g in groups:
            group_list.addItem(g)

        layout.addWidget(group_list)

        btn_layout = QHBoxLayout()

        create_btn = QPushButton("Create Group")
        delete_btn = QPushButton("Delete Group")
        add_visible_btn = QPushButton("Add Visible Widgets")
        show_btn = QPushButton("Show Group")
        hide_btn = QPushButton("Hide Group")

        btn_layout.addWidget(create_btn)
        btn_layout.addWidget(delete_btn)
        btn_layout.addWidget(add_visible_btn)
        btn_layout.addWidget(show_btn)
        btn_layout.addWidget(hide_btn)

        layout.addLayout(btn_layout)

        close_buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        close_buttons.rejected.connect(dialog.reject)
        layout.addWidget(close_buttons)

        def create_group():
            text, ok = QInputDialog.getText(dialog, "Create Group", "Group name:")
            if ok and text:
                if self.widget_engine.create_group(text):
                    group_list.addItem(text)
                    # persist
                    self.settings.setdefault("groups", {})[text] = []
                    self._save_settings()

        def delete_group():
            item = group_list.currentItem()
            if not item:
                return
            name = item.text()
            if self.widget_engine.delete_group(name):
                row = group_list.currentRow()
                group_list.takeItem(row)
                self.settings.get("groups", {}).pop(name, None)
                self._save_settings()

        def add_visible_widgets():
            item = group_list.currentItem()
            if not item:
                return
            name = item.text()
            visible_ids = [wid for wid, w in self.widget_instances.items() if w.isVisible()]
            for wid in visible_ids:
                self.widget_engine.add_widget_to_group(name, wid)
            # persist
            self.settings.setdefault("groups", {})[name] = list(self.widget_engine.groups.get(name, []))
            self._save_settings()

        def show_group():
            item = group_list.currentItem()
            if not item:
                return
            name = item.text()
            self.widget_engine.show_group(name)

        def hide_group():
            item = group_list.currentItem()
            if not item:
                return
            name = item.text()
            self.widget_engine.hide_group(name)

        create_btn.clicked.connect(create_group)
        delete_btn.clicked.connect(delete_group)
        add_visible_btn.clicked.connect(add_visible_widgets)
        show_btn.clicked.connect(show_group)
        hide_btn.clicked.connect(hide_group)

        dialog.exec()
    
    def _toggle_click_through(self):
        """Toggle click-through mode for all widgets."""
        enabled = self.settings.get("global", {}).get("click_through", False)
        self.settings["global"]["click_through"] = not enabled
        self._save_settings()
        
        for widget in self.widget_instances.values():
            widget.set_click_through(not enabled)
        
        self._build_tray_menu()
    
    def _show_help(self):
        """Show help dialog."""
        help_text = """
        <h2>WidgetWall Help</h2>
        
        <h3>Adding Widgets</h3>
        <p>Click the menu bar icon and select "Add Widget"</p>
        
        <h3>Moving Widgets</h3>
        <p>Drag widgets by their title bar to reposition them.</p>
        
        <h3>Resizing Widgets</h3>
        <p>Use the resize handle in the bottom-right corner.</p>
        
        <h3>Click-Through Mode</h3>
        <p>Enable this in Settings to let clicks pass through widgets.</p>
        
        <h3>Customizing Widgets</h3>
        <p>Right-click on any widget to access its settings.</p>
        """
        
        dialog = QDialog(self.main_window)
        dialog.setWindowTitle("WidgetWall Help")
        dialog.setMinimumWidth(500)
        
        layout = QVBoxLayout(dialog)
        
        text = QLabel(help_text)
        text.setWordWrap(True)
        text.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(text)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        buttons.accepted.connect(dialog.accept)
        layout.addWidget(buttons)
        
        dialog.exec()
    
    def _show_about(self):
        """Show about dialog."""
        about_text = """
        <h2>WidgetWall</h2>
        <p><b>Version:</b> 1.0.0</p>
        <p><b>Description:</b> Premium desktop widgets for macOS 10.15+</p>
        <p><b>Features:</b></p>
        <ul>
            <li>13+ customizable widgets</li>
            <li>Premium features included free</li>
            <li>Minimalist design</li>
            <li>Works on macOS 10.15 through macOS 15</li>
        </ul>
        """
        
        dialog = QDialog(self.main_window)
        dialog.setWindowTitle("About WidgetWall")
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout(dialog)
        
        text = QLabel(about_text)
        text.setWordWrap(True)
        text.setTextFormat(Qt.TextFormat.RichText)
        text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(text)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        buttons.accepted.connect(dialog.accept)
        layout.addWidget(buttons)
        
        dialog.exec()
    
    def run(self) -> int:
        """Run the application."""
        self.is_running = True
        
        # Enter main event loop
        exit_code = self.exec()
        
        # Cleanup
        self._cleanup()
        
        return exit_code
    
    def _cleanup(self):
        """Cleanup on exit."""
        logger.info("Cleaning up application...")
        
        # Stop timers
        if hasattr(self, 'telemetry_timer') and self.telemetry_timer:
            self.telemetry_timer.stop()
            self.telemetry_timer.deleteLater()
            self.telemetry_timer = None
        
        # Save all widget positions
        for widget_id, widget in self.widget_instances.items():
            if hasattr(widget, 'position'):
                pos = widget.pos()
                size = widget.size()
                if widget_id in self.settings.get("widgets", {}):
                    self.settings["widgets"][widget_id]["position"] = {
                        "x": pos.x(),
                        "y": pos.y()
                    }
                    self.settings["widgets"][widget_id]["size"] = {
                        "width": size.width(),
                        "height": size.height()
                    }
        
        # Save settings
        self._save_settings()
        
        # Close all widgets
        for widget in list(self.widget_instances.values()):
            widget.close()
            widget.deleteLater()
        self.widget_instances.clear()
        
        # Terminate Swift helper if running
        if hasattr(self, 'swift_process') and self.swift_process:
            try:
                logger.info("Terminating native Swift helper background process...")
                if self.swift_process.stdin:
                    self.swift_process.stdin.close()
                self.swift_process.terminate()
                self.swift_process.wait(timeout=1)
            except Exception as e:
                logger.warning(f"Error terminating Swift helper: {e}")
            self.swift_process = None
            
        # Clean up UI components before QApplication destroys itself
        if hasattr(self, 'main_window') and self.main_window:
            self.main_window.close()
            self.main_window.deleteLater()
            self.main_window = None
            
        if hasattr(self, 'tray_icon') and self.tray_icon:
            self.tray_icon.hide()
            self.tray_icon.deleteLater()
            self.tray_icon = None
        
        logger.info("Application cleanup complete")
    
    def quit(self):
        """Quit the application."""
        # Confirm if widgets are active
        if self.widget_instances:
            msg = QMessageBox(self.main_window)
            msg.setWindowTitle("Quit WidgetWall?")
            msg.setText("Are you sure you want to quit WidgetWall?")
            msg.setInformativeText("All widgets will be closed.")
            msg.setIcon(QMessageBox.Icon.Question)
            msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            
            if msg.exec() != QMessageBox.StandardButton.Yes:
                return
        
        super().quit()

