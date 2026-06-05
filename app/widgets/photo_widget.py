"""
Photo Slideshow Widget
Displays images from a user-selected directory as a slideshow.
"""
from pathlib import Path
from typing import Optional, Dict, Any
import os
import glob
import random

from PyQt6.QtWidgets import QLabel, QVBoxLayout, QPushButton, QHBoxLayout
from PyQt6.QtCore import QTimer, QSize, Qt
from PyQt6.QtGui import QPixmap

from app.widgets.base_widget import BaseWidget


class PhotoWidget(BaseWidget):
    def _get_default_settings(self) -> Dict:
        return {
            **super()._get_default_settings(),
            "photo_dir": str(Path.home() / "Pictures"),
            "interval_sec": 8,
            "shuffle": True
        }

    def _init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        self.image_label = QLabel()
        self.image_label.setAlignment(self.image_label.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumSize(200, 150)
        layout.addWidget(self.image_label)

        btn_layout = QHBoxLayout()
        self.prev_btn = QPushButton("◀")
        self.next_btn = QPushButton("▶")
        btn_layout.addWidget(self.prev_btn)
        btn_layout.addWidget(self.next_btn)
        layout.addLayout(btn_layout)

        self.prev_btn.clicked.connect(self.show_prev)
        self.next_btn.clicked.connect(self.show_next)

        self.setLayout(layout)

        self.photos = []
        self.current_index = 0

        self._load_photos()

        interval = max(2, int(self.settings.get("interval_sec", 8))) * 1000
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.show_next)
        self.timer.start(interval)

        self.update_content()

    def _load_photos(self):
        photo_dir = Path(self.settings.get("photo_dir", Path.home() / "Pictures"))
        if not photo_dir.exists():
            self.photos = []
            return

        patterns = ["*.png", "*.jpg", "*.jpeg", "*.gif", "*.bmp"]
        files = []
        for p in patterns:
            files.extend(photo_dir.glob(p))

        self.photos = [str(f) for f in files]
        if self.settings.get("shuffle", True):
            random.shuffle(self.photos)

    def update_content(self):
        if not self.photos:
            self.image_label.setText("No photos found")
            return

        self.show_image(self.current_index)

    def show_image(self, idx: int):
        if not self.photos:
            return
        idx = idx % len(self.photos)
        self.current_index = idx
        path = self.photos[self.current_index]
        pix = QPixmap(path)
        if pix.isNull():
            self.image_label.setText("Failed to load image")
            return

        # Scale pixmap preserving aspect
        scaled = pix.scaled(self.image_label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation) if hasattr(QPixmap, 'scaled') else pix
        self.image_label.setPixmap(scaled)

    def show_next(self):
        if not self.photos:
            return
        self.current_index = (self.current_index + 1) % len(self.photos)
        self.show_image(self.current_index)

    def show_prev(self):
        if not self.photos:
            return
        self.current_index = (self.current_index - 1) % len(self.photos)
        self.show_image(self.current_index)
