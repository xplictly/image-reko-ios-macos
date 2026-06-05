# Widgets package for WidgetWall

from app.widgets.base_widget import (
    BaseWidget,
    WIDGET_REGISTRY,
    create_widget,
    ClockWidget,
    CalendarWidget,
    NotesWidget,
    WeatherWidget,
    SystemWidget,
    QuotesWidget,
)

# Import additional widgets implemented in separate modules
from app.widgets.photo_widget import PhotoWidget
from app.widgets.music_widget import MusicWidget


__all__ = [
    'BaseWidget',
    'WIDGET_REGISTRY',
    'create_widget',
    'ClockWidget',
    'CalendarWidget',
    'NotesWidget',
    'WeatherWidget',
    'SystemWidget',
    'QuotesWidget',
    'PhotoWidget',
    'MusicWidget'
]

