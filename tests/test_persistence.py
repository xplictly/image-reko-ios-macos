import json
import time

from pathlib import Path

import pytest

from PyQt6.QtWidgets import QApplication

from app.main_window import WidgetWallApp


def test_groups_persist_to_disk(tmp_path):
    # Ensure a clean config dir
    cfg = tmp_path / "data"
    cfg.mkdir()

    # Ensure a QApplication exists for WidgetWallApp (tests run headless)
    _ = QApplication.instance() or QApplication([])

    # Create app (this constructs WidgetWallApp which is a QApplication)
    app = WidgetWallApp(config_dir=cfg)

    # create a group via engine
    app.widget_engine.create_group("persist_me")

    # small wait to allow signal handlers to run
    time.sleep(0.1)

    settings_file = cfg / "settings.json"
    assert settings_file.exists()

    data = json.loads(settings_file.read_text(encoding='utf-8'))
    assert "groups" in data
    assert "persist_me" in data["groups"]