# main.py  (PyQt6, лента тревог из Supabase)

import sys

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QListWidget,
    QStackedWidget,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
)

from datetime import datetime

# вместо db импортируем функции из Supabase-клиента
from supabase_client import fetch_latest_ai_events


class AlertsPage(QWidget):
    """
    Экран "Лента тревог".
    Показывает события из таблицы ai_raw_events (Supabase).
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)

        # Заголовок
        title = QLabel("Лента тревог")
        title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        # Таблица
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID",
            "Тип события",
            "Время",
            "Уверенность",
            "Камера",
            "Переезд",
        ])

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        # двойной клик по строке
        self.table.doubleClicked.connect(self.on_row_double_clicked)

        layout.addWidget(self.table)

        # Таймер для авто-обновления данных
        self.timer = QTimer(self)
        self.timer.setInterval(2000)  # 2000 мс = 2 секунды
        self.timer.timeout.connect(self.load_data)
        self.timer.start()

        # первая загрузка
        self.load_data()

    def _format_datetime(self, value) -> str:
        """Красиво форматируем дату/время, которое пришло из Supabase."""
        if isinstance(value, str):
            try:
                # '2025-11-22T18:10:05.123456+00:00' или '...Z'
                dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
                return dt.strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                return value
        return str(value) if value is not None else ""

    def load_data(self):
        """
        Тянем данные из Supabase и заполняем таблицу.
        Ожидаем, что fetch_latest_ai_events возвращает
        список dict'ов с ключами:
        id, detected_at, confidence, camera_id, crossing_id, raw_metadata (JSON)
        """
        try:
            events = fetch_latest_ai_events(limit=100)
        except Exception as e:
            print("Ошибка при загрузке данных из Supabase:", e)
            return

        self.table.setRowCount(len(events))

        for row, ev in enumerate(events):
            ev_id = str(ev.get("id", ""))

            detected_at = self._format_datetime(ev.get("detected_at"))
            conf = ev.get("confidence")
            conf_str = f"{conf:.2f}" if isinstance(conf, (int, float)) else (str(conf) if conf is not None else "")

            camera_id = ev.get("camera_id")
            crossing_id = ev.get("crossing_id")

            raw = ev.get("raw_metadata") or {}
            ev_type = raw.get("type", "—")

            self.table.setItem(row, 0, QTableWidgetItem(ev_id))
            self.table.setItem(row, 1, QTableWidgetItem(str(ev_type)))
            self.table.setItem(row, 2, QTableWidgetItem(detected_at))
            self.table.setItem(row, 3, QTableWidgetItem(conf_str))
            self.table.setItem(row, 4, QTableWidgetItem(str(camera_id or "")))
            self.table.setItem(row, 5, QTableWidgetItem(str(crossing_id or "")))

    def on_row_double_clicked(self, index):
        row = index.row()
        ev_id_item = self.table.item(row, 0)
        ev_type_item = self.table.item(row, 1)

        if not ev_id_item or not ev_type_item:
            return

        ev_id = ev_id_item.text()
        ev_type = ev_type_item.text()

        print(f"Двойной клик по событию {ev_id}: {ev_type}")

        QMessageBox.information(
            self,
            "Событие",
            f"Двойной клик по событию {ev_id}:\n{ev_type}",
        )


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("ПЕРЕЕЗД.AI — операторский пульт")
        self.resize(1200, 700)

        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)
        self.setCentralWidget(central_widget)

        # Левая панель навигации
        self.nav_list = QListWidget()
        self.nav_list.addItem("Лента тревог")
        self.nav_list.addItem("Видео / Камеры")
        self.nav_list.addItem("Инциденты / Отчёты")
        self.nav_list.addItem("Настройки")
        self.nav_list.setFixedWidth(220)

        # Правая часть — стек страниц
        self.stack = QStackedWidget()

        alerts_page = AlertsPage()
        video_page = self._create_placeholder_page("Здесь будет видео с камер")
        incidents_page = self._create_placeholder_page("Здесь будет список инцидентов")
        settings_page = self._create_placeholder_page("Здесь будут настройки")

        self.stack.addWidget(alerts_page)
        self.stack.addWidget(video_page)
        self.stack.addWidget(incidents_page)
        self.stack.addWidget(settings_page)

        main_layout.addWidget(self.nav_list)
        main_layout.addWidget(self.stack, stretch=1)

        self.nav_list.currentRowChanged.connect(self.stack.setCurrentIndex)
        self.nav_list.setCurrentRow(0)

    def _create_placeholder_page(self, text: str) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        label = QLabel(text)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        return page


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
