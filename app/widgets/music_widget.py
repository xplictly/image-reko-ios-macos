"""
Music Controls Widget
Simple controls for Apple Music or Spotify using AppleScript via osascript.
"""
from typing import Dict, Optional, Any
import subprocess

from PyQt6.QtWidgets import QLabel, QVBoxLayout, QPushButton, QHBoxLayout
from PyQt6.QtCore import QTimer

from app.widgets.base_widget import BaseWidget


def _run_applescript(cmd: str) -> str:
    try:
        res = subprocess.run(["osascript", "-e", cmd], capture_output=True, text=True, timeout=3)
        return res.stdout.strip()
    except Exception:
        return ""


class MusicWidget(BaseWidget):
    def _get_default_settings(self) -> Dict:
        return {
            **super()._get_default_settings(),
            "player": "Music",  # or Spotify
            "refresh": 2000
        }

    def _init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(6)

        self.track_label = QLabel("—")
        self.artist_label = QLabel("")
        self.track_label.setWordWrap(True)
        layout.addWidget(self.track_label)
        layout.addWidget(self.artist_label)

        btn_layout = QHBoxLayout()
        self.prev_btn = QPushButton("◀")
        self.play_btn = QPushButton("⏯")
        self.next_btn = QPushButton("▶")
        btn_layout.addWidget(self.prev_btn)
        btn_layout.addWidget(self.play_btn)
        btn_layout.addWidget(self.next_btn)
        layout.addLayout(btn_layout)

        self.prev_btn.clicked.connect(self.prev_track)
        self.play_btn.clicked.connect(self.play_pause)
        self.next_btn.clicked.connect(self.next_track)

        self.setLayout(layout)

        self._start_refresh_timer(self.settings.get("refresh", 2000))
        self.update_content()

    def _player_name(self):
        return self.settings.get("player", "Music")

    def get_current_track(self) -> Dict[str, str]:
        player = self._player_name()
        result = {"track": "", "artist": "", "state": "stopped"}

        if player.lower() == "music":
            # Apple Music
            title = _run_applescript('tell application "Music" to name of current track')
            artist = _run_applescript('tell application "Music" to artist of current track')
            state = _run_applescript('tell application "Music" to player state as string')
            result.update({"track": title, "artist": artist, "state": state})
        else:
            # Try Spotify
            title = _run_applescript('tell application "Spotify" to name of current track')
            artist = _run_applescript('tell application "Spotify" to artist of current track')
            state = _run_applescript('tell application "Spotify" to player state as string')
            result.update({"track": title, "artist": artist, "state": state})

        return result

    def update_content(self):
        info = self.get_current_track()
        self.track_label.setText(info.get("track") or "—")
        self.artist_label.setText(info.get("artist") or "")

    def play_pause(self):
        player = self._player_name()
        if player.lower() == "music":
            _run_applescript('tell application "Music" to playpause')
        else:
            _run_applescript('tell application "Spotify" to playpause')
        self.update_content()

    def next_track(self):
        player = self._player_name()
        if player.lower() == "music":
            _run_applescript('tell application "Music" to next track')
        else:
            _run_applescript('tell application "Spotify" to next track')
        self.update_content()

    def prev_track(self):
        player = self._player_name()
        if player.lower() == "music":
            _run_applescript('tell application "Music" to previous track')
        else:
            _run_applescript('tell application "Spotify" to previous track')
        self.update_content()
