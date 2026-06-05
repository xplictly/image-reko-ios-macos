"""
Base Widget Class for WidgetWall
All widget types inherit from this class
"""

import sys
from pathlib import Path
from typing import Dict, Optional, Any, List
from datetime import datetime

try:
    from PyQt6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
        QMenu, QSystemTrayIcon, QGraphicsDropShadowEffect,
        QDialog, QFormLayout, QSlider, QCheckBox, QComboBox, QSpinBox
    )
    from PyQt6.QtCore import (
        Qt, QSize, QPoint, QTimer, QPropertyAnimation, QEasingCurve,
        QRect, pyqtSignal, QObject, QParallelAnimationGroup
    )
    from PyQt6.QtGui import (
        QIcon, QPixmap, QColor, QPainter, QPen, QBrush, QFont,
        QAction, QCursor, QPalette, QLinearGradient, QRadialGradient,
        QGuiApplication, QScreen
    )
except ImportError:
    print("Error: PyQt6 is required. Install with: pip install PyQt6")
    sys.exit(1)


# Widget registry - all widgets must be registered here
WIDGET_REGISTRY = {
    "clock": {
        "name": "Clock",
        "icon": "🕐",
        "description": "Digital and analog clock widget",
        "category": "essentials",
        "premium": False,
        "min_size": (200, 150),
        "max_size": (500, 400)
    },
    "calendar": {
        "name": "Calendar",
        "icon": "📅",
        "description": "Monthly calendar view",
        "category": "essentials",
        "premium": False,
        "min_size": (250, 250),
        "max_size": (400, 400)
    },
    "weather": {
        "name": "Weather",
        "icon": "🌤️",
        "description": "Current weather and forecast",
        "category": "information",
        "premium": False,
        "min_size": (200, 150),
        "max_size": (400, 300)
    },
    "notes": {
        "name": "Notes",
        "icon": "📝",
        "description": "Quick notes widget",
        "category": "productivity",
        "premium": False,
        "min_size": (200, 150),
        "max_size": (400, 400)
    },
    "todo": {
        "name": "To-Do List",
        "icon": "✅",
        "description": "Task management with checkboxes",
        "category": "productivity",
        "premium": False,
        "min_size": (200, 200),
        "max_size": (400, 600)
    },
    "pomodoro": {
        "name": "Pomodoro",
        "icon": "🍅",
        "description": "Focus timer with breaks",
        "category": "productivity",
        "premium": False,
        "min_size": (250, 200),
        "max_size": (400, 300)
    },
    "stock": {
        "name": "Stock/Crypto",
        "icon": "📈",
        "description": "Real-time investment tracker",
        "category": "information",
        "premium": False,
        "min_size": (250, 150),
        "max_size": (400, 200)
    },
    "system": {
        "name": "System Monitor",
        "icon": "💻",
        "description": "CPU, RAM, and disk usage",
        "category": "information",
        "premium": False,
        "min_size": (200, 120),
        "max_size": (400, 300)
    },
    "battery": {
        "name": "Battery",
        "icon": "🔋",
        "description": "Battery status and health",
        "category": "information",
        "premium": False,
        "min_size": (150, 100),
        "max_size": (300, 200)
    },
    "music": {
        "name": "Music",
        "icon": "🎵",
        "description": "Music player controls",
        "category": "media",
        "premium": False,
        "min_size": (250, 120),
        "max_size": (400, 200)
    },
    "photo": {
        "name": "Photo Slideshow",
        "icon": "🖼️",
        "description": "Photo slideshow from a folder",
        "category": "media",
        "premium": False,
        "min_size": (250, 150),
        "max_size": (800, 600)
    },
    "calculator": {
        "name": "Calculator",
        "icon": "🔢",
        "description": "Functional calculator",
        "category": "tools",
        "premium": False,
        "min_size": (250, 350),
        "max_size": (400, 500)
    },
    "countdown": {
        "name": "Countdown",
        "icon": "⏳",
        "description": "Event countdown timer",
        "category": "productivity",
        "premium": False,
        "min_size": (250, 150),
        "max_size": (400, 200)
    },
    "photo": {
        "name": "Photo Frame",
        "icon": "🖼️",
        "description": "Photo slideshow widget",
        "category": "media",
        "premium": False,
        "min_size": (200, 200),
        "max_size": (600, 500)
    },
    "pinterest": {
        "name": "Pinterest",
        "icon": "📌",
        "description": "Pinterest board widget",
        "category": "media",
        "premium": False,
        "min_size": (200, 250),
        "max_size": (400, 400)
    },
    "quotes": {
        "name": "Quotes",
        "icon": "💬",
        "description": "Daily quotes widget",
        "category": "information",
        "premium": False,
        "min_size": (200, 100),
        "max_size": (400, 200)
    }
}


