import pytest
import sys

import os
from PyQt6.QtWidgets import QApplication

from app.widget_engine import WidgetEngine


@pytest.fixture(scope="session")
def qapp():
    # Ensure a single QApplication for the test session and clean it up
    # at the end to avoid Qt/PyQt deallocation order crashes on exit.
    # Use sip.setdestroyonexit(False) when available to avoid sip
    # attempting to destroy wrapped C++ objects during CPython
    # interpreter shutdown — this prevents EXC_BAD_ACCESS in many
    # PyQt/sip combinations.
    try:
        import sip
        if hasattr(sip, "setdestroyonexit"):
            sip.setdestroyonexit(False)
    except Exception:
        pass

    # Force headless/offscreen Qt platform for tests to avoid creating
    # real macOS windows which can complicate teardown.
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

    app = QApplication.instance() or QApplication([])
    yield app

    # Close and delete top-level widgets to avoid sip/Qt teardown races
    try:
        for w in app.topLevelWidgets():
            try:
                w.close()
                w.deleteLater()
            except Exception:
                pass
    except Exception:
        pass

    try:
        app.quit()
    except Exception:
        pass
    # remove reference
    try:
        del app
    except Exception:
        pass


class DummyWidget:
    def __init__(self, widget_name="dummy"):
        self.widget_name = widget_name
        self._visible = True
        self.settings = {}

    def show(self):
        self._visible = True

    def hide(self):
        self._visible = False

    def isVisible(self):
        return self._visible

    def close(self):
        self._visible = False


@pytest.fixture
def engine(qapp, tmp_path):
    # Avoid creating an extra top-level QWidget as the parent because
    # its destruction can race with sip/Qt teardown at interpreter exit.
    eng = WidgetEngine(parent=None, config_dir=tmp_path, settings={})
    return eng


def test_create_and_delete_group(engine):
    assert engine.create_group("alpha") is True
    assert engine.create_group("alpha") is False  # already exists
    assert "alpha" in engine.groups

    assert engine.delete_group("alpha") is True
    assert engine.delete_group("alpha") is False


def test_add_remove_widget_from_group(engine):
    # add a dummy widget into engine.widgets
    engine.widgets["w1"] = DummyWidget("W1")

    # adding to non-existing group should create it
    assert engine.add_widget_to_group("team", "w1") is True
    assert "team" in engine.groups
    assert "w1" in engine.groups["team"]
    # groups persisted to engine.settings
    assert isinstance(engine.settings, dict)
    assert "team" in engine.settings.get("groups", {})
    assert "w1" in engine.settings.get("groups", {}).get("team", [])

    # remove
    assert engine.remove_widget_from_group("team", "w1") is True
    assert "w1" not in engine.groups["team"]


def test_show_hide_group(engine):
    engine.widgets["w2"] = DummyWidget("W2")
    engine.widgets["w3"] = DummyWidget("W3")

    engine.create_group("g1")
    engine.add_widget_to_group("g1", "w2")
    engine.add_widget_to_group("g1", "w3")

    # hide group
    engine.hide_group("g1")
    assert not engine.widgets["w2"].isVisible()
    assert not engine.widgets["w3"].isVisible()

    # show group
    engine.show_group("g1")
    assert engine.widgets["w2"].isVisible()
    assert engine.widgets["w3"].isVisible()
