"""
Main Management Window UI for WidgetWall
Redesigned to mimic the macOS native Widget Gallery
"""

import sys
from pathlib import Path
from typing import Dict, Optional, List

try:
    from PyQt6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
        QListWidget, QListWidgetItem, QDialog, QDialogButtonBox,
        QScrollArea, QGridLayout, QFrame, QSizePolicy,
        QSpacerItem, QGroupBox, QLineEdit, QStackedWidget, QCheckBox, QComboBox
    )
    from PyQt6.QtCore import Qt, QSize, pyqtSignal, QMargins
    from PyQt6.QtGui import QIcon, QFont, QPixmap, QPainter, QColor
except ImportError:
    print("Error: PyQt6 is required. Install with: pip install PyQt6")
    sys.exit(1)


class FlowLayout(QVBoxLayout):
    """A simple flow layout fallback if needed, but we will just use QGridLayout with row/col wrapping."""
    pass


class MainManagementWindow(QWidget):
    """Main management window for WidgetWall."""
    
    def __init__(
        self,
        parent=None,
        widget_engine=None,
        theme_manager=None
    ):
        super().__init__(parent)
        
        self.widget_engine = widget_engine
        self.theme_manager = theme_manager
        
        # Determine unique categories
        self.categories = ["All Widgets"]
        from app.widgets.base_widget import WIDGET_REGISTRY
        cats = set()
        for w in WIDGET_REGISTRY.values():
            cats.add(w.get("category", "other").capitalize())
        self.categories.extend(sorted(list(cats)))
        
        self._init_ui()
        self._apply_styles()
    
    def _init_ui(self):
        """Initialize the UI."""
        self.setWindowTitle("Widget Gallery")
        self.setMinimumSize(850, 600)
        self.resize(900, 650)
        
        # Main layout: Horizontal Split
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # --- LEFT SIDEBAR ---
        sidebar_frame = QFrame()
        sidebar_frame.setObjectName("sidebar")
        sidebar_frame.setFixedWidth(240)
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(15, 20, 15, 20)
        sidebar_layout.setSpacing(10)
        
        # Search Box
        self.search_box = QLineEdit()
        self.search_box.setObjectName("searchBox")
        self.search_box.setPlaceholderText("🔍 Search Widgets")
        self.search_box.textChanged.connect(self._on_search)
        sidebar_layout.addWidget(self.search_box)
        
        sidebar_layout.addSpacing(10)
        
        # Categories List
        self.category_list = QListWidget()
        self.category_list.setObjectName("sidebarList")
        for cat in self.categories:
            item = QListWidgetItem(cat)
            self.category_list.addItem(item)
        
        self.category_list.itemSelectionChanged.connect(self._on_sidebar_selection)
        sidebar_layout.addWidget(self.category_list)
        
        # Management Section in Sidebar
        management_label = QLabel("Management")
        management_label.setObjectName("sectionLabel")
        sidebar_layout.addWidget(management_label)
        
        self.management_list = QListWidget()
        self.management_list.setObjectName("sidebarList")
        self.management_list.setFixedHeight(140)
        
        for item_name in ["Active Widgets", "Groups", "Settings"]:
            self.management_list.addItem(QListWidgetItem(item_name))
            
        self.management_list.itemSelectionChanged.connect(self._on_management_selection)
        sidebar_layout.addWidget(self.management_list)
        
        sidebar_frame.setLayout(sidebar_layout)
        main_layout.addWidget(sidebar_frame)
        
        # --- RIGHT CONTENT AREA ---
        self.content_stack = QStackedWidget()
        self.content_stack.setObjectName("contentArea")
        
        # Page 0: Widget Gallery (Grid)
        self.gallery_page = QWidget()
        gallery_layout = QVBoxLayout()
        gallery_layout.setContentsMargins(0, 0, 0, 0)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setObjectName("scrollArea")
        
        self.scroll_content = QWidget()
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(20)
        self.grid_layout.setContentsMargins(30, 30, 30, 30)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.scroll_content.setLayout(self.grid_layout)
        self.scroll_area.setWidget(self.scroll_content)
        
        gallery_layout.addWidget(self.scroll_area)
        self.gallery_page.setLayout(gallery_layout)
        self.content_stack.addWidget(self.gallery_page)
        
        # Page 1: Active Widgets
        self.active_page = self._create_active_widgets_page()
        self.content_stack.addWidget(self.active_page)
        
        # Page 2: Groups
        self.groups_page = self._create_groups_page()
        self.content_stack.addWidget(self.groups_page)
        
        # Page 3: Settings
        self.settings_page = self._create_settings_page()
        self.content_stack.addWidget(self.settings_page)
        
        main_layout.addWidget(self.content_stack)
        
        self.setLayout(main_layout)
        
        # Select first category by default
        self.category_list.setCurrentRow(0)
        self._populate_grid()
        
    def _create_active_widgets_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)
        
        title = QLabel("Active Widgets")
        title.setObjectName("pageTitle")
        layout.addWidget(title)
        
        self.active_widgets_list = QListWidget()
        self.active_widgets_list.setObjectName("managementList")
        layout.addWidget(self.active_widgets_list)
        
        btn_layout = QHBoxLayout()
        hide_btn = QPushButton("Hide All")
        hide_btn.clicked.connect(self._hide_all)
        show_btn = QPushButton("Show All")
        show_btn.clicked.connect(self._show_all)
        
        btn_layout.addWidget(hide_btn)
        btn_layout.addWidget(show_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        return page

    def _create_groups_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)
        
        title = QLabel("Widget Groups")
        title.setObjectName("pageTitle")
        layout.addWidget(title)
        
        content = QHBoxLayout()
        
        # Left: Groups
        left = QVBoxLayout()
        self.groups_list = QListWidget()
        self.groups_list.setObjectName("managementList")
        self.groups_list.itemSelectionChanged.connect(self._on_group_selection_changed)
        left.addWidget(QLabel("Groups"))
        left.addWidget(self.groups_list)
        
        grp_btns = QHBoxLayout()
        btn_new = QPushButton("New Group")
        btn_new.clicked.connect(self._create_group_dialog)
        btn_del = QPushButton("Delete")
        btn_del.clicked.connect(self._delete_selected_group)
        btn_save = QPushButton("Save Groups")
        btn_save.clicked.connect(self._save_groups)
        
        grp_btns.addWidget(btn_new)
        grp_btns.addWidget(btn_del)
        left.addLayout(grp_btns)
        left.addWidget(btn_save)
        
        content.addLayout(left, 1)
        
        # Middle: Controls
        mid = QVBoxLayout()
        btn_show = QPushButton("Show Group")
        btn_show.clicked.connect(self._show_selected_group)
        btn_hide = QPushButton("Hide Group")
        btn_hide.clicked.connect(self._hide_selected_group)
        btn_add = QPushButton("Add Active")
        btn_add.clicked.connect(self._add_selected_active_to_group)
        btn_rem = QPushButton("Remove Item")
        btn_rem.clicked.connect(self._remove_selected_from_group)
        
        mid.addStretch()
        mid.addWidget(btn_show)
        mid.addWidget(btn_hide)
        mid.addSpacing(20)
        mid.addWidget(btn_add)
        mid.addWidget(btn_rem)
        mid.addStretch()
        
        content.addLayout(mid, 1)
        
        # Right: Members
        right = QVBoxLayout()
        self.group_members_list = QListWidget()
        self.group_members_list.setObjectName("managementList")
        right.addWidget(QLabel("Members"))
        right.addWidget(self.group_members_list)
        
        content.addLayout(right, 1)
        
        layout.addLayout(content)
        return page

    def _create_settings_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)
        
        title = QLabel("Settings")
        title.setObjectName("pageTitle")
        layout.addWidget(title)
        
        theme_group = QGroupBox("Appearance")
        theme_layout = QVBoxLayout()
        
        theme_label = QLabel("Theme:")
        theme_layout.addWidget(theme_label)
        
        self.theme_combo = QComboBox()
        if self.theme_manager:
            for theme_name in self.theme_manager.get_available_themes():
                self.theme_combo.addItem(theme_name)
            current_theme = self.theme_manager.current_theme_name
            self.theme_combo.setCurrentText(current_theme)
        theme_layout.addWidget(self.theme_combo)
        
        theme_group.setLayout(theme_layout)
        layout.addWidget(theme_group)
        
        global_group = QGroupBox("Global Behaviors")
        global_layout = QVBoxLayout()
        
        self.click_through_check = QCheckBox("Enable Click-Through Mode (Ignores Mouse)")
        global_layout.addWidget(self.click_through_check)
        
        self.snap_grid_check = QCheckBox("Snap Widgets to Edge")
        self.snap_grid_check.setChecked(True)
        global_layout.addWidget(self.snap_grid_check)
        
        global_group.setLayout(global_layout)
        layout.addWidget(global_group)
        
        layout.addStretch()
        return page

    def _on_sidebar_selection(self):
        """Handle gallery category selection."""
        if not self.category_list.selectedItems(): return
        self.management_list.clearSelection()
        self.content_stack.setCurrentIndex(0)
        self._populate_grid()
        
    def _on_management_selection(self):
        """Handle management section selection."""
        if not self.management_list.selectedItems(): return
        self.category_list.clearSelection()
        
        item = self.management_list.selectedItems()[0].text()
        if item == "Active Widgets":
            self.content_stack.setCurrentIndex(1)
            self.refresh_active_widgets()
        elif item == "Groups":
            self.content_stack.setCurrentIndex(2)
            self.refresh_groups()
        elif item == "Settings":
            self.content_stack.setCurrentIndex(3)

    def _on_search(self, text):
        """Filter the grid based on search."""
        self.category_list.setCurrentRow(0) # Select "All Widgets"
        self._populate_grid(search_query=text.lower())
        
    def _populate_grid(self, search_query=""):
        """Populate the right grid layout with widget cards."""
        # Clear layout
        while self.grid_layout.count():
            child = self.grid_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
        category = "All Widgets"
        if self.category_list.selectedItems():
            category = self.category_list.selectedItems()[0].text()
            
        from app.widgets.base_widget import WIDGET_REGISTRY
        
        row, col = 0, 0
        max_cols = 3
        
        for widget_type, info in WIDGET_REGISTRY.items():
            w_cat = info.get("category", "other").capitalize()
            w_name = info.get("name", widget_type)
            
            # Filter logic
            if category != "All Widgets" and w_cat != category:
                continue
            if search_query and search_query not in w_name.lower():
                continue
                
            card = self._create_widget_card(info, widget_type)
            self.grid_layout.addWidget(card, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1

    def _create_widget_card(self, info: Dict, widget_type: str) -> QFrame:
        """Create a beautiful macOS style widget preview card."""
        card = QFrame()
        card.setObjectName("widgetCard")
        card.setFixedSize(180, 160)
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(15, 20, 15, 15)
        layout.setSpacing(10)
        
        icon_label = QLabel(info.get("icon", "📦"))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setPointSize(42)
        icon_label.setFont(font)
        
        name_label = QLabel(info.get("name", widget_type))
        name_label.setObjectName("cardTitle")
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        add_btn = QPushButton("Add")
        add_btn.setObjectName("addButton")
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.clicked.connect(lambda checked, w=widget_type: self._add_widget(w))
        
        layout.addWidget(icon_label)
        layout.addWidget(name_label)
        layout.addStretch()
        layout.addWidget(add_btn)
        
        card.setLayout(layout)
        return card

    def _add_widget(self, widget_type: str):
        """Add widget via engine."""
        if self.widget_engine:
            self.widget_engine.create_widget(widget_type)
            self.refresh_active_widgets()

    def _apply_styles(self):
        """Apply native macOS Widget Gallery styling."""
        colors = {
            "bg": "#1e1e1e",
            "sidebar_bg": "#171717",
            "surface": "#2d2d2d",
            "card_bg": "#2a2a2a",
            "card_hover": "#363636",
            "text": "#ffffff",
            "text_dim": "#999999",
            "accent": "#0A84FF",
            "border": "#333333"
        }
        if self.theme_manager:
            theme_colors = self.theme_manager.current_theme.get("colors", {})
            colors["accent"] = theme_colors.get("accent", "#0A84FF")
            
        css = f"""
        QWidget {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            color: {colors['text']};
        }}
        
        #sidebar {{
            background-color: {colors['sidebar_bg']};
            border-right: 1px solid {colors['border']};
        }}
        
        #contentArea, #scrollArea {{
            background-color: {colors['bg']};
        }}
        
        #searchBox {{
            background-color: {colors['surface']};
            border: 1px solid {colors['border']};
            border-radius: 6px;
            padding: 8px 12px;
            font-size: 13px;
        }}
        
        #sectionLabel {{
            color: {colors['text_dim']};
            font-size: 11px;
            font-weight: bold;
            text-transform: uppercase;
            margin-top: 15px;
            margin-left: 5px;
        }}
        
        #sidebarList {{
            background-color: transparent;
            border: none;
            outline: none;
        }}
        
        #sidebarList::item {{
            padding: 8px 12px;
            border-radius: 6px;
            margin-bottom: 2px;
            font-size: 13px;
            font-weight: 500;
        }}
        
        #sidebarList::item:hover {{
            background-color: {colors['surface']};
        }}
        
        #sidebarList::item:selected {{
            background-color: {colors['accent']};
            color: white;
            font-weight: bold;
        }}
        
        #pageTitle {{
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 20px;
        }}
        
        #widgetCard {{
            background-color: {colors['card_bg']};
            border: 1px solid {colors['border']};
            border-radius: 14px;
        }}
        
        #widgetCard:hover {{
            background-color: {colors['card_hover']};
            border: 1px solid {colors['text_dim']};
        }}
        
        #cardTitle {{
            font-size: 14px;
            font-weight: 600;
        }}
        
        #addButton {{
            background-color: {colors['surface']};
            border: 1px solid {colors['border']};
            border-radius: 10px;
            padding: 6px 0;
            font-weight: bold;
            color: {colors['accent']};
        }}
        
        #addButton:hover {{
            background-color: {colors['accent']};
            color: white;
        }}
        
        #managementList {{
            background-color: {colors['card_bg']};
            border: 1px solid {colors['border']};
            border-radius: 8px;
            padding: 5px;
        }}
        
        #managementList::item {{
            padding: 8px;
            border-bottom: 1px solid {colors['border']};
        }}
        
        QPushButton {{
            background-color: {colors['surface']};
            border: 1px solid {colors['border']};
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: 500;
        }}
        
        QPushButton:hover {{
            background-color: {colors['card_hover']};
        }}
        
        QGroupBox {{
            border: 1px solid {colors['border']};
            border-radius: 8px;
            margin-top: 15px;
            padding-top: 15px;
            font-weight: bold;
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 15px;
            padding: 0 5px;
        }}
        
        QScrollBar:vertical {{
            border: none;
            background: transparent;
            width: 10px;
            margin: 0px 0px 0px 0px;
        }}
        QScrollBar::handle:vertical {{
            background: {colors['border']};
            border-radius: 5px;
            min-height: 20px;
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        """
        
        self.setStyleSheet(css)

    # -----------------
    # Controls (same as before)
    # -----------------
    def _hide_all(self):
        if self.widget_engine: self.widget_engine.hide_all_widgets()
    
    def _show_all(self):
        if self.widget_engine: self.widget_engine.show_all_widgets()

    def refresh_active_widgets(self):
        if self.widget_engine:
            self.active_widgets_list.clear()
            for widget_id, widget in self.widget_engine.get_all_widgets().items():
                item = QListWidgetItem(f"{widget.widget_name} ({widget_id})")
                self.active_widgets_list.addItem(item)

    def refresh_groups(self):
        self.groups_list.clear()
        self.group_members_list.clear()
        if not self.widget_engine: return
        for group_name in sorted(self.widget_engine.groups.keys()):
            self.groups_list.addItem(QListWidgetItem(group_name))

    def _on_group_selection_changed(self):
        self.group_members_list.clear()
        items = self.groups_list.selectedItems()
        if not items or not self.widget_engine: return
        group_name = items[0].text()
        members = self.widget_engine.groups.get(group_name, set())
        for wid in sorted(members):
            self.group_members_list.addItem(QListWidgetItem(wid))

    def _create_group_dialog(self):
        from PyQt6.QtWidgets import QInputDialog
        name, ok = QInputDialog.getText(self, "Create Group", "Group name:")
        if ok and name:
            if self.widget_engine and self.widget_engine.create_group(name):
                self.refresh_groups()

    def _delete_selected_group(self):
        items = self.groups_list.selectedItems()
        if not items or not self.widget_engine: return
        group_name = items[0].text()
        self.widget_engine.delete_group(group_name)
        self.refresh_groups()

    def _show_selected_group(self):
        items = self.groups_list.selectedItems()
        if not items or not self.widget_engine: return
        group_name = items[0].text()
        self.widget_engine.show_group(group_name)

    def _hide_selected_group(self):
        items = self.groups_list.selectedItems()
        if not items or not self.widget_engine: return
        group_name = items[0].text()
        self.widget_engine.hide_group(group_name)

    def _parse_widget_id_from_item(self, text: str) -> str:
        if not text: return text
        if "(" in text and text.endswith(")"):
            return text[text.rfind("(")+1:-1]
        return text

    def _add_selected_active_to_group(self):
        grp_items = self.groups_list.selectedItems()
        if not grp_items or not self.widget_engine: return
        group_name = grp_items[0].text()
        for sel in self.active_widgets_list.selectedItems():
            wid = self._parse_widget_id_from_item(sel.text())
            if wid:
                self.widget_engine.add_widget_to_group(group_name, wid)
        self._on_group_selection_changed()

    def _remove_selected_from_group(self):
        grp_items = self.groups_list.selectedItems()
        if not grp_items or not self.widget_engine: return
        group_name = grp_items[0].text()
        for sel in self.group_members_list.selectedItems():
            wid = sel.text()
            if wid:
                self.widget_engine.remove_widget_from_group(group_name, wid)
        self._on_group_selection_changed()

    def _save_groups(self):
        """Trigger a save of groups to persistent settings via the engine signal."""
        if self.widget_engine:
            try:
                self.widget_engine.groups_changed.emit()
            except Exception:
                pass