class WidgetSettingsDialog(QDialog):
    """Universal Settings Dialog for all Widgets."""
    def __init__(self, widget, parent=None):
        super().__init__(parent)
        self.widget = widget
        self.setWindowTitle(f"{widget.widget_name} Settings")
        self.setWindowFlags(Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)
        self.resize(300, 200)
        
        layout = QFormLayout(self)
        
        # Opacity slider
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(20, 100)
        self.opacity_slider.setValue(int(widget.settings.get("opacity", 1.0) * 100))
        self.opacity_slider.valueChanged.connect(self._on_opacity_changed)
        layout.addRow("Opacity:", self.opacity_slider)
        
        # Always on top check
        self.on_top_check = QCheckBox()
        self.on_top_check.setChecked(widget.settings.get("always_on_top", True))
        self.on_top_check.toggled.connect(self._on_top_toggled)
        layout.addRow("Always on Top:", self.on_top_check)
        
        # Lock position
        self.lock_check = QCheckBox()
        self.lock_check.setChecked(widget.settings.get("locked", False))
        self.lock_check.toggled.connect(self._on_lock_toggled)
        layout.addRow("Lock Position:", self.lock_check)
        
    def _on_opacity_changed(self, value):
        new_opacity = value / 100.0
        self.widget.settings["opacity"] = new_opacity
        self.widget.setWindowOpacity(new_opacity)
        self.widget.save_settings()
        
    def _on_top_toggled(self, checked):
        self.widget.settings["always_on_top"] = checked
        flags = self.widget.windowFlags()
        if checked:
            flags |= Qt.WindowType.WindowStaysOnTopHint
            if not self.widget.click_through_enabled:
                flags &= ~Qt.WindowType.TransparentForMouseEvents
        else:
            flags &= ~Qt.WindowType.WindowStaysOnTopHint
        self.widget.setWindowFlags(flags)
        
        self.widget.show()  # Required after flag change
        self.widget.save_settings()
        
    def _on_lock_toggled(self, checked):
        self.widget.settings["locked"] = checked
        self.widget.save_settings()


class BaseWidget(QWidget):
    """
    Base class for all widgets.
    Provides common functionality like drag, resize, settings, theming.
    """
    
    # Signals
    closed = pyqtSignal(str)  # Emitted when widget is closed
    moved = pyqtSignal(str, QPoint)  # Emitted when widget is moved
    resized = pyqtSignal(str, QSize)  # Emitted when widget is resized
    settings_changed = pyqtSignal(str, dict)  # Emitted when settings change
    duplicate_requested = pyqtSignal(str)  # Emitted when widget duplication is requested
    
    def __init__(
        self,
        widget_id: str,
        widget_type: str,
        position: QPoint,
        size: QSize,
        theme: Optional[Dict] = None,
        settings: Optional[Dict] = None,
        parent: Optional[QWidget] = None
    ):
        super().__init__(parent)
        
        # Widget identification
        self.widget_id = widget_id
        self.widget_type = widget_type
        self.widget_name = WIDGET_REGISTRY.get(widget_type, {}).get("name", widget_type)
        
        # Position and size
        self.target_position = position
        self.target_size = size
        
        # Theme and settings
        self.theme = theme or {}
        self.settings = settings or {}
        self.default_settings = self._get_default_settings()
        
        # Drag state
        self.dragging = False
        self.drag_position = QPoint()
        self.resizing = False
        self.resize_corner = 10  # Corner size for resize
        
        # Animation
        self.animation = None
        self.opacity_anim = None
        self.size_anim = None
        self.snap_anim = None
        
        # Click-through state
        self.click_through_enabled = False
        
        # Hover state
        self.hovered = False
        self.resize_edge = ""
        self.setMouseTracking(True)
        
        # Initialize
        self._init_ui()
        self._apply_theme()
        self._load_settings()
        self._setup_context_menu()
        
        # Set initial position and size
        self.move(self.target_position)
        self.resize(self.target_size)
        
        # Set window flags for frameless widget
        self._setup_window_flags()
    
    def _init_ui(self):
        """Initialize the widget UI. Override in subclasses."""
        pass
    
    def _get_default_settings(self) -> Dict:
        """Get default settings for this widget. Override in subclasses."""
        return {
            "show_title": True,
            "opacity": 1.0,
            "always_on_top": False,  # Default to true desktop widget (stays on bottom)
            "click_through": False,
            "locked": False
        }
    
    def _setup_window_flags(self):
        """Setup window flags for the widget."""
        # Frameless window
        flags = Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool
        
        # Apply floating or desktop pinned behavior
        if self.settings.get("always_on_top", False):
            flags |= Qt.WindowType.WindowStaysOnTopHint
        else:
            flags |= Qt.WindowType.WindowStaysOnBottomHint
            
        self.setWindowFlags(flags)
        
        # Enable transparency on macOS
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
    
    def _setup_context_menu(self):
        """Setup right-click context menu."""
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
    
    def _show_context_menu(self, position):
        """Show context menu at position."""
        menu = QMenu(self)
        
        # Add menu actions
        if self.click_through_enabled:
            disable_ct = QAction("Enable Mouse Interactions", self)
        else:
            disable_ct = QAction("Enable Click-Through", self)
        disable_ct.triggered.connect(self._toggle_click_through)
        menu.addAction(disable_ct)
        
        # Lock Action
        lock_action = QAction("Unlock Position" if self.settings.get("locked", False) else "Lock Position", self)
        lock_action.triggered.connect(self._toggle_lock)
        menu.addAction(lock_action)
        
        menu.addSeparator()
        
        # Settings
        settings_action = QAction("Settings...", self)
        settings_action.triggered.connect(self._show_settings)
        menu.addAction(settings_action)
        
        # Size submenu
        size_menu = menu.addMenu("Size")
        
        for size_name, size_dim in [
            ("Small", (200, 150)),
            ("Medium", (300, 200)),
            ("Large", (400, 300))
        ]:
            action = QAction(size_name, self)
            action.setData(size_dim)
            action.triggered.connect(lambda checked, s=size_dim: self._resize_animated(QSize(*s)))
            size_menu.addAction(action)
        
        menu.addSeparator()
        
        # Duplicate action
        duplicate_action = QAction("Duplicate Widget", self)
        duplicate_action.triggered.connect(lambda: self.duplicate_requested.emit(self.widget_id))
        menu.addAction(duplicate_action)
        
        # Close
        close_action = QAction("Close Widget", self)
        close_action.triggered.connect(self._close_widget)
        menu.addAction(close_action)
        
        # Show menu
        menu.exec(QCursor.pos())
    
    def _toggle_click_through(self):
        """Toggle click-through mode."""
        self.click_through_enabled = not self.click_through_enabled
        self.set_click_through(self.click_through_enabled)
    
    def set_click_through(self, enabled: bool):
        """Set click-through mode."""
        self.click_through_enabled = enabled
        
        if enabled:
            # Ignore mouse events
            self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        else:
            # Accept mouse events
            self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        
        # Save setting
        self.settings["click_through"] = enabled
    
    def _toggle_lock(self):
        """Toggle position lock."""
        is_locked = self.settings.get("locked", False)
        self.settings["locked"] = not is_locked
        self.save_settings()

    def _resize_animated(self, size: QSize):
        """Animate resizing."""
        self.size_anim = QPropertyAnimation(self, b"size")
        self.size_anim.setDuration(250)
        self.size_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.size_anim.setEndValue(size)
        self.size_anim.finished.connect(lambda: self.resized.emit(self.widget_id, self.size()))
        self.size_anim.start()

    def _show_settings(self):
        """Show widget settings dialog. Override in subclasses."""
        self.settings_dialog = WidgetSettingsDialog(self)
        self.settings_dialog.show()
    
    def _close_widget(self):
        """Close the widget and emit signal."""
        self.closed.emit(self.widget_id)
        self.close()
    
    def _apply_theme(self, theme: Optional[Dict] = None):
        """Apply theme colors to the widget."""
        if theme:
            self.theme = theme
        
        # Get colors from theme
        colors = self.theme.get("colors", {})
        
        bg_color = colors.get("background", "#1a1a1a")
        text_color = colors.get("text", "#ffffff")
        accent_color = colors.get("accent", "#007AFF")
        
        # Apply palette
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(bg_color))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(text_color))
        self.setPalette(palette)
        
        # Apply stylesheet
        border_radius = self.theme.get("border_radius", {}).get("md", 8)
        opacity = self.theme.get("opacity", {}).get("background", 0.85)
        
        css = f"""
        QWidget {{
            background-color: rgba({int(bg_color[1:3], 16)}, {int(bg_color[3:5], 16)}, {int(bg_color[5:7], 16)}, {int(opacity * 255)});
            color: {text_color};
            border-radius: {border_radius}px;
            font-family: -apple-system, sans-serif;
        }}
        """
        
        self.setStyleSheet(css)
    
    def apply_theme(self, theme: Dict):
        """Apply a new theme."""
        self._apply_theme(theme)
        self.update()
    
    def load_settings(self, settings: Optional[Dict] = None):
        """Public method to load settings."""
        self._load_settings(settings)
    
    def _load_settings(self, settings: Optional[Dict] = None):
        """Load widget settings."""
        if settings:
            self.settings = settings
        
        # Apply settings
        opacity = self.settings.get("opacity", 1.0)
        self.setWindowOpacity(opacity)
        
        click_through = self.settings.get("click_through", False)
        if click_through:
            self.set_click_through(True)
    
    def save_settings(self):
        """Save current settings."""
        # Override in subclasses to save widget-specific settings
        self.settings_changed.emit(self.widget_id, self.settings)
    
    def get_resize_edge(self, pos):
        """Determine which edge/corner the mouse is on for resizing."""
        margin = self.resize_corner
        w, h = self.width(), self.height()
        edge = ''
        if pos.y() <= margin: edge += 'top'
        elif pos.y() >= h - margin: edge += 'bottom'
        if pos.x() <= margin: edge += 'left'
        elif pos.x() >= w - margin: edge += 'right'
        return edge

    def update_cursor_shape(self, edge):
        """Update the cursor shape based on hover edge."""
        if not edge:
            self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        elif edge in ('topleft', 'bottomright'):
            self.setCursor(QCursor(Qt.CursorShape.SizeFDiagCursor))
        elif edge in ('topright', 'bottomleft'):
            self.setCursor(QCursor(Qt.CursorShape.SizeBDiagCursor))
        elif edge in ('left', 'right'):
            self.setCursor(QCursor(Qt.CursorShape.SizeHorCursor))
        elif edge in ('top', 'bottom'):
            self.setCursor(QCursor(Qt.CursorShape.SizeVerCursor))

    def mousePressEvent(self, event):
        """Handle mouse press for drag/resize."""
        if event.button() == Qt.MouseButton.LeftButton:
            edge = self.get_resize_edge(event.pos())
            if edge:
                self.resizing = True
                self.resize_edge = edge
                self.resize_start = event.globalPosition().toPoint()
                self.resize_initial_rect = self.geometry()
            elif not self.settings.get("locked", False):
                self.dragging = True
                self.drag_position = event.globalPosition().toPoint() - self.pos()
                self.setCursor(QCursor(Qt.CursorShape.ClosedHandCursor))
    
    def mouseMoveEvent(self, event):
        """Handle mouse move for drag/resize."""
        if self.dragging:
            # Move widget
            new_pos = event.globalPosition().toPoint() - self.drag_position
            self.move(new_pos)
        
        elif self.resizing:
            # Resize widget according to active edge
            r = QRect(self.resize_initial_rect)
            delta = event.globalPosition().toPoint() - self.resize_start
            
            if 'left' in self.resize_edge:
                r.setLeft(r.left() + delta.x())
            elif 'right' in self.resize_edge:
                r.setRight(r.right() + delta.x())
            if 'top' in self.resize_edge:
                r.setTop(r.top() + delta.y())
            elif 'bottom' in self.resize_edge:
                r.setBottom(r.bottom() + delta.y())
                
            # Restrict by minimum size bounds
            min_size = self.minimumSize()
            
            if r.width() < min_size.width():
                if 'left' in self.resize_edge: r.setLeft(r.right() - min_size.width())
                else: r.setRight(r.left() + min_size.width())
            
            if r.height() < min_size.height():
                if 'top' in self.resize_edge: r.setTop(r.bottom() - min_size.height())
                else: r.setBottom(r.top() + min_size.height())
                
            self.setGeometry(r)
        else:
            # Manage hover cursor updates
            if not self.click_through_enabled:
                edge = self.get_resize_edge(event.pos())
                self.update_cursor_shape(edge)
                if not self.hovered:
                    self.hovered = True
                    self.update()
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release and perform screen snapping."""
        if self.dragging:
            self.dragging = False
            self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
            
            # Edge Snap feature
            screen = QGuiApplication.primaryScreen().availableGeometry()
            pos = self.pos()
            new_x, new_y = pos.x(), pos.y()
            snap_margin = 25
            
            if pos.x() < snap_margin: new_x = 0
            elif (pos.x() + self.width()) > screen.width() - snap_margin: new_x = screen.width() - self.width()
            
            if pos.y() < snap_margin: new_y = 0
            elif (pos.y() + self.height()) > screen.height() - snap_margin: new_y = screen.height() - self.height()
            
            if new_x != pos.x() or new_y != pos.y():
                self.snap_anim = QPropertyAnimation(self, b"pos")
                self.snap_anim.setDuration(150)
                self.snap_anim.setEasingCurve(QEasingCurve.Type.OutQuad)
                self.snap_anim.setEndValue(QPoint(new_x, new_y))
                self.snap_anim.finished.connect(lambda: self.moved.emit(self.widget_id, self.pos()))
                self.snap_anim.start()
            else:
                self.moved.emit(self.widget_id, self.pos())
        
        elif self.resizing:
            self.resizing = False
            self.resized.emit(self.widget_id, self.size())
            self.update_cursor_shape(self.get_resize_edge(event.pos()))
    
    def enterEvent(self, event):
        """Handle mouse enter."""
        if not self.click_through_enabled:
            self.hovered = True
            self.update()
    
    def leaveEvent(self, event):
        """Handle mouse leave."""
        if not self.click_through_enabled:
            self.hovered = False
            self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
            self.update()
    
    def paintEvent(self, event):
        """Custom paint event for background and dynamic hover headers."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        colors = self.theme.get("colors", {})
        bg_color = QColor(colors.get("background", "#1a1a1a"))
        border_color = QColor(colors.get("border", "#3d3d3d"))
        border_radius = self.theme.get("border_radius", {}).get("md", 8)
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(bg_color))
        painter.drawRoundedRect(self.rect(), border_radius, border_radius)
        
        painter.setPen(QPen(border_color, 1))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(self.rect().adjusted(0, 0, -1, -1), border_radius, border_radius)
        
        # Draw hover header 
        if self.hovered and not self.resizing and not self.dragging and not self.click_through_enabled:
            header_rect = QRect(0, 0, self.width(), 30)
            gradient = QLinearGradient(0, 0, 0, 30)
            gradient.setColorAt(0, QColor(0, 0, 0, 40))
            gradient.setColorAt(1, QColor(0, 0, 0, 0))
            painter.fillRect(header_rect, gradient)
            
            painter.setPen(QPen(QColor(255, 255, 255, 180)))
            font = QFont("-apple-system", 10, QFont.Weight.Bold)
            painter.setFont(font)
            painter.drawText(header_rect.adjusted(12, 0, -12, 0), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, self.widget_name)
    
    def closeEvent(self, event):
        """Handle close event."""
        self.save_settings()
        super().closeEvent(event)
    
    def showEvent(self, event):
        """Handle show event with fade-in."""
        super().showEvent(event)
        self.raise_()
        
        # Initial fade-in animation
        self.opacity_anim = QPropertyAnimation(self, b"windowOpacity")
        self.opacity_anim.setDuration(300)
        self.opacity_anim.setStartValue(0.0)
        self.opacity_anim.setEndValue(self.settings.get("opacity", 1.0))
        self.opacity_anim.start()
    
    def update_content(self):
        """Update widget content. Override in subclasses."""
        pass
    
    def set_refresh_rate(self, milliseconds: int):
        """Set auto-refresh rate in milliseconds. 0 to disable."""
        if hasattr(self, '_refresh_timer'):
            if milliseconds > 0:
                self._refresh_timer.start(milliseconds)
            else:
                self._refresh_timer.stop()
    
    def _start_refresh_timer(self, interval: int = 1000):
        """Start a refresh timer for automatic updates."""
        self._refresh_timer = QTimer(self)
        self._refresh_timer.timeout.connect(self.update_content)
        self._refresh_timer.start(interval)


