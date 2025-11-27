# ui_desktop/ui/login_window.py

from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFrame,
    QMessageBox,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIcon, QPainter


from ui.main_window import MainWindow
from paths import resource_path

class BackgroundFrame(QFrame):
    def __init__(self, image_path: str, parent=None):
        super().__init__(parent)
        self._pixmap = QPixmap(image_path)

    def paintEvent(self, event):
        if self._pixmap.isNull():
            return super().paintEvent(event)

        painter = QPainter(self)
        # Масштабируем картинку под размер окна с обрезкой (аналог cover)
        scaled = self._pixmap.scaled(
            self.size(),
            Qt.KeepAspectRatioByExpanding,
            Qt.SmoothTransformation
        )
        x = (self.width() - scaled.width()) // 2
        y = (self.height() - scaled.height()) // 2
        painter.drawPixmap(x, y, scaled)


class LoginWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ПЕРЕЕЗД.AI — Авторизация")
        self.setMinimumSize(1312, 744)
        self._build_ui()

    def _build_ui(self):
        central = QWidget(self)
        self.setCentralWidget(central)

        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        bg_frame = BackgroundFrame(resource_path("assets/img/login_bg.png"))
        bg_frame.setObjectName("loginBackground")
        bg_frame.setObjectName("loginBackground")
        root_layout.addWidget(bg_frame)

        layout = QVBoxLayout(bg_frame)
        layout.setAlignment(Qt.AlignCenter)

        content = QVBoxLayout()
        content.setSpacing(24)
        layout.addLayout(content)

        # Логотип
        logo_label = QLabel()
        logo_label.setObjectName("loginLogo")
        pixmap = QPixmap(resource_path("assets/img/logo.png"))
        if not pixmap.isNull():
            logo_label.setPixmap(pixmap)
            logo_label.setScaledContents(True)
            logo_label.setFixedSize(360, 72)  # логотип крупнее
        else:
            logo_label.setText("ПЕРЕЕЗД.AI")
        logo_label.setAlignment(Qt.AlignCenter)
        content.addWidget(logo_label, 0, Qt.AlignHCenter)

        # Дополнительный отступ под логотипом
        content.addSpacing(24)



                # Поле логина
        self.login_edit = QLineEdit()
        self.login_edit.setObjectName("loginEdit")
        self.login_edit.setPlaceholderText("ЛОГИН")
        self.login_edit.setFixedWidth(444)

        login_icon = QIcon(resource_path("assets/img/icon_user.png"))
        self.login_edit.addAction(login_icon, QLineEdit.LeadingPosition)

        content.addWidget(self.login_edit, 0, Qt.AlignHCenter)

        # Поле пароля
        self.password_edit = QLineEdit()
        self.password_edit.setObjectName("passwordEdit")
        self.password_edit.setPlaceholderText("ПАРОЛЬ")
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setFixedWidth(444)

        lock_icon = QIcon(resource_path("assets/img/icon_lock.png"))
        self.password_edit.addAction(lock_icon, QLineEdit.LeadingPosition)

        content.addWidget(self.password_edit, 0, Qt.AlignHCenter)

        # Кнопка входа
        self.login_button = QPushButton("ВОЙТИ")
        self.login_button.setObjectName("loginButton")
        self.login_button.setFixedWidth(300)
        self.login_button.clicked.connect(self.handle_login)
        content.addWidget(self.login_button, 0, Qt.AlignHCenter)


        # "Забыли пароль?"
        bottom_layout = QHBoxLayout()
        bottom_layout.setAlignment(Qt.AlignCenter)
        self.forgot_button = QPushButton("забыли пароль?")
        self.forgot_button.setObjectName("forgotPasswordButton")
        self.forgot_button.setFlat(True)
        self.forgot_button.clicked.connect(self.handle_forgot_password)
        bottom_layout.addWidget(self.forgot_button)
        content.addLayout(bottom_layout)

    # В этой версии авторизация фейковая
    def handle_login(self):
        login = self.login_edit.text().strip()
        password = self.password_edit.text().strip()
        
        # Проверка логина и пароля
        if login == "admin" and password == "admin123":
            # Успешная авторизация
            self.main_window = MainWindow()
            self.main_window.show()
            self.close()
        else:
            # Неверные данные
            self.show_error_message()

    def show_error_message(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("Ошибка авторизации")
        msg.setText("Неверный логин или пароль. Попробуйте снова.")
        msg.setIcon(QMessageBox.Warning)
        
        # Кастомный стиль для окна ошибки
        msg.setStyleSheet("""
            QMessageBox {
                font-family: 'IBM Plex Sans';
                background-color: white;
            }
            QLabel {
                font-size: 14px;
                color: #D32F2F;
            }
            QPushButton {
                min-width: 80px;
                padding: 6px 16px;
                background: #D32F2F;
                color: white;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #B71C1C;
            }
        """)
        
        msg.exec_()

    def handle_forgot_password(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("Восстановление пароля")
        msg.setText("Обратитесь к администратору.")
        msg.setIcon(QMessageBox.Information)

        # Кастомный стиль
        msg.setStyleSheet("""
            QMessageBox {
                font-family: 'IBM Plex Sans';
                color: #1044D4;
            }
            QLabel {
                font-size: 14px;
                color: #1044D4;
            }
            QPushButton {
                min-width: 80px;
                padding: 6px 16px;
                background: #1044D4;
                color: white;
                border-radius: 4px;
            }
            QPushButton:hover {
                background: #0d3bb3;
            }
        """)

        msg.exec_()
