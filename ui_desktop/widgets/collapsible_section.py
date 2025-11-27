from PyQt5.QtWidgets import QWidget, QVBoxLayout, QToolButton, QFrame
from PyQt5.QtCore import Qt


class CollapsibleSection(QWidget):
    def __init__(self, title: str = "", parent=None):
        super().__init__(parent)

        self.toggle_button = QToolButton(text=title, checkable=True, checked=True)
        self.toggle_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.toggle_button.setArrowType(Qt.DownArrow)
        self.toggle_button.clicked.connect(self._on_toggled)
        self.toggle_button.setObjectName("collapsibleHeader")

        self.setTitle(title)
        self.content_area = QFrame()
        self.content_area.setObjectName("collapsibleContent")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(4)
        main_layout.addWidget(self.toggle_button)
        main_layout.addWidget(self.content_area)

    def setContentLayout(self, layout):
        layout.setContentsMargins(0, 0, 0, 0)
        self.content_area.setLayout(layout)

    def _on_toggled(self, checked: bool):
        self.content_area.setVisible(checked)
        self.toggle_button.setArrowType(Qt.DownArrow if checked else Qt.RightArrow)

    def setTitle(self, title: str):
        self.toggle_button.setText("  " + title)

    def title(self) -> str:
        return self.toggle_button.text()