class ClockWidget(BaseWidget):
    """Clock widget with digital and analog display."""
    
    def _get_default_settings(self) -> Dict:
        return {
            **super()._get_default_settings(),
            "clock_type": "digital",  # digital, analog
            "show_seconds": True,
            "show_date": True,
            "font_size": 48,
            "font_family": "-apple-system"
        }
    
    def _init_ui(self):
        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        
        # Time label
        self.time_label = QLabel()
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setPointSize(self.settings.get("font_size", 48))
        font.setFamily(self.settings.get("font_family", "-apple-system"))
        self.time_label.setFont(font)
        
        layout.addWidget(self.time_label)
        
        # Date label
        self.date_label = QLabel()
        self.date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        date_font = QFont()
        date_font.setPointSize(14)
        self.date_label.setFont(date_font)
        
        layout.addWidget(self.date_label)
        
        self.setLayout(layout)
        
        # Start update timer
        self._start_refresh_timer(1000)
        self.update_content()
    
    def update_content(self):
        """Update clock display."""
        from datetime import datetime
        
        now = datetime.now()
        
        # Format time
        time_format = "%H:%M"
        if self.settings.get("show_seconds", True):
            time_format += ":%S"
        
        self.time_label.setText(now.strftime(time_format))
        
        # Format date
        if self.settings.get("show_date", True):
            self.date_label.setText(now.strftime("%A, %B %d"))
        else:
            self.date_label.setText("")


