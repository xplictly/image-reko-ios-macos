"""
Lightweight premium features helper module.
- Provides a set of curated theme presets (free and original)
- Simple import/export configuration helpers (JSON)
- A very small automation scheduler wrapper (APScheduler can be used if installed)

These are intentionally minimal and meant to be used by the app components.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


def get_builtin_premium_themes() -> Dict[str, Dict[str, Any]]:
    """Return a small curated set of theme presets inspired by modern macOS styling.
    These are original palettes (not copied from any paid product).
    """
    return {
        "aurora_dark": {
            "name": "Aurora Dark",
            "colors": {
                "background": "#0b1020",
                "text": "#e6eef8",
                "accent": "#6ee7b7"
            },
            "border_radius": {"md": 12},
            "opacity": {"background": 0.88}
        },
        "paper_light": {
            "name": "Paper Light",
            "colors": {
                "background": "#f7f7fb",
                "text": "#111827",
                "accent": "#3b82f6"
            },
            "border_radius": {"md": 8},
            "opacity": {"background": 0.95}
        },
        "sunset": {
            "name": "Sunset",
            "colors": {
                "background": "#16121a",
                "text": "#fff7ed",
                "accent": "#ff8a65"
            },
            "border_radius": {"md": 14},
            "opacity": {"background": 0.9}
        }
    }


def export_configuration(config: Dict[str, Any], path: Optional[Path] = None) -> Path:
    """Export the provided configuration dict to a JSON file.
    Returns the path to the exported file.
    """
    if path is None:
        path = Path.cwd() / f"widgetwall_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    return path


def import_configuration(path: Path) -> Dict[str, Any]:
    """Import configuration from a JSON file and return the dict."""
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


def schedule_automation_task(task_name: str, callback, when: float):
    """Very small helper to schedule a one-off call using threading.Timer.
    For heavy usage, swap to APScheduler or similar.
    """
    import threading

    timer = threading.Timer(when, callback)
    timer.setName(f"automation-{task_name}")
    timer.daemon = True
    timer.start()
    return timer
