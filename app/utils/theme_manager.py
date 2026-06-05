"""
Theme Manager for WidgetWall
Handles loading and applying minimalist themes
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from app.utils.logger import logger


class ThemeManager:
    """Manages application themes."""
    
    BUILTIN_THEMES = {
        "minimal_dark": {
            "name": "Minimal Dark",
            "colors": {
                "background": "#1a1a1a",
                "surface": "#2d2d2d",
                "text": "#ffffff",
                "text_secondary": "#8e8e93",
                "border": "#3d3d3d",
                "accent": "#007AFF",
                "success": "#34c759",
                "warning": "#ff9500",
                "error": "#ff3b30"
            },
            "fonts": {"primary": "-apple-system, sans-serif"},
            "spacing": {"xs": 4, "sm": 8, "md": 16, "lg": 24},
            "border_radius": {"sm": 4, "md": 8, "lg": 12}
        },
        "minimal_light": {
            "name": "Minimal Light",
            "colors": {
                "background": "#ffffff",
                "surface": "#f5f5f7",
                "text": "#1d1d1f",
                "text_secondary": "#86868b",
                "border": "#d2d2d7",
                "accent": "#0071e3",
                "success": "#34c759",
                "warning": "#ff9500",
                "error": "#ff3b30"
            },
            "fonts": {"primary": "-apple-system, sans-serif"},
            "spacing": {"xs": 4, "sm": 8, "md": 16, "lg": 24},
            "border_radius": {"sm": 4, "md": 8, "lg": 12}
        },
        "midnight": {
            "name": "Midnight",
            "colors": {
                "background": "#0d1117",
                "surface": "#161b22",
                "text": "#c9d1d9",
                "text_secondary": "#8b949e",
                "border": "#30363d",
                "accent": "#58a6ff",
                "success": "#3fb950",
                "warning": "#d29922",
                "error": "#f85149"
            },
            "fonts": {"primary": "-apple-system, sans-serif"},
            "spacing": {"xs": 4, "sm": 8, "md": 16, "lg": 24},
            "border_radius": {"sm": 4, "md": 8, "lg": 12}
        }
    }
    
    def __init__(self, theme_dir: Path = Path("data/themes")):
        self.theme_dir = theme_dir
        self.current_theme: Optional[Dict] = None
        self.current_theme_name = "minimal_dark"
        
        self.theme_dir.mkdir(parents=True, exist_ok=True)
        custom_dir = self.theme_dir / "custom"
        custom_dir.mkdir(parents=True, exist_ok=True)
        
        self._save_builtin_themes()
    
    def _save_builtin_themes(self):
        for theme_name, theme_data in self.BUILTIN_THEMES.items():
            theme_file = self.theme_dir / f"{theme_name}.json"
            if not theme_file.exists():
                try:
                    with open(theme_file, 'w', encoding='utf-8') as f:
                        json.dump(theme_data, f, indent=2)
                    logger.info(f"Saved built-in theme: {theme_name}")
                except Exception as e:
                    logger.error(f"Failed to save theme {theme_name}: {e}")
    
    def get_available_themes(self) -> List[str]:
        themes = list(self.BUILTIN_THEMES.keys())
        if self.theme_dir.exists():
            for theme_file in self.theme_dir.glob("*.json"):
                theme_name = theme_file.stem
                if theme_name not in themes:
                    themes.append(theme_name)
        return sorted(themes)
    
    def get_theme(self, theme_name: str) -> Optional[Dict]:
        if theme_name in self.BUILTIN_THEMES:
            return self.BUILTIN_THEMES[theme_name]
        
        theme_file = self.theme_dir / f"{theme_name}.json"
        if theme_file.exists():
            try:
                with open(theme_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load theme {theme_name}: {e}")
        return None
    
    def load_theme(self, theme_name: str) -> bool:
        theme = self.get_theme(theme_name)
        
        if theme is None:
            logger.warning(f"Theme not found: {theme_name}, using default")
            theme = self.BUILTIN_THEMES.get("minimal_dark", {})
            theme_name = "minimal_dark"
        
        self.current_theme = theme
        self.current_theme_name = theme_name
        logger.info(f"Loaded theme: {theme_name}")
        return True
    
    def save_theme(self, theme_name: str, theme_data: Dict) -> bool:
        if "colors" not in theme_data:
            logger.error("Invalid theme structure")
            return False
        
        theme_file = self.theme_dir / "custom" / f"{theme_name}.json"
        
        try:
            with open(theme_file, 'w', encoding='utf-8') as f:
                json.dump(theme_data, f, indent=2)
            logger.info(f"Saved custom theme: {theme_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to save theme {theme_name}: {e}")
            return False
    
    def get_color(self, color_key: str, fallback: str = "#ffffff") -> str:
        if self.current_theme:
            return self.current_theme.get("colors", {}).get(color_key, fallback)
        return fallback
    
    def create_qss(self, additional_css: str = "") -> str:
        if not self.current_theme:
            return additional_css
        
        colors = self.current_theme.get("colors", {})
        fonts = self.current_theme.get("fonts", {})
        
        bg = colors.get('background', '#1a1a1a')
        text = colors.get('text', '#ffffff')
        surface = colors.get('surface', '#2d2d2d')
        border = colors.get('border', '#3d3d3d')
        accent = colors.get('accent', '#007AFF')
        font = fonts.get('primary', '-apple-system, sans-serif')
        
        qss = (
            "QWidget { background-color: " + bg + "; color: " + text + "; font-family: " + font + "; font-size: 13px; } "
            "QPushButton { background-color: " + surface + "; color: " + text + "; border: 1px solid " + border + "; border-radius: 4px; padding: 8px 16px; } "
            "QPushButton:hover { background-color: " + border + "; } "
            "QPushButton:pressed { background-color: " + accent + "; } "
            "QLineEdit, QTextEdit { background-color: " + surface + "; color: " + text + "; border: 1px solid " + border + "; border-radius: 4px; padding: 8px; } "
            "QLabel { color: " + text + "; } "
            "QCheckBox { color: " + text + "; spacing: 8px; } "
            "QSlider::groove:horizontal { background-color: " + border + "; height: 4px; border-radius: 2px; } "
            "QSlider::handle:horizontal { background-color: " + accent + "; width: 16px; height: 16px; margin: -6px 0; border-radius: 8px; } "
            "QGroupBox { border: 1px solid " + border + "; border-radius: 8px; margin-top: 16px; padding-top: 16px; } "
            "QMenuBar { background-color: " + bg + "; color: " + text + "; } "
            "QMenu { background-color: " + surface + "; color: " + text + "; border: 1px solid " + border + "; } "
            "QMenu::item:selected { background-color: " + accent + "; } "
        )
        
        return qss + additional_css

