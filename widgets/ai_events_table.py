# widgets/ai_events_table.py
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtWidgets import QAbstractItemView

from db import fetch_latest_ai_raw_events


class AiEventsTable(QWidget):
    """
    Таблица, которая показывает последние события из ai_raw_events.
    Автообновление раз в refresh_ms миллисекунд.
    """

    def __init__(self, parent=None, refresh_ms: int = 3000, limit: int = 50):
        super().__init__(parent)
        self._limit = limit

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID",
            "Время",
            "Камера",
            "Переезд",
            "Тип триггера",
            "Уверенность",
        ])

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        layout.addWidget(self.table)

        # таймер автообновления
        self.timer = QTimer(self)
        self.timer.setInterval(refresh_ms)
        self.timer.timeout.connect(self.load_data)
        self.timer.start()

        # первая загрузка
        self.load_data()

    def load_data(self):
        try:
            events = fetch_latest_ai_raw_events(self._limit)
        except Exception as e:
            print("Ошибка при загрузке ai_raw_events:", e)
            return

        self.table.setRowCount(len(events))

        for row, ev in enumerate(events):
            ev_id = str(ev["id"])
            ts = ev["detected_at"]
            ts_str = ts.strftime("%Y-%m-%d %H:%M:%S") if ts else ""

            camera_id = str(ev.get("camera_id") or "")
            crossing_id = str(ev.get("crossing_id") or "")
            trigger_type_id = str(ev.get("trigger_type_id") or "")
            confidence = ev.get("confidence")
            conf_str = f"{confidence:.2f}" if confidence is not None else ""

            self.table.setItem(row, 0, QTableWidgetItem(ev_id))
            self.table.setItem(row, 1, QTableWidgetItem(ts_str))
            self.table.setItem(row, 2, QTableWidgetItem(camera_id))
            self.table.setItem(row, 3, QTableWidgetItem(crossing_id))
            self.table.setItem(row, 4, QTableWidgetItem(trigger_type_id))
            self.table.setItem(row, 5, QTableWidgetItem(conf_str))
