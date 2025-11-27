# paths.py
import sys
from pathlib import Path


def resource_path(relative: str) -> str:
    """
    Пути к ресурсам, которые работают и в .py, и в .exe.

    relative: "assets/img/login_bg.png", "styles/main.qss" и т.д.
    Возвращает строку с абсолютным путём.
    """
    # когда запущено из exe (PyInstaller)
    if hasattr(sys, "_MEIPASS"):
        base_path = Path(sys._MEIPASS)
    else:
        # когда запускаем обычный main.py
        base_path = Path(__file__).resolve().parent

    return str(base_path / relative)