class CalendarWidget(BaseWidget):
    """Monthly calendar widget."""
    
    def _get_default_settings(self) -> Dict:
        return {
            **super()._get_default_settings(),
            "show_week_numbers": False,
            "first_day_monday": False
        }
    
    def _init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(5)
        
        # Month/year header
        self.header_label = QLabel()
        self.header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_font = QFont()
        header_font.setPointSize(16)
        header_font.setBold(True)
        self.header_label.setFont(header_font)
        layout.addWidget(self.header_label)
        
        # Days grid
        self.days_label = QLabel()
        self.days_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.days_label)
        
        self.setLayout(layout)
        
        # Start update timer
        self._start_refresh_timer(60000)  # Update every minute
        self.update_content()
    
    def update_content(self):
        """Update calendar display."""
        from datetime import datetime
        import calendar
        
        now = datetime.now()
        
        # Header
        self.header_label.setText(now.strftime("%B %Y"))
        
        # Days header
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        if not self.settings.get("first_day_monday", False):
            days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        
        days_text = "  ".join(days)
        self.days_label.setText(days_text)
    
    def paintEvent(self, event):
        """Custom paint with calendar grid."""
        super().paintEvent(event)
        
        # Could add calendar grid drawing here


class NotesWidget(BaseWidget):
    """Notes widget with editable text."""
    
    def _get_default_settings(self) -> Dict:
        return {
            **super()._get_default_settings(),
            "content": "",
            "font_size": 14,
            "word_wrap": True
        }
    
    def _init_ui(self):
        from PyQt6.QtWidgets import QTextEdit
        
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Text edit
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Type your note here...")
        self.text_edit.setText(self.settings.get("content", ""))
        
        font = QFont()
        font.setPointSize(self.settings.get("font_size", 14))
        self.text_edit.setFont(font)
        
        if self.settings.get("word_wrap", True):
            self.text_edit.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        else:
            self.text_edit.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        
        layout.addWidget(self.text_edit)
        
        self.setLayout(layout)
        
        # Connect text change to save
        self.text_edit.textChanged.connect(self._save_content)
    
    def _save_content(self):
        """Save note content."""
        self.settings["content"] = self.text_edit.toPlainText()
    
    def update_content(self):
        """Update note display."""
        pass


