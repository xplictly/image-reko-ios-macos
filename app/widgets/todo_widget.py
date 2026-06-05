"""
Interactive To-Do Widget
Manage tasks with checkboxes.
"""
from typing import Dict, List, Optional, Any

from PyQt6.QtWidgets import (
    QLabel, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLineEdit, QListWidget, QListWidgetItem, QCheckBox,
    QWidget, QMenu
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QColor, QAction, QCursor

from app.widgets.base_widget import BaseWidget


class TodoWidget(BaseWidget):
    """Interactive To-Do List Widget."""
    
    def _get_default_settings(self) -> Dict:
        return {
            **super()._get_default_settings(),
            "items": [],  # List of {"text": str, "checked": bool}
            "show_completed": True
        }
    
    def _init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 35, 10, 10)
        layout.setSpacing(5)
        
        # Input area
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Add a task...")
        self.input_field.returnPressed.connect(self.add_item)
        
        add_btn = QPushButton("+")
        add_btn.setFixedSize(30, 30)
        add_btn.clicked.connect(self.add_item)
        
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(add_btn)
        layout.addLayout(input_layout)
        
        # List
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("background: transparent; border: none;")
        self.list_widget.setSelectionMode(QListWidget.SelectionMode.NoSelection)
        self.list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self.show_item_context_menu)
        layout.addWidget(self.list_widget)
        
        self.setLayout(layout)
        
        self.load_items()

    def load_items(self):
        self.list_widget.clear()
        items = self.settings.get("items", [])
        
        for item_data in items:
            self.add_list_item(item_data)

    def add_list_item(self, item_data):
        text = item_data.get("text", "")
        checked = item_data.get("checked", False)
        
        item = QListWidgetItem(self.list_widget)
        
        # Custom widget for item (Checkbox + Label)
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(2, 2, 2, 2)
        
        checkbox = QCheckBox(text)
        checkbox.setChecked(checked)
        checkbox.stateChanged.connect(lambda state, i=item: self.on_item_changed(i, state))
        
        # Apply strikethrough if checked
        f = checkbox.font()
        f.setStrikeOut(checked)
        checkbox.setFont(f)
        
        layout.addWidget(checkbox)
        widget.setLayout(layout)
        
        item.setSizeHint(widget.sizeHint())
        self.list_widget.setItemWidget(item, widget)
        
        # Store data in item
        item.setData(Qt.ItemDataRole.UserRole, item_data)

    def add_item(self):
        text = self.input_field.text().strip()
        if not text:
            return
            
        item_data = {"text": text, "checked": False}
        
        # Update settings
        items = self.settings.get("items", [])
        items.append(item_data)
        self.settings["items"] = items
        self.save_settings()
        
        self.add_list_item(item_data)
        self.input_field.clear()

    def on_item_changed(self, item: QListWidgetItem, state):
        widget = self.list_widget.itemWidget(item)
        checkbox = widget.findChild(QCheckBox)
        
        checked = (state == 2) # Qt.CheckState.Checked
        
        # Update UI style
        f = checkbox.font()
        f.setStrikeOut(checked)
        checkbox.setFont(f)
        checkbox.setStyleSheet("color: #888;" if checked else "color: #fff;")
            
        # Update settings
        row = self.list_widget.row(item)
        items = self.settings.get("items", [])
        if 0 <= row < len(items):
            items[row]["checked"] = checked
            self.settings["items"] = items
            self.save_settings()

    def show_item_context_menu(self, pos):
        item = self.list_widget.itemAt(pos)
        if not item:
            return
            
        menu = QMenu(self)
        delete_action = QAction("Delete Task", self)
        delete_action.triggered.connect(lambda: self.delete_item(item))
        menu.addAction(delete_action)
        
        menu.exec(QCursor.pos())

    def delete_item(self, item):
        row = self.list_widget.row(item)
        self.list_widget.takeItem(row)
        
        items = self.settings.get("items", [])
        if 0 <= row < len(items):
            items.pop(row)
            self.settings["items"] = items
            self.save_settings()
