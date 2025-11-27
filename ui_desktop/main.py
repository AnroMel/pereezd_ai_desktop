import os
import sys

# 1) Очищаем возможные проблемные переменные окружения
os.environ.pop("QT_PLUGIN_PATH", None)
os.environ.pop("QT_QPA_PLATFORM_PLUGIN_PATH", None)

# 2) Явно указываем путь к плагинам из PyQt5 в виртуальном окружении
import PyQt5
qt_plugins_dir = os.path.join(os.path.dirname(PyQt5.__file__), "Qt5", "plugins")
os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = qt_plugins_dir

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFontDatabase, QFont
from ui.login_window import LoginWindow

from paths import resource_path   # ← НОВОЕ


def load_fonts():
    """Подключаем семейство IBM Plex Sans из assets/fonts."""
    font_db = QFontDatabase()
    font_paths = [
        resource_path("assets/fonts/IBMPlexSans-Regular.ttf"),
        resource_path("assets/fonts/IBMPlexSans-Medium.ttf"),
        resource_path("assets/fonts/IBMPlexSans-Bold.ttf"),
    ]
    for path in font_paths:
        font_id = font_db.addApplicationFont(path)
        if font_id == -1:
            print(f"Не удалось подключить шрифт: {path}")

    if "IBM Plex Sans" in QFontDatabase().families():
        QApplication.setFont(QFont("IBM Plex Sans", 10))


def load_styles(app: QApplication):
    try:
        style_path = resource_path("styles/main.qss")
        with open(style_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        print("Файл стилей styles/main.qss не найден")


def main():
    print("=== MAIN STARTED ===")
    app = QApplication(sys.argv)
    load_fonts()
    load_styles(app)

    win = LoginWindow()
    win.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