class WeatherWidget(BaseWidget):
    """Weather widget showing current conditions."""
    
    def _get_default_settings(self) -> Dict:
        return {
            **super()._get_default_settings(),
            "location": "Current Location",
            "units": "celsius",  # celsius, fahrenheit
            "show_forecast": True
        }
    
    def _init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Location label
        self.location_label = QLabel()
        self.location_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.location_label.setFont(font)
        layout.addWidget(self.location_label)
        
        # Temperature label
        self.temp_label = QLabel()
        self.temp_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setPointSize(36)
        font.setBold(True)
        self.temp_label.setFont(font)
        layout.addWidget(self.temp_label)
        
        # Condition label
        self.condition_label = QLabel()
        self.condition_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.condition_label)
        
        self.setLayout(layout)
        
        # Start update timer (update every 30 minutes)
        self._start_refresh_timer(1800000)
        self.update_content()
    
    def update_content(self):
        """Update weather display using Open-Meteo (free) when possible."""
        from app.premium.premium_features import schedule_automation_task
        import requests

        # Determine coordinates
        lat = self.settings.get("latitude")
        lon = self.settings.get("longitude")

        if lat is None or lon is None:
            # Try IP-based geolocation as a fallback
            try:
                resp = requests.get("http://ip-api.com/json", timeout=5)
                if resp.status_code == 200:
                    data = resp.json()
                    lat = data.get("lat")
                    lon = data.get("lon")
                    city = data.get("city")
                    self.location_label.setText(city or self.settings.get("location", "Location"))
            except Exception:
                self.location_label.setText(self.settings.get("location", "Location"))

        try:
            if lat is None or lon is None:
                self.temp_label.setText("--°")
                self.condition_label.setText("Location unknown")
                return

            units = self.settings.get("units", "celsius")
            temp_unit = "celsius" if units == "celsius" else "fahrenheit"
            params = {
                "latitude": lat,
                "longitude": lon,
                "current_weather": True,
                "temperature_unit": temp_unit
            }
            r = requests.get("https://api.open-meteo.com/v1/forecast", params=params, timeout=6)
            if r.status_code == 200:
                d = r.json()
                cw = d.get("current_weather", {})
                temp = cw.get("temperature")
                wind = cw.get("windspeed")
                # Open-Meteo provides weathercode; we map a few codes to text
                code = cw.get("weathercode")
                cond = {
                    0: "Clear",
                    1: "Mainly clear",
                    2: "Partly cloudy",
                    3: "Overcast",
                    45: "Fog",
                    48: "Depositing rime fog",
                    51: "Light drizzle",
                    61: "Slight rain",
                    63: "Moderate rain",
                    71: "Snow"
                }.get(code, "")
                if temp is not None:
                    self.temp_label.setText(f"{int(round(temp))}°")
                else:
                    self.temp_label.setText("--°")

                self.condition_label.setText(f"{cond} {'' if wind is None else f'• {int(wind)} km/h'}")
            else:
                self.temp_label.setText("--°")
                self.condition_label.setText("Weather API error")
        except Exception as e:
            self.temp_label.setText("--°")
            self.condition_label.setText("Error")


