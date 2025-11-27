from PyQt5.QtWidgets import (
    QWidget,
    QScrollArea,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QFrame,
    QGraphicsDropShadowEffect,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QColor, QMovie

from paths import resource_path


class TriggerCard(QFrame):
    def __init__(
        self,
        image_path: str,
        title: str,
        info_lines: list[str],
        footer: str,
        parent=None,
    ):
        super().__init__(parent)
        self.setObjectName("triggerCard")
        self.setFixedSize(542, 500)  # по макету

        # тень снизу
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(16)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 60))
        self.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Картинка или GIF
        img_label = QLabel()
        img_label.setObjectName("triggerImage")
        img_label.setScaledContents(True)
        img_label.setMinimumHeight(280)
        img_label.setMaximumHeight(280)
        
        # Проверяем расширение файла
        if image_path.lower().endswith(('.gif', '.webp')):
            # Для GIF используем QMovie
            self.movie = QMovie(image_path)
            if not self.movie.isValid():
                # Если GIF не загрузился, показываем заглушку
                self._set_placeholder_image(img_label)
            else:
                img_label.setMovie(self.movie)
                self.movie.start()  # Запускаем анимацию
        else:
            # Для обычных изображений используем QPixmap
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                img_label.setPixmap(
                    pixmap.scaled(
                        542,
                        280,
                        Qt.KeepAspectRatioByExpanding,
                        Qt.SmoothTransformation,
                    )
                )
            else:
                self._set_placeholder_image(img_label)
        
        layout.addWidget(img_label)

        # ---- БЛОК ТЕКСТА ----
        text_block = QFrame()
        text_layout = QVBoxLayout(text_block)
        text_layout.setContentsMargins(20, 20, 20, 20)  # ← ПАДДИНГИ 20/40
        text_layout.setSpacing(12)

        # Заголовок
        title_label = QLabel(title)
        title_label.setObjectName("triggerTitle")
        title_label.setWordWrap(True)
        text_layout.addWidget(title_label)

        # Информационные строки
        for line in info_lines:
            label = QLabel()
            label.setObjectName("triggerInfo")
            label.setWordWrap(True)
            label.setTextFormat(Qt.RichText)

            # Логика жирного текста
            html = line
            if ":" in line:
                name, value = line.split(":", 1)
                name = name.strip()
                value = value.strip()

                if name == "Приоритет":
                    html = f"<b>{name}: {value}</b>"
                elif name in ("Рекомендуемые действия", "Оператор"):
                    html = f"<b>{name}:</b> {value}"
                else:
                    html = line

            label.setText(f'<span style="font-size:15px;">{html}</span>')
            text_layout.addWidget(label)

        # footer
        footer_label = QLabel(footer)
        footer_label.setObjectName("triggerFooter")
        text_layout.addWidget(footer_label, 0, Qt.AlignRight)

        # Добавляем блок текста в карточку
        layout.addWidget(text_block)


class TriggerCarousel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setFrameShape(QFrame.NoFrame)

        # белый фон вместо серого
        scroll.setStyleSheet("QScrollArea { background: #ffffff; border: none; }")
        scroll.viewport().setStyleSheet("background: #ffffff;")

        container = QWidget()
        container.setStyleSheet("background: #ffffff;")
        h_layout = QHBoxLayout(container)
        h_layout.setContentsMargins(0, 0, 0, 24)
        h_layout.setSpacing(16)

        # Пример 3 карточек
        card1 = TriggerCard(
            resource_path("assets/gif/video.gif"),
            "Машина едет на закрытый шлагбаум",
            [
                "Приоритет: Высокий",
                "Рекомендуемые действия: Немедленно оповестить водителя через громкоговоритель",
                "Оператор: Иванова Людмила Васильевна",
            ],
            "13:54   26 октября 2025",
        )
        card2 = TriggerCard(
            resource_path("assets/gif/video1.gif"),
            "Машина едет на запрещающий сигнал светофора",
            [
                "Приоритет: Высокий",
                "Рекомендуемые действия: Немедленно оповестить водителя через громкоговоритель",
                "Оператор: Ларина Татьяна Павловна",
            ],
            "15:15   26 октября 2025",
        )
        card3 = TriggerCard(
            resource_path("assets/gif/video2.gif"),
            "Неисправность оборудования",
            [
                "Приоритет: Средний",
                "Рекомендуемые действия: Оповестить техническую службу",
                "Оператор: Глушев А.В.",
            ],
            "16:02   26 октября 2025",
        )

        for c in (card1, card2, card3):
            h_layout.addWidget(c)

        h_layout.addStretch()
        scroll.setWidget(container)
        root_layout.addWidget(scroll)

