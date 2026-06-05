"""
Stock/Crypto Ticker Widget
Displays real-time price information using yfinance.
"""
from typing import Dict, Optional, Any
import threading

from PyQt6.QtWidgets import (
    QLabel, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLineEdit, QWidget
)
from PyQt6.QtCore import QTimer, Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor

from app.widgets.base_widget import BaseWidget
from app.utils.logger import logger

try:
    import yfinance as yf
    HAS_YFINANCE = True
except ImportError:
    HAS_YFINANCE = False


class StockWidget(BaseWidget):
    """Stock ticker widget."""
    
    data_updated = pyqtSignal(dict)
    
    def _get_default_settings(self) -> Dict:
        return {
            **super()._get_default_settings(),
            "symbol": "AAPL",
            "refresh_interval": 60000,  # 1 minute
            "show_percent": True
        }
    
    def _init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(5)
        
        # Symbol Input (Hidden by default, shown on double click or settings)
        self.symbol_input = QLineEdit()
        self.symbol_input.setPlaceholderText("Enter Symbol (e.g. AAPL, BTC-USD)")
        self.symbol_input.returnPressed.connect(self._on_symbol_entered)
        self.symbol_input.hide()
        layout.addWidget(self.symbol_input)
        
        # Symbol Label
        self.symbol_label = QLabel(self.settings.get("symbol", "AAPL"))
        self.symbol_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        self.symbol_label.setFont(font)
        layout.addWidget(self.symbol_label)
        
        # Price Label
        self.price_label = QLabel("Loading...")
        self.price_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        price_font = QFont()
        price_font.setPointSize(28)
        price_font.setBold(True)
        self.price_label.setFont(price_font)
        layout.addWidget(self.price_label)
        
        # Change Label
        self.change_label = QLabel("")
        self.change_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        change_font = QFont()
        change_font.setPointSize(14)
        self.change_label.setFont(change_font)
        layout.addWidget(self.change_label)
        
        self.setLayout(layout)
        
        self.data_updated.connect(self._update_ui_data)
        
        # Start update timer
        interval = self.settings.get("refresh_interval", 60000)
        self._start_refresh_timer(interval)
        
        # Initial update
        QTimer.singleShot(100, self.update_content)

    def mouseDoubleClickEvent(self, event):
        """Show input on double click."""
        if self.symbol_input.isVisible():
            self.symbol_input.hide()
            self.symbol_label.show()
        else:
            self.symbol_input.setText(self.settings.get("symbol", ""))
            self.symbol_label.hide()
            self.symbol_input.show()
            self.symbol_input.setFocus()
        
        super().mouseDoubleClickEvent(event)

    def _on_symbol_entered(self):
        new_symbol = self.symbol_input.text().strip().upper()
        if new_symbol:
            self.settings["symbol"] = new_symbol
            self.symbol_label.setText(new_symbol)
            self.save_settings()
            self.update_content()
        
        self.symbol_input.hide()
        self.symbol_label.show()

    def update_content(self):
        """Fetch stock data in background."""
        if not HAS_YFINANCE:
            self.price_label.setText("Error")
            self.change_label.setText("yfinance not installed")
            return
            
        symbol = self.settings.get("symbol", "AAPL")
        
        # Run in thread to avoid freezing UI
        thread = threading.Thread(target=self._fetch_data, args=(symbol,))
        thread.daemon = True
        thread.start()
        
    def _fetch_data(self, symbol):
        try:
            ticker = yf.Ticker(symbol)
            # fast_info is faster than history
            info = ticker.fast_info
            
            if info and hasattr(info, 'last_price'):
                price = info.last_price
                prev_close = info.previous_close
                change = price - prev_close
                pct_change = (change / prev_close) * 100
                
                self.data_updated.emit({
                    "price": price,
                    "change": change,
                    "pct_change": pct_change,
                    "success": True
                })
            else:
                 # Fallback to history if fast_info fails
                hist = ticker.history(period="1d")
                if not hist.empty:
                    close = hist['Close'].iloc[-1]
                    # We might not get change easily from 1d history without previous close
                    # But often [0] is open or prev close depending on data
                    self.data_updated.emit({
                        "price": close,
                        "change": 0.0,
                        "pct_change": 0.0,
                        "success": True
                    })
                else:
                    self.data_updated.emit({"success": False, "error": "No data"})
                    
        except Exception as e:
            logger.error(f"Error fetching stock data: {e}")
            self.data_updated.emit({"success": False, "error": str(e)})

    def _update_ui_data(self, data):
        if not data.get("success"):
            self.change_label.setText("Data unavailable")
            return
            
        price = data.get("price", 0.0)
        change = data.get("change", 0.0)
        pct = data.get("pct_change", 0.0)
        
        self.price_label.setText(f"{price:.2f}")
        
        sign = "+" if change >= 0 else ""
        color = "#2ecc71" if change >= 0 else "#e74c3c"
        
        self.change_label.setText(f"{sign}{change:.2f} ({sign}{pct:.2f}%)")
        self.change_label.setStyleSheet(f"color: {color};")