class SystemWidget(BaseWidget):
    """System monitor widget (CPU, RAM)."""
    
    def _get_default_settings(self) -> Dict:
        return {
            **super()._get_default_settings(),
            "show_cpu": True,
            "show_memory": True,
            "show_battery": False,
            "refresh_interval": 2000
        }
    
    def _init_ui(self):
        from PyQt6.QtWidgets import QProgressBar
        
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # CPU section
        if self.settings.get("show_cpu", True):
            cpu_layout = QHBoxLayout()
            cpu_label = QLabel("CPU:")
            self.cpu_bar = QProgressBar()
            self.cpu_bar.setMaximum(100)
            self.cpu_bar.setTextVisible(True)
            cpu_layout.addWidget(cpu_label)
            cpu_layout.addWidget(self.cpu_bar)
            layout.addLayout(cpu_layout)
        
        # Memory section
        if self.settings.get("show_memory", True):
            mem_layout = QHBoxLayout()
            mem_label = QLabel("RAM:")
            self.mem_bar = QProgressBar()
            self.mem_bar.setMaximum(100)
            self.mem_bar.setTextVisible(True)
            mem_layout.addWidget(mem_label)
            mem_layout.addWidget(self.mem_bar)
            layout.addLayout(mem_layout)
        
        self.setLayout(layout)
        
        # Start update timer
        interval = self.settings.get("refresh_interval", 2000)
        self._start_refresh_timer(interval)
        self.update_content()
    
    def update_content(self):
        """Update system metrics."""
        from app.native.macos_utils import get_cpu_usage, get_memory_usage
        
        # CPU
        if hasattr(self, 'cpu_bar'):
            cpu = get_cpu_usage()
            self.cpu_bar.setValue(int(cpu))
        
        # Memory
        if hasattr(self, 'mem_bar'):
            mem = get_memory_usage()
            self.mem_bar.setValue(int(mem.get("used_percent", 0)))


