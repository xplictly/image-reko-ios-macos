"""
Calculator Widget
Simple calculator with a clean UI.
"""
from typing import Dict, Any

from PyQt6.QtWidgets import (
    QLabel, QVBoxLayout, QGridLayout, QPushButton, 
    QWidget
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QColor

from app.widgets.base_widget import BaseWidget


class CalculatorWidget(BaseWidget):
    """Calculator widget."""
    
    def _get_default_settings(self) -> Dict:
        return {
            **super()._get_default_settings(),
            "buttons_color": "#333333",
            "accent_color": "#FF9500",
            "text_color": "#FFFFFF"
        }
    
    def _init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Display
        self.display = QLabel("0")
        self.display.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.display.setFixedHeight(50)
        font = QFont()
        font.setPointSize(32)
        self.display.setFont(font)
        self.display.setStyleSheet("color: white; padding-right: 5px;")
        layout.addWidget(self.display)
        
        # Buttons grid
        grid_layout = QGridLayout()
        grid_layout.setSpacing(5)
        
        buttons = [
            ('C', 0, 0), ('±', 0, 1), ('%', 0, 2), ('/', 0, 3, '#FF9500'),
            ('7', 1, 0), ('8', 1, 1), ('9', 1, 2), ('x', 1, 3, '#FF9500'),
            ('4', 2, 0), ('5', 2, 1), ('6', 2, 2), ('-', 2, 3, '#FF9500'),
            ('1', 3, 0), ('2', 3, 1), ('3', 3, 2), ('+', 3, 3, '#FF9500'),
            ('0', 4, 0, None, 2), ('.', 4, 2), ('=', 4, 3, '#FF9500'),
        ]
        
        for btn_data in buttons:
            text = btn_data[0]
            row = btn_data[1]
            col = btn_data[2]
            color = btn_data[3] if len(btn_data) > 3 else '#333333'
            colspan = btn_data[4] if len(btn_data) > 4 else 1
            
            btn = QPushButton(text)
            btn.setFixedSize(0, 50)  # Width expands, height fixed
            if colspan == 1:
                btn.setSizePolicy(
                    btn.sizePolicy().horizontalPolicy(), 
                    btn.sizePolicy().verticalPolicy()
                )
            
            # Styling
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border-radius: 25px;
                    font-size: 20px;
                    font-weight: bold;
                    border: none;
                }}
                QPushButton:pressed {{
                    background-color: {self._adjust_color(color, 20)};
                }}
            """)
            
            btn.clicked.connect(lambda checked, t=text: self.on_button_click(t))
            
            grid_layout.addWidget(btn, row, col, 1, colspan)
            
        layout.addLayout(grid_layout)
        self.setLayout(layout)
        
        # State
        self.current_value = "0"
        self.pending_op = None
        self.stored_value = None
        self.new_number = True

    def _adjust_color(self, hex_color, percent):
        """Lighten/darken color for press effect (simple version)."""
        return "#555555" # Fallback for simplicity

    def on_button_click(self, text):
        if text in '0123456789.':
            self._handle_digit(text)
        elif text in '+-x/':
            self._handle_op(text)
        elif text == '=':
            self._handle_equals()
        elif text == 'C':
            self._handle_clear()
        elif text == '±':
            self._handle_sign()
        elif text == '%':
            self._handle_percent()
            
    def _handle_digit(self, digit):
        if self.new_number:
            self.current_value = digit if digit != '.' else "0."
            self.new_number = False
        else:
            if digit == '.' and '.' in self.current_value:
                return
            self.current_value += digit
        self.display.setText(self.current_value)

    def _handle_op(self, op):
        self.pending_op = op
        self.stored_value = float(self.current_value)
        self.new_number = True

    def _handle_equals(self):
        if self.pending_op and self.stored_value is not None:
            current = float(self.current_value)
            result = 0
            if self.pending_op == '+':
                result = self.stored_value + current
            elif self.pending_op == '-':
                result = self.stored_value - current
            elif self.pending_op == 'x':
                result = self.stored_value * current
            elif self.pending_op == '/':
                if current != 0:
                    result = self.stored_value / current
                else:
                    self.display.setText("Error")
                    self.new_number = True
                    return
            
            # Format result
            if result.is_integer():
                self.current_value = str(int(result))
            else:
                self.current_value = f"{result:.8f}".rstrip('0').rstrip('.')
                
            self.display.setText(self.current_value)
            self.pending_op = None
            self.new_number = True

    def _handle_clear(self):
        self.current_value = "0"
        self.pending_op = None
        self.stored_value = None
        self.new_number = True
        self.display.setText("0")

    def _handle_sign(self):
        if self.current_value == "0":
            return
        if self.current_value.startswith("-"):
            self.current_value = self.current_value[1:]
        else:
            self.current_value = "-" + self.current_value
        self.display.setText(self.current_value)

    def _handle_percent(self):
        val = float(self.current_value)
        val /= 100
        self.current_value = str(val)
        self.display.setText(self.current_value)
        self.new_number = True
