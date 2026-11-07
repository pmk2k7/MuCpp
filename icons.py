import os
from typing import Dict
from PySide6.QtGui import QIcon, QPixmap

_ICONS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "icons")
_CACHE: Dict[str, QIcon] = {}


def get_icon(name: str) -> QIcon:
    """Returns a cached QIcon for the given icon name (without .svg extension)."""
    if name in _CACHE:
        return _CACHE[name]

    filename = f"{name}.svg" if not name.endswith(".svg") else name
    path = os.path.join(_ICONS_DIR, filename)
    if os.path.exists(path):
        icon = QIcon(path)
        _CACHE[name] = icon
        return icon

    # Fallback to empty icon
    return QIcon()


def get_app_icon() -> QIcon:
    """Returns the primary application icon for MuCpp."""
    return get_icon("app_logo")