class QuotesWidget(BaseWidget):
    """Quotes widget displaying random quotes."""
    
    QUOTES = [
        ("The only way to do great work is to love what you do.", "Steve Jobs"),
        ("In the middle of difficulty lies opportunity.", "Albert Einstein"),
        ("Believe you can and you're halfway there.", "Theodore Roosevelt"),
        ("The future belongs to those who believe in the beauty of their dreams.", "Eleanor Roosevelt"),
        ("It does not matter how slowly you go as long as you do not stop.", "Confucius"),
        ("The only impossible journey is the one you never begin.", "Tony Robbins"),
        ("Success is not final, failure is not fatal.", "Winston Churchill"),
        ("Your time is limited, so don't waste it living someone else's life.", "Steve Jobs")
    ]
    
    def _get_default_settings(self) -> Dict:
        return {
            **super()._get_default_settings(),
            "show_author": True,
            "auto_rotate": True,
            "rotate_interval": 3600000  # 1 hour
        }
    
    def _init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        
        # Quote text
        self.quote_label = QLabel()
        self.quote_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.quote_label.setWordWrap(True)
        
        font = QFont()
        font.setPointSize(14)
        self.quote_label.setFont(font)
        layout.addWidget(self.quote_label)
        
        # Author label
        self.author_label = QLabel()
        self.author_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.author_label)
        
        self.setLayout(layout)
        
        # Start update timer if auto-rotate is enabled
        if self.settings.get("auto_rotate", True):
            interval = self.settings.get("rotate_interval", 3600000)
            self._start_refresh_timer(interval)
        
        self.update_content()
    
    def update_content(self):
        """Update quote display."""
        import random
        
        quote, author = random.choice(self.QUOTES)
        
        self.quote_label.setText(f'"{quote}"')
        
        if self.settings.get("show_author", True):
            self.author_label.setText(f"- {author}")
        else:
            self.author_label.setText("")


# Factory function to create widgets
def create_widget(widget_type: str, **kwargs) -> Optional[BaseWidget]:
    """Factory function to create a widget by type."""
    
    widget_classes = {
        "clock": ClockWidget,
        "calendar": CalendarWidget,
        "notes": NotesWidget,
        "weather": WeatherWidget,
        "system": SystemWidget,
        "quotes": QuotesWidget,
        "todo": __import__("app.widgets.todo_widget", fromlist=["TodoWidget"]).TodoWidget,
        "pomodoro": __import__("app.widgets.pomodoro_widget", fromlist=["PomodoroWidget"]).PomodoroWidget,
        "stock": __import__("app.widgets.stock_widget", fromlist=["StockWidget"]).StockWidget,
        "calculator": __import__("app.widgets.calculator_widget", fromlist=["CalculatorWidget"]).CalculatorWidget,
        "countdown": __import__("app.widgets.countdown_widget", fromlist=["CountdownWidget"]).CountdownWidget,
        # New widgets
        "photo": __import__("app.widgets.photo_widget", fromlist=["PhotoWidget"]).PhotoWidget,
        "music": __import__("app.widgets.music_widget", fromlist=["MusicWidget"]).MusicWidget
    }
    
    widget_class = widget_classes.get(widget_type)
    
    if widget_class:
        return widget_class(widget_type=widget_type, **kwargs)
    
    return None


