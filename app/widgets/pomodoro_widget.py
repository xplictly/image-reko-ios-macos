"""
Pomodoro Timer Widget
Productivity timer with work/break intervals.
"""
from typing import Dict, Optional, Any
from datetime import datetime, timedelta

from PyQt6.QtWidgets import (
    QLabel, QVBoxLayout, QPushButton, QHBoxLayout, 
    QProgressBar, QSpinBox, QComboBox
)
from PyQt6.QtCore import QTimer, Qt, QTime
from PyQt6.QtGui import QFont, QColor

from app.widgets.base_widget import BaseWidget


class PomodoroWidget(BaseWidget):
    """Pomodoro timer widget."""
    
    def _get_default_settings(self) -> Dict:
        return {
            **super()._get_default_settings(),
            "work_duration": 25,  # minutes
            "short_break": 5,     # minutes
            "long_break": 15,     # minutes
            "auto_start_break": False,
            "sound_enabled": True
        }
    
    def _init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Status Label (Work / Break)
        self.status_label = QLabel("Focus")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_font = QFont()
        status_font.setPointSize(14)
        status_font.setBold(True)
        self.status_label.setFont(status_font)
        layout.addWidget(self.status_label)
        
        # Timer Label
        self.timer_label = QLabel("25:00")
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        timer_font = QFont()
        timer_font.setPointSize(36)
        timer_font.setBold(True)
        # Monospace font for timer stability
        timer_font.setFamily("Menlo, Monaco, Consolas, Courier New, monospace") 
        self.timer_label.setFont(timer_font)
        layout.addWidget(self.timer_label)
        
        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                background-color: rgba(255, 255, 255, 0.2);
                border-radius: 3px;
            }
            QProgressBar::chunk {
                background-color: #ff5e57;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # Controls
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        self.toggle_btn = QPushButton("Start")
        self.toggle_btn.clicked.connect(self.toggle_timer)
        self.toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.reset_btn = QPushButton("Reset")
        self.reset_btn.clicked.connect(self.reset_timer)
        self.reset_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        btn_layout.addWidget(self.toggle_btn)
        btn_layout.addWidget(self.reset_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        
        # State
        self.remaining_time = self.settings.get("work_duration", 25) * 60
        self.total_time = self.remaining_time
        self.is_running = False
        self.mode = "work"  # work, short_break, long_break
        
        # Timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        
        self.update_display()

    def toggle_timer(self):
        if self.is_running:
            self.timer.stop()
            self.is_running = False
            self.toggle_btn.setText("Resume")
        else:
            self.timer.start(1000)
            self.is_running = True
            self.toggle_btn.setText("Pause")
            
    def reset_timer(self):
        self.timer.stop()
        self.is_running = False
        self.toggle_btn.setText("Start")
        
        duration = 25
        if self.mode == "work":
            duration = self.settings.get("work_duration", 25)
        elif self.mode == "short_break":
            duration = self.settings.get("short_break", 5)
        elif self.mode == "long_break":
            duration = self.settings.get("long_break", 15)
            
        self.remaining_time = duration * 60
        self.total_time = self.remaining_time
        self.update_display()

    def update_timer(self):
        if self.remaining_time > 0:
            self.remaining_time -= 1
            self.update_display()
        else:
            self.timer_finished()
            
    def timer_finished(self):
        self.timer.stop()
        self.is_running = False
        self.toggle_btn.setText("Start")
        
        # Play sound (system beep for now)
        if self.settings.get("sound_enabled", True):
            from PyQt6.QtWidgets import QApplication
            QApplication.beep()
            
        # Switch mode
        if self.mode == "work":
            # Just finished work, time for break
            self.mode = "short_break" # Or long break logic
            self.status_label.setText("Break Time")
            
            # Use break color
            self.progress_bar.setStyleSheet("""
                QProgressBar {
                    border: none;
                    background-color: rgba(255, 255, 255, 0.2);
                    border-radius: 3px;
                }
                QProgressBar::chunk {
                    background-color: #0be881;
                    border-radius: 3px;
                }
            """)
        else:
            # Finished break, back to work
            self.mode = "work"
            self.status_label.setText("Focus Time")
            
            # Use work color
            self.progress_bar.setStyleSheet("""
                QProgressBar {
                    border: none;
                    background-color: rgba(255, 255, 255, 0.2);
                    border-radius: 3px;
                }
                QProgressBar::chunk {
                    background-color: #ff5e57;
                    border-radius: 3px;
                }
            """)
            
        self.reset_timer()
        
        if self.settings.get("auto_start_break", False):
            self.toggle_timer()

    def update_display(self):
        minutes = self.remaining_time // 60
        seconds = self.remaining_time % 60
        self.timer_label.setText(f"{minutes:02d}:{seconds:02d}")
        
        progress = 0
        if self.total_time > 0:
            progress = int((1 - self.remaining_time / self.total_time) * 100)
        self.progress_bar.setValue(progress)
    
    def _show_settings(self):
        # We can implement a custom settings dialog here if needed
        # For now, base class implementation (if any) or rely on JSON edits
        pass
