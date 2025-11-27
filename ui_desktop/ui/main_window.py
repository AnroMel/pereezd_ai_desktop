# ui_desktop/ui/main_window.py

from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QStackedWidget,
    QScrollArea,
    QGroupBox,
    QTableWidget,
    QTableWidgetItem,
)
from PyQt5.QtCore import Qt, QTimer, QRectF
from PyQt5.QtGui import QPixmap, QPainter, QPainterPath

from widgets.collapsible_section import CollapsibleSection
from widgets.statistics_widget import StatisticsWidget
from widgets.trigger_carousel import TriggerCarousel

from paths import resource_path


# функция чтения событий из БД
from db import fetch_latest_trigger_events


# ======================= СТРАНИЦА АРХИВА ОТЧЁТОВ =======================

class ArchivePage(QWidget):
    """
    Вкладка "Архив отчётов".
    Показывает содержимое таблицы trigger_events.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.current_lang = "ru"

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        self.title_label = QLabel("Архив отчётов")
        self.title_label.setObjectName("archiveTitle")
        self.title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.title_label.setStyleSheet("font-size: 20px; font-weight: 600;")
        layout.addWidget(self.title_label)

        self.table = QTableWidget()
        self.table.setStyleSheet("""
            QTableWidget {
                color: #111111;
                font-size: 13px;
            }
            QHeaderView::section {
                color: #111111;
                font-weight: 600;
            }
        """)
        self.table.setObjectName("archiveTable")
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID",
            "Название",
            "Приоритет",
            "Статус",
            "Время",
            "Камера",
            "Переезд",
        ])

        header = self.table.horizontalHeader()
        header.setStretchLastSection(True)
        # растягиваем все колонки
        for i in range(self.table.columnCount()):
            header.setSectionResizeMode(i, header.Stretch)

        # СКРЫВАЕМ ЛЕВЫЙ НУМЕРАТОР СТРОК
        self.table.verticalHeader().setVisible(False)

        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)

        # таймер для автообновления
        self.timer = QTimer(self)
        self.timer.setInterval(2000)   # 2 секунды
        self.timer.timeout.connect(self.load_data)
        self.timer.start()

        self.load_data()

    def load_data(self):
        """Читает последние события из trigger_events и заполняет таблицу."""
        try:
            events = fetch_latest_trigger_events(limit=100)
        except Exception as e:
            print("ArchivePage: ошибка при запросе к БД:", e)
            return

        self.table.setRowCount(len(events))

        for row, ev in enumerate(events):
            ev_id = str(ev.get("id", ""))
            title = ev.get("title") or ""
            priority = str(ev.get("priority", ""))
            status = ev.get("status") or ""
            created_at = ev.get("created_at")
            time_str = ""
            if created_at is not None:
                try:
                    # created_at приходит как datetime из psycopg2
                    time_str = created_at.strftime("%Y-%m-%d %H:%M:%S")
                except Exception:
                    time_str = str(created_at)

            camera_id = str(ev.get("camera_id", ""))
            crossing_id = str(ev.get("crossing_id", ""))

            self.table.setItem(row, 0, QTableWidgetItem(ev_id))
            self.table.setItem(row, 1, QTableWidgetItem(title))
            self.table.setItem(row, 2, QTableWidgetItem(priority))
            self.table.setItem(row, 3, QTableWidgetItem(status))
            self.table.setItem(row, 4, QTableWidgetItem(time_str))
            self.table.setItem(row, 5, QTableWidgetItem(camera_id))
            self.table.setItem(row, 6, QTableWidgetItem(crossing_id))

    def set_language(self, lang: str):
        """Переключение языка заголовка и шапки таблицы."""
        self.current_lang = lang

        if lang == "ru":
            self.title_label.setText("Архив отчётов")
            self.table.setHorizontalHeaderLabels([
                "ID",
                "Название",
                "Приоритет",
                "Статус",
                "Время",
                "Камера",
                "Переезд",
            ])
        else:
            self.title_label.setText("Reports archive")
            self.table.setHorizontalHeaderLabels([
                "ID",
                "Title",
                "Priority",
                "Status",
                "Time",
                "Camera",
                "Crossing",
            ])


# ======================= ОСНОВНОЕ ОКНО =======================

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ПЕРЕЕЗД.AI")
        self.setMinimumSize(1312, 744)
        self.current_lang = "ru"

        self._build_ui()
        self.set_language("ru")

    # ---------- сборка интерфейса ----------

    def _build_ui(self):
        central = QWidget(self)
        self.setCentralWidget(central)

        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ----- HEADER -----
        header = QFrame()
        header.setObjectName("header")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(48, 24, 48, 24)
        header_layout.setSpacing(32)

        # ЛОГО
        self.logo_label = QLabel()
        self.logo_label.setObjectName("headerLogo")
        self.logo_label.setText('ПЕРЕЕЗД<span style="color:#003160">.AI</span>')
        self.logo_label.setTextFormat(Qt.RichText)
        self.logo_label.setAlignment(Qt.AlignVCenter)
        header_layout.addWidget(self.logo_label)

        header_layout.addStretch(1)

        # Навигация
        nav_layout = QHBoxLayout()
        nav_layout.setSpacing(48)

        self.btn_home = QPushButton("ГЛАВНАЯ")
        self.btn_home.setObjectName("navHome")
        self.btn_archive = QPushButton("АРХИВ ОТЧЕТОВ")
        self.btn_archive.setObjectName("navArchive")
        self.btn_profile = QPushButton("ЛИЧНЫЙ КАБИНЕТ")
        self.btn_profile.setObjectName("navProfile")

        for btn in (self.btn_home, self.btn_archive, self.btn_profile):
            btn.setCheckable(True)
            btn.setFlat(True)
            btn.setCursor(Qt.PointingHandCursor)

        self.btn_home.setChecked(True)

        nav_layout.addWidget(self.btn_home)
        nav_layout.addWidget(self.btn_archive)
        nav_layout.addWidget(self.btn_profile)

        header_layout.addLayout(nav_layout)

        # Кнопка языка
        self.lang_button = QPushButton("EN")
        self.lang_button.setObjectName("langButton")
        self.lang_button.setCursor(Qt.PointingHandCursor)
        self.lang_button.clicked.connect(self.toggle_language)
        header_layout.addWidget(self.lang_button, 0, Qt.AlignVCenter)

        root_layout.addWidget(header)

        # ----- BODY -----
        body = QFrame()
        body.setObjectName("body")
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(70, 24, 70, 24)
        body_layout.setSpacing(16)

        # Левая часть: страницы
        self.pages = QStackedWidget()

        # Главная (дашборд)
        self.page_dashboard = self._build_dashboard_page()
        self.pages.addWidget(self.page_dashboard)

        # Архив отчётов — НАША НОВАЯ СТРАНИЦА
        self.page_archive = ArchivePage()
        self.pages.addWidget(self.page_archive)

        # Личный кабинет — пока простой заглушкой
        self.page_profile = self._build_profile_page()
        self.pages.addWidget(self.page_profile)

        # подключаем навигацию
        self.btn_home.clicked.connect(lambda: self._switch_page(0))
        self.btn_archive.clicked.connect(lambda: self._switch_page(1))
        self.btn_profile.clicked.connect(lambda: self._switch_page(2))

        body_layout.addWidget(self.pages, 3)

        # Правая боковая панель (напоминания)
        self.sidebar = self._build_sidebar()
        body_layout.addWidget(self.sidebar, 1)

        root_layout.addWidget(body)

    # ---------- страницы ----------

    def _switch_page(self, index: int):
        self.pages.setCurrentIndex(index)
        self.btn_home.setChecked(index == 0)
        self.btn_archive.setChecked(index == 1)
        self.btn_profile.setChecked(index == 2)

    def _build_simple_page(self, title: str, text: str) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title_label = QLabel(title)
        title_label.setObjectName("simplePageTitle")
        text_label = QLabel(text)
        text_label.setWordWrap(True)

        layout.addWidget(title_label)
        layout.addWidget(text_label)
        layout.addStretch()
        return page

    def _build_dashboard_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        # Триггеры
        triggers_title = QLabel("Триггеры")
        triggers_title.setObjectName("sectionTitle")
        layout.addWidget(triggers_title)

        self.trigger_carousel = TriggerCarousel()
        layout.addWidget(self.trigger_carousel)

        # Статистика
        stats_section = CollapsibleSection("Статистика")
        stats_layout = QVBoxLayout()
        stats_widget = StatisticsWidget()
        stats_layout.addWidget(stats_widget)
        stats_section.setContentLayout(stats_layout)
        layout.addWidget(stats_section)

        layout.addStretch()

        # сохраняем ссылки для перевода
        self.dashboard_triggers_title = triggers_title
        self.dashboard_stats_section = stats_section

        return page

    def _build_sidebar(self) -> QWidget:
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(24)

        # ====================== НАПОМИНАНИЯ (1/3 высоты) ======================
        reminders_group = QGroupBox("Напоминания")
        reminders_group.setObjectName("remindersGroup")  # Добавьте это!
        rg_layout = QVBoxLayout(reminders_group)
        rg_layout.setContentsMargins(0, 0, 0, 0)
        rg_layout.setSpacing(8)

        # Просто текст "У вас нет напоминаний"
        no_reminders_label = QLabel("У вас нет напоминаний")
        no_reminders_label.setObjectName("noRemindersText")
        no_reminders_label.setAlignment(Qt.AlignCenter)
        no_reminders_label.setMinimumHeight(160)  # Увеличиваем высоту
        
        rg_layout.addWidget(no_reminders_label)
        layout.addWidget(reminders_group)

        # ====================== НОВОСТИ (2/3 высоты) ======================
        news_group = QGroupBox("Новости")
        news_group.setObjectName("newsGroup")  # Добавьте это!
        ng_layout = QVBoxLayout(news_group)
        ng_layout.setContentsMargins(0, 0, 0, 0)
        ng_layout.setSpacing(8)

        # Одна картинка с новостью
        news_image = QLabel()
        news_image.setObjectName("newsImage")
        news_image.setAlignment(Qt.AlignCenter)
        
        # Загружаем изображение
        image_path = resource_path("assets/img/news_1.jpg")
        pixmap = QPixmap(image_path)

        if not pixmap.isNull():
            # Масштабируем
            target_width = 300
            scaled_pixmap = pixmap.scaledToWidth(target_width, Qt.SmoothTransformation)

            # <<< ВАЖНО: применяем скругление >>>
            rounded_pixmap = self.round_corners(scaled_pixmap, 8)

            news_image.setPixmap(rounded_pixmap)
            news_image.setFixedHeight(rounded_pixmap.height())

            # Чтобы QLabel не показывал рамки
            news_image.setStyleSheet("border: none; background: transparent;")
        else:
            news_image.setFixedHeight(300)
            news_image.setStyleSheet("""
                background: #e9ecef;
                border-radius: 8px;
                border: 1px solid #ddd;
            """)
            news_image.setText("Новостное изображение")
            news_image.setAlignment(Qt.AlignCenter)

        ng_layout.addWidget(news_image)
        layout.addWidget(news_group)

        layout.addStretch()

        # Сохраняем для перевода
        self.sidebar_reminders_group = reminders_group
        self.sidebar_news_group = news_group
        self.no_reminders_label = no_reminders_label

        return sidebar

    # ---------- перевод / язык ----------

    def toggle_language(self):
        if self.current_lang == "ru":
            self.set_language("en")
        else:
            self.set_language("ru")

    def set_language(self, lang: str):
        self.current_lang = lang

        if lang == "ru":
            self.btn_home.setText("ГЛАВНАЯ")
            self.btn_archive.setText("АРХИВ ОТЧЁТОВ")
            self.btn_profile.setText("ЛИЧНЫЙ КАБИНЕТ")
            self.dashboard_triggers_title.setText("Триггеры")
            self.dashboard_stats_section.setTitle("Статистика")
            self.sidebar_reminders_group.setTitle("Напоминания")
            self.sidebar_news_group.setTitle("Новости")
            self.no_reminders_label.setText("У вас нет напоминаний")
            self.lang_button.setText("EN")
        else:
            self.btn_home.setText("HOME")
            self.btn_archive.setText("REPORTS ARCHIVE")
            self.btn_profile.setText("PROFILE")
            self.dashboard_triggers_title.setText("Triggers")
            self.dashboard_stats_section.setTitle("Statistics")
            self.sidebar_reminders_group.setTitle("Reminders")
            self.sidebar_news_group.setTitle("News")
            self.no_reminders_label.setText("You have no reminders")
            self.lang_button.setText("RU")

        # Обновляем язык на странице архива
        if hasattr(self, "page_archive"):
            self.page_archive.set_language(lang)

    def round_corners(self, pixmap: QPixmap, radius: int = 8) -> QPixmap:
        """Возвращает QPixmap с закруглёнными углами."""
        if pixmap.isNull():
            return pixmap

        rounded = QPixmap(pixmap.size())
        rounded.fill(Qt.transparent)

        painter = QPainter(rounded)
        painter.setRenderHint(QPainter.Antialiasing, True)

        path = QPainterPath()
        rect = QRectF(rounded.rect())          # <-- КОНВЕРТИРУЕМ В QRectF
        path.addRoundedRect(rect, float(radius), float(radius))

        painter.setClipPath(path)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()

        return rounded
    



# ======================= СТРАНИЦА ЛИЧНЫЙ КАБИНЕТ =======================
    def _build_profile_page(self) -> QWidget:
        page = QWidget()
        page.setObjectName("profilePage")

        layout = QHBoxLayout(page)
        layout.setContentsMargins(48, 24, 48, 24)
        layout.setSpacing(32)

        # ===== ЛЕВАЯ ЧАСТЬ (аватар + данные + контакты) =====
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(16)

        # --- верх: аватар + ФИО ---
        header_layout = QHBoxLayout()
        header_layout.setSpacing(16)

        # аватар
        avatar_label = QLabel()
        avatar_label.setObjectName("profileAvatar")
        avatar_label.setFixedSize(130, 130)

        avatar_pixmap = QPixmap(resource_path("assets/img/profile_avatar.png"))
        if not avatar_pixmap.isNull():
            avatar_pixmap = avatar_pixmap.scaled(
                120, 120,
                Qt.KeepAspectRatioByExpanding,
                Qt.SmoothTransformation
            )
            avatar_label.setPixmap(avatar_pixmap)
            avatar_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(avatar_label, 0, Qt.AlignTop)

        # должность + имя
        name_block = QVBoxLayout()
        name_block.setSpacing(4)

        position_label = QLabel("оператор по железнодорожным переездам")
        position_label.setObjectName("profilePosition")

        name_label = QLabel("Иванов Иван Иванович")
        name_label.setObjectName("profileName")

        name_block.addWidget(position_label)
        name_block.addWidget(name_label)
        name_block.addStretch()

        header_layout.addLayout(name_block, 1)
        left_layout.addLayout(header_layout)

        # --- дата рождения / возраст / стаж ---
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)

        birth_label = QLabel("Дата рождения: 01.01.2000      25 лет")
        birth_label.setObjectName("profileBirth")

        exp_label = QLabel("Стаж: 3 года")
        exp_label.setObjectName("profileExperience")

        info_layout.addWidget(birth_label)
        info_layout.addWidget(exp_label)

        left_layout.addLayout(info_layout)

        # --- карточка контактов ---
        contacts_card = QFrame()
        contacts_card.setObjectName("profileContactsCard")

        contacts_layout = QVBoxLayout(contacts_card)
        contacts_layout.setContentsMargins(24, 16, 24, 16)
        contacts_layout.setSpacing(12)

        # заголовок карточки
        card_header = QHBoxLayout()
        card_header.setSpacing(8)

        contacts_title = QLabel("Контакты")
        contacts_title.setObjectName("profileContactsTitle")

        plus_label = QLabel("+")
        plus_label.setObjectName("profileContactsAdd")

        card_header.addWidget(contacts_title)
        card_header.addStretch()
        card_header.addWidget(plus_label)

        contacts_layout.addLayout(card_header)

        # строка: город
        city_layout = QHBoxLayout()
        city_layout.setSpacing(8)

        city_icon = QLabel()
        city_icon.setObjectName("profileIconLocation")
        city_icon.setFixedSize(18, 18)
        city_pix = QPixmap(resource_path("assets/img/icon_location.png"))
        if not city_pix.isNull():
            city_pix = city_pix.scaled(
                18, 18,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            city_icon.setPixmap(city_pix)
        city_layout.addWidget(city_icon)

        city_label = QLabel("Ярославль")
        city_label.setObjectName("profileCity")
        city_layout.addWidget(city_label)
        city_layout.addStretch()

        contacts_layout.addLayout(city_layout)

        # строка: телефон
        phone_layout = QHBoxLayout()
        phone_layout.setSpacing(8)

        phone_icon = QLabel()
        phone_icon.setObjectName("profileIconPhone")
        phone_icon.setFixedSize(18, 18)
        phone_pix = QPixmap(resource_path("assets/img/icon_phone.png"))
        if not phone_pix.isNull():
            phone_pix = phone_pix.scaled(
                18, 18,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            phone_icon.setPixmap(phone_pix)
        phone_layout.addWidget(phone_icon)

        phone_label = QLabel("8(800)-555-35-35")
        phone_label.setObjectName("profilePhone")
        phone_layout.addWidget(phone_label)
        phone_layout.addStretch()

        contacts_layout.addLayout(phone_layout)

        # строка: иконки соцсетей
        social_layout = QHBoxLayout()
        social_layout.setSpacing(16)
        social_layout.addStretch()

        def make_social_icon(obj_name: str, path: str) -> QLabel:
            lbl = QLabel()
            lbl.setObjectName(obj_name)
            lbl.setFixedSize(24, 24)
            pm = QPixmap(resource_path(path))
            if not pm.isNull():
                pm = pm.scaled(
                    24, 24,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                lbl.setPixmap(pm)
            return lbl

        social_layout.addWidget(
            make_social_icon("profileIconTelegram", "assets/img/icon_telegram.png")
        )
        social_layout.addWidget(
            make_social_icon("profileIconVk", "assets/img/icon_vk.png")
        )
        social_layout.addWidget(
            make_social_icon("profileIconWhatsapp", "assets/img/icon_whatsapp.png")
        )

        contacts_layout.addLayout(social_layout)

        # строка: e-mail
        email_layout = QHBoxLayout()
        email_layout.setSpacing(8)
        email_layout.addStretch()

        email_icon = QLabel()
        email_icon.setObjectName("profileIconEmail")
        email_icon.setFixedSize(18, 18)
        email_pix = QPixmap(resource_path("assets/img/icon_email.png"))
        if not email_pix.isNull():
            email_pix = email_pix.scaled(
                18, 18,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            email_icon.setPixmap(email_pix)
        email_layout.addWidget(email_icon)

        email_label = QLabel("ivanov_20cool.@mail.ru")
        email_label.setObjectName("profileEmail")
        email_layout.addWidget(email_label)

        contacts_layout.addLayout(email_layout)

        left_layout.addWidget(contacts_card)
        left_layout.addStretch()

        layout.addWidget(left, 4)

        # ===== ПРАВАЯ ЧАСТЬ (меню профиля) =====
        right = QFrame()
        right.setObjectName("profileSidebar")

        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(24, 8, 0, 24)
        right_layout.setSpacing(8)

        menu_frame = QFrame()
        menu_frame.setObjectName("profileMenu")
        menu_layout = QVBoxLayout(menu_frame)
        menu_layout.setContentsMargins(0, 0, 0, 0)
        menu_layout.setSpacing(4)

        # активный пункт
        self.profile_menu_about = QPushButton("О себе")
        self.profile_menu_about.setObjectName("profileMenuItemActive")
        self.profile_menu_about.setFlat(True)
        self.profile_menu_about.setCursor(Qt.PointingHandCursor)

        # остальные пункты
        def make_menu_btn(text: str) -> QPushButton:
            btn = QPushButton(text)
            btn.setObjectName("profileMenuItem")
            btn.setFlat(True)
            btn.setCursor(Qt.PointingHandCursor)
            return btn

        self.profile_menu_photo = make_menu_btn("Фото")
        self.profile_menu_calendar = make_menu_btn("Календарь")
        self.profile_menu_instr = make_menu_btn("Инструкции")
        self.profile_menu_docs = make_menu_btn("Документы")
        self.profile_menu_salary = make_menu_btn("Зарплата")
        self.profile_menu_privacy = make_menu_btn("Приватность")

        for btn in [
            self.profile_menu_about,
            self.profile_menu_photo,
            self.profile_menu_calendar,
            self.profile_menu_instr,
            self.profile_menu_docs,
            self.profile_menu_salary,
            self.profile_menu_privacy,
        ]:
            menu_layout.addWidget(btn)

        right_layout.addWidget(menu_frame)
        right_layout.addStretch()

        # кнопка выхода
        self.profile_logout_btn = QPushButton("Выход")
        self.profile_logout_btn.setObjectName("profileLogout")
        self.profile_logout_btn.setFlat(True)
        self.profile_logout_btn.clicked.connect(self.logout_to_login)
        self.profile_logout_btn.setCursor(Qt.PointingHandCursor)

        right_layout.addWidget(self.profile_logout_btn, 0, Qt.AlignLeft | Qt.AlignBottom)

        layout.addWidget(right, 2)

        # красная вертикальная полоса справа
        red_bar = QFrame()
        red_bar.setObjectName("profileRedBar")
        red_bar.setFixedWidth(3)
        layout.addWidget(red_bar)

        # ссылки, если захочешь использовать при смене языка
        self.profile_name_label = name_label
        self.profile_position_label = position_label
        self.profile_birth_label = birth_label
        self.profile_exp_label = exp_label
        self.profile_contacts_title = contacts_title

        return page
    
    def logout_to_login(self): 
        from ui.login_window import LoginWindow
        self.login_window = LoginWindow()   # создаём новое окно логина
        self.login_window.show()            # показываем
        self.close()                        # закрываем текущий MainWindow

    def _switch_page(self, index: int):
        self.pages.setCurrentIndex(index)

        self.btn_home.setChecked(index == 0)
        self.btn_archive.setChecked(index == 1)
        self.btn_profile.setChecked(index == 2)

        # <-- вот это добавляем
        if index == 2:          # страница "Личный кабинет"
            self.sidebar.hide()  # сайдбар не виден и не занимает места
        else:
            self.sidebar.show()  # на остальных страницах показываем









