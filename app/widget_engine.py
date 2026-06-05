"""
Widget Engine - Manages widget creation and lifecycle
"""

import sys
from pathlib import Path
from typing import Dict, Optional, List, Any
from datetime import datetime

try:
    from PyQt6.QtCore import QPoint, QSize, Qt, pyqtSignal, QObject
    from PyQt6.QtWidgets import QWidget, QApplication
except ImportError:
    print("Error: PyQt6 is required. Install with: pip install PyQt6")
    sys.exit(1)

from app.utils.logger import logger
from app.widgets.base_widget import BaseWidget, WIDGET_REGISTRY, create_widget


class WidgetEngine(QObject):
    """
    Engine for managing widget creation, positioning, and lifecycle.
    """
    
    widget_created = pyqtSignal(str, QWidget)  # widget_id, widget
    widget_closed = pyqtSignal(str)  # widget_id
    widget_moved = pyqtSignal(str, QPoint)  # widget_id, position
    widget_resized = pyqtSignal(str, QSize)  # widget_id, size
    # Signal emitted when groups change (create/delete/add/remove)
    groups_changed = pyqtSignal()
    
    def __init__(
        self,
        parent: QWidget,
        config_dir: Path = Path("data"),
        theme_manager = None,
        settings: Dict = {}
    ):
        super().__init__(parent)
        
        self.parent = parent
        self.config_dir = config_dir
        self.theme_manager = theme_manager
        self.settings = settings
        
        # Widget registry
        self.widgets: Dict[str, BaseWidget] = {}

        # Widget groups: group_name -> set(widget_id)
        self.groups: Dict[str, set] = {}

        # Available widget types
        self.available_widgets = WIDGET_REGISTRY
        
        # Grid settings for snap-to-grid
        self.snap_to_grid = settings.get("global", {}).get("snap_to_grid", True)
        self.grid_size = settings.get("global", {}).get("grid_size", 20)
        
        # Click-through default
        self.default_click_through = settings.get("global", {}).get("click_through", False)
        
        logger.info("WidgetEngine initialized")
        # Load groups from provided settings if present
        try:
            groups_conf = settings.get("groups", {}) if isinstance(settings, dict) else {}
            for g, members in groups_conf.items():
                self.groups[g] = set(members or [])
        except Exception:
            # ignore malformed groups config
            pass
    
    def create_widget(
        self,
        widget_type: str,
        widget_id: str,
        position: QPoint,
        size: QSize,
        theme: Optional[Dict] = None,
        settings: Optional[Dict] = None
    ) -> Optional[BaseWidget]:
        """
        Create a new widget instance.
        
        Args:
            widget_type: Type of widget to create
            widget_id: Unique identifier for the widget
            position: Initial position
            size: Initial size
            theme: Theme colors to apply
            settings: Widget-specific settings
        
        Returns:
            Created widget instance or None if failed
        """
        try:
            # Get widget configuration
            widget_info = self.available_widgets.get(widget_type, {})
            
            # Get theme
            widget_theme = theme or (self.theme_manager.current_theme if self.theme_manager else {})
            
            # Get settings
            widget_settings = settings or {}
            
            # Create widget using factory
            widget = create_widget(
                widget_type=widget_type,
                widget_id=widget_id,
                position=position,
                size=size,
                theme=widget_theme,
                settings=widget_settings
            )
            
            if widget:
                # Connect signals
                widget.closed.connect(self._on_widget_closed)
                widget.moved.connect(self._on_widget_moved)
                widget.resized.connect(self._on_widget_resized)
                
                # Store widget
                self.widgets[widget_id] = widget
                
                # Apply snap-to-grid if enabled
                if self.snap_to_grid:
                    self._snap_to_grid(widget)
                
                # Apply click-through if default enabled
                if self.default_click_through:
                    widget.set_click_through(True)
                
                # Emit signal
                self.widget_created.emit(widget_id, widget)
                
                logger.info(f"Created widget: {widget_type} ({widget_id})")
                return widget
            else:
                logger.error(f"Failed to create widget: {widget_type}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating widget {widget_type}: {e}", exc_info=True)
            return None
    
    def _on_widget_closed(self, widget_id: str):
        """Handle widget closed signal."""
        if widget_id in self.widgets:
            del self.widgets[widget_id]
            self.widget_closed.emit(widget_id)
            logger.info(f"Widget closed: {widget_id}")
    
    def _on_widget_moved(self, widget_id: str, position: QPoint):
        """Handle widget moved signal."""
        if self.snap_to_grid and widget_id in self.widgets:
            self._snap_to_grid(self.widgets[widget_id])
        
        self.widget_moved.emit(widget_id, position)
    
    def _on_widget_resized(self, widget_id: str, size: QSize):
        """Handle widget resized signal."""
        self.widget_resized.emit(widget_id, size)
    
    def _snap_to_grid(self, widget: QWidget):
        """Snap widget position to grid."""
        pos = widget.pos()
        x = round(pos.x() / self.grid_size) * self.grid_size
        y = round(pos.y() / self.grid_size) * self.grid_size
        widget.move(int(x), int(y))
    
    def close_widget(self, widget_id: str) -> bool:
        """Close a specific widget."""
        if widget_id in self.widgets:
            widget = self.widgets[widget_id]
            widget.close()
            return True
        return False
    
    def close_all_widgets(self):
        """Close all active widgets."""
        for widget in list(self.widgets.values()):
            widget.close()
        self.widgets.clear()
        logger.info("All widgets closed")
    
    def show_widget(self, widget_id: str):
        """Show a specific widget."""
        if widget_id in self.widgets:
            widget = self.widgets[widget_id]
            widget.show()
            widget.raise_()
    
    def hide_widget(self, widget_id: str):
        """Hide a specific widget."""
        if widget_id in self.widgets:
            self.widgets[widget_id].hide()
    
    def show_all_widgets(self):
        """Show all widgets."""
        for widget in self.widgets.values():
            widget.show()
            widget.raise_()
    
    def hide_all_widgets(self):
        """Hide all widgets."""
        for widget in self.widgets.values():
            widget.hide()
    
    def toggle_widgets_visibility(self):
        """Toggle visibility of all widgets."""
        visible = any(w.isVisible() for w in self.widgets.values())
        
        if visible:
            self.hide_all_widgets()
        else:
            self.show_all_widgets()
    
    def get_widget_position(self, widget_id: str) -> Optional[QPoint]:
        """Get widget position."""
        if widget_id in self.widgets:
            return self.widgets[widget_id].pos()
        return None
    
    def set_widget_position(self, widget_id: str, position: QPoint):
        """Set widget position."""
        if widget_id in self.widgets:
            widget = self.widgets[widget_id]
            
            if self.snap_to_grid:
                x = round(position.x() / self.grid_size) * self.grid_size
                y = round(position.y() / self.grid_size) * self.grid_size
                widget.move(int(x), int(y))
            else:
                widget.move(position)
    
    def get_widget_size(self, widget_id: str) -> Optional[QSize]:
        """Get widget size."""
        if widget_id in self.widgets:
            return self.widgets[widget_id].size()
        return None
    
    def set_widget_size(self, widget_id: str, size: QSize):
        """Set widget size."""
        if widget_id in self.widgets:
            self.widgets[widget_id].resize(size)
    
    def get_all_widgets(self) -> Dict[str, BaseWidget]:
        """Get all active widgets."""
        return self.widgets.copy()
    
    def get_widget_count(self) -> int:
        """Get number of active widgets."""
        return len(self.widgets)
    
    def apply_theme_to_all(self, theme: Dict):
        """Apply theme to all widgets."""
        for widget in self.widgets.values():
            widget.apply_theme(theme)
        logger.info("Applied theme to all widgets")
    
    def set_click_through_all(self, enabled: bool):
        """Set click-through mode for all widgets."""
        for widget in self.widgets.values():
            widget.set_click_through(enabled)
        logger.info(f"Set click-through for all widgets: {enabled}")
    
    def save_widget_positions(self) -> Dict[str, Dict]:
        """Save all widget positions and sizes."""
        positions = {}
        
        for widget_id, widget in self.widgets.items():
            pos = widget.pos()
            size = widget.size()
            
            positions[widget_id] = {
                "position": {
                    "x": pos.x(),
                    "y": pos.y()
                },
                "size": {
                    "width": size.width(),
                    "height": size.height()
                },
                "settings": widget.settings
            }
        
        return positions
    
    def restore_widget_positions(self, positions: Dict[str, Dict]):
        """Restore widget positions from saved data."""
        for widget_id, data in positions.items():
            pos_data = data.get("position", {"x": 100, "y": 100})
            size_data = data.get("size", {"width": 300, "height": 200})
            settings = data.get("settings", {})
            
            # Create widget at saved position
            # This should be called during app startup
            logger.info(f"Restoring widget {widget_id} position")
    
    def get_available_widgets(self) -> Dict[str, Dict]:
        """Get list of available widget types."""
        return self.available_widgets
    
    def get_widget_info(self, widget_type: str) -> Optional[Dict]:
        """Get information about a specific widget type."""
        return self.available_widgets.get(widget_type)
    
    def get_widget_categories(self) -> List[str]:
        """Get list of widget categories."""
        categories = set()
        for widget_info in self.available_widgets.values():
            categories.add(widget_info.get("category", "other"))
        return sorted(list(categories))
    
    def get_widgets_by_category(self, category: str) -> Dict[str, Dict]:
        """Get widgets filtered by category."""
        return {
            name: info
            for name, info in self.available_widgets.items()
            if info.get("category") == category
        }

    # Group management
    def create_group(self, group_name: str) -> bool:
        if group_name in self.groups:
            return False
        self.groups[group_name] = set()
        logger.info(f"Created group: {group_name}")
        # persist
        try:
            if isinstance(self.settings, dict):
                self.settings.setdefault("groups", {})[group_name] = []
        except Exception:
            pass
        self.groups_changed.emit()
        return True

    def delete_group(self, group_name: str) -> bool:
        if group_name in self.groups:
            del self.groups[group_name]
            logger.info(f"Deleted group: {group_name}")
            # persist
            try:
                if isinstance(self.settings, dict):
                    self.settings.get("groups", {}).pop(group_name, None)
            except Exception:
                pass
            self.groups_changed.emit()
            return True
        return False

    def add_widget_to_group(self, group_name: str, widget_id: str) -> bool:
        if group_name not in self.groups:
            self.create_group(group_name)
        self.groups[group_name].add(widget_id)
        logger.info(f"Added widget {widget_id} to group {group_name}")
        # persist
        try:
            if isinstance(self.settings, dict):
                self.settings.setdefault("groups", {})[group_name] = list(self.groups[group_name])
        except Exception:
            pass
        self.groups_changed.emit()
        return True

    def remove_widget_from_group(self, group_name: str, widget_id: str) -> bool:
        if group_name in self.groups and widget_id in self.groups[group_name]:
            self.groups[group_name].remove(widget_id)
            logger.info(f"Removed widget {widget_id} from group {group_name}")
            # persist
            try:
                if isinstance(self.settings, dict):
                    self.settings.setdefault("groups", {})[group_name] = list(self.groups.get(group_name, []))
            except Exception:
                pass
            self.groups_changed.emit()
            return True
        return False

    def show_group(self, group_name: str):
        if group_name not in self.groups:
            return
        for wid in self.groups[group_name]:
            if wid in self.widgets:
                self.widgets[wid].show()

    def hide_group(self, group_name: str):
        if group_name not in self.groups:
            return
        for wid in self.groups[group_name]:
            if wid in self.widgets:
                self.widgets[wid].hide()
    
    def export_configuration(self) -> Dict:
        """Export current widget configuration."""
        return {
            "timestamp": datetime.now().isoformat(),
            "widget_count": self.get_widget_count(),
            "positions": self.save_widget_positions(),
            "settings": self.settings
        }
    
    def import_configuration(self, config: Dict) -> bool:
        """Import widget configuration."""
        try:
            positions = config.get("positions", {})
            self.restore_widget_positions(positions)
            return True
        except Exception as e:
            logger.error(f"Failed to import configuration: {e}")
            return False


