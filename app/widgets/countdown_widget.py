"""
Countdown Timer Widget
Displays days, hours, minutes until a target date.
"""
from typing import Dict, Any
from datetime import datetime, timedelta

from PyQt6.QtWidgets import (
    QLabel, QVBoxLayout, QHBoxLayout, QPushButton, 
    QDateTimeEdit, QWidget, QLineEdit
)
from PyQt6.QtCore import QTimer, Qt, QDateTime
from PyQt6.QtGui import QFont, QColor

from app.widgets.base_widget import BaseWidget


class CountdownWidget(BaseWidget):
    """Countdown widget."""
    
    def _get_default_settings(self) -> Dict:
        return {
            **super()._get_default_settings(),
            "target_date": (datetime.now() + timedelta(days=1)).isoformat(),
            "event_name": "Event Name",
            "show_seconds": True
        }
    
    def _init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        
        # Event Name (Click to edit)
        self.name_label = QLabel(self.settings.get("event_name", "Event"))
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setPointSize(24)
        font.setBold(True)
        self.name_label.setFont(font)
        layout.addWidget(self.name_label)
        
        # Input for name (hidden)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Event Name")
        self.name_input.returnPressed.connect(self._save_name)
        self.name_input.hide()
        layout.addWidget(self.name_input)
        
        # Countdown Display
        self.time_label = QLabel("--:--:--:--")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        time_font = QFont()
        time_font.setPointSize(36)
        time_font.setBold(True)
        self.time_label.setFont(time_font)
        # Monospace for stable width
        self.time_label.setStyleSheet("font-family: monospace;") 
        layout.addWidget(self.time_label)
        
        # Labels (Days, Hrs, Min, Sec)
        labels_layout = QHBoxLayout()
        for text in ["DAYS", "HRS", "MIN", "SEC"]:
            l = QLabel(text)
            l.setAlignment(Qt.AlignmentFlag.AlignCenter)
            l.setStyleSheet("color: #888; font-size: 10px;")
            labels_layout.addWidget(l)
        layout.addLayout(labels_layout)
        
        # Date Edit (Hidden)
        target_str = self.settings.get("target_date")
        try:
            target_dt = datetime.fromisoformat(target_str)
        except:
            target_dt = datetime.now() + timedelta(days=1)
            
        self.date_edit = QDateTimeEdit(target_dt)
        self.date_edit.setCalendarPopup(True)
        self.date_edit.dateTimeChanged.connect(self._save_date)
        self.date_edit.hide()
        layout.addWidget(self.date_edit)
        
        self.setLayout(layout)
        
        # Parse target
        self.target_time = target_dt
        
        # Start timer
        self._start_refresh_timer(1000)
        self.update_content()

    def mouseDoubleClickEvent(self, event):
        """Toggle edit mode on double click."""
        if self.date_edit.isVisible():
            self.date_edit.hide()
            self.name_input.hide()
            self.name_label.show()
            self.time_label.show()
        else:
            self.name_input.setText(self.settings.get("event_name", ""))
            self.date_edit.setDateTime(self.target_time)
            
            self.time_label.hide()
            self.name_label.hide()
            self.name_input.show()
            self.date_edit.show()
            self.name_input.setFocus()
            
        super().mouseDoubleClickEvent(event)

    def _save_name(self):
        new_name = self.name_input.text().strip()
        if new_name:
            self.settings["event_name"] = new_name
            self.name_label.setText(new_name)
            self.save_settings()
        
        # Hide inputs if date is also done? For now kept separate
        
    def _save_date(self, qdt: QDateTime):
        dt = qdt.toPyDateTime()
        self.target_time = dt
        self.settings["target_date"] = dt.isoformat()
        self.save_settings()
        self.update_content()

    def update_content(self):
        now = datetime.now()
        diff = self.target_time - now
        
        if diff.total_seconds() <= 0:
            self.time_label.setText("00:00:00:00")
            return
            
        days = diff.days
        seconds = diff.seconds
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        self.time_label.setText(f"{days:02d}:{hours:02d}:{minutes:02d}:{secs:02d}")
