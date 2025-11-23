from PyQt5.QtWidgets import QWidget, QHBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QFrame, QVBoxLayout
from PyQt5.QtChart import QChartView, QChart, QPieSeries, QLegend
from PyQt5.QtCore import Qt, QMargins
from PyQt5.QtGui import QPainter, QFont



class StatisticsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(32)

        # -------- ДАННЫЕ ДЛЯ ТАБЛИЦЫ --------
        sample_data = [
            ["26.10 13:12", "Ваулово – Чебаково, 308 км пк1", "ПЧ-4 Рыбинск", "Автобус"],
            ["26.10 13:07", "Сахтыш – Якшинский, 273 км пк 7", "ИЧ-1 Иваново", "Грузовой авто"],
            ["26.10 12:52", "Сендега – Дровинки, 384 км пк 10", "ИЧ-1 Иваново", "Легковой авто"],
        ]

        # -------- ТАБЛИЦА --------
        rows = len(sample_data)      # ← столько строк, сколько данных (без лишней пустой)
        cols = 4

        table = QTableWidget(rows, cols)
        table.setObjectName("statsTable")

        # Заголовки как в макете
        table.setHorizontalHeaderLabels([
            "Дата",
            "Место ДТП",
            "ПЧ/ИЧ",
            "Наименование ТС",
        ])

        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        table.verticalHeader().setVisible(False)

        for row, row_data in enumerate(sample_data):
            for col, value in enumerate(row_data):
                item = QTableWidgetItem(value)

                # Последний столбец (наименование трансп. средства) — жирным
                if col == 3:
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)

                table.setItem(row, col, item)

        table.setFixedWidth(650)   # ← ширина таблицы по макету
        layout.addWidget(table)

        # -------- КРУГОВАЯ ДИАГРАММА --------
        series = QPieSeries()
        series.append("Выезд на закрытый шлагбаум", 4)
        series.append("Остановка на пути", 2)
        series.append("Переезд через шлагбаум", 3)
        series.append("Неисправность оборудования", 1)
        series.append("Другие инциденты", 1)

        # круг в 2 раза больше, ближе к легенде
        series.setPieSize(0.9)             # сильно увеличили размер
        series.setHorizontalPosition(0.38) # ближе к тексту справа

        chart = QChart()
        chart.addSeries(series)
        chart.setAnimationOptions(QChart.NoAnimation)
        chart.setTitle("")
        # убираем фон и рамки вокруг диаграммы
        chart.setBackgroundVisible(False)
        chart.setPlotAreaBackgroundVisible(False)
        chart.setMargins(QMargins(0, 0, 0, 0))

        # легенда справа, шрифт 12
        legend = chart.legend()
        legend.setAlignment(Qt.AlignRight)
        legend.setFont(QFont("IBM Plex Sans", 8))
        legend.setMarkerShape(QLegend.MarkerShapeRectangle)
        legend.setMaximumWidth(300)

        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        chart_view.setMinimumWidth(520)
        chart_view.setMinimumHeight(150)   # больше высота под увеличенный круг
        chart_view.setStyleSheet("background: #ffffff; border: none;")
        # оборачиваем в фрейм без паддингов и границ
        chart_frame = QFrame()
        chart_frame.setObjectName("statsChartFrame")
        cf_layout = QVBoxLayout(chart_frame)
        cf_layout.setContentsMargins(0, 0, 0, 0)   # без паддингов вокруг диаграммы
        cf_layout.setSpacing(0)
        cf_layout.addWidget(chart_view)

        layout.addWidget(chart_frame, 4)

