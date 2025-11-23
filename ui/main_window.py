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
    QVBoxLayout,
    QSpacerItem,
    QSizePolicy,
    QToolButton
)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QPixmap, QDesktopServices

from widgets.collapsible_section import CollapsibleSection
from widgets.statistics_widget import StatisticsWidget
from widgets.trigger_carousel import TriggerCarousel


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ПЕРЕЕЗД.AI")
        self.setMinimumSize(1312, 744)
        self.current_lang = "ru"  
        self._build_ui()
        self.set_language("ru")

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

        # ЛОГОТИП ПЕРЕЕЗД.AI
        self.logo_label = QLabel()
        self.logo_label.setObjectName("headerLogo")
        self.logo_label.setText('ПЕРЕЕЗД<span style="color:#003160">.AI</span>')
        self.logo_label.setTextFormat(Qt.RichText)
        self.logo_label.setAlignment(Qt.AlignVCenter)
        header_layout.addWidget(self.logo_label)

        # растяжка между логотипом и навигацией
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

        # ----- MAIN CONTENT (body) -----
        body = QFrame()
        body.setObjectName("body")
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(70, 24, 70, 24)
        body_layout.setSpacing(16)

        # Левая часть: QStackedWidget
        self.pages = QStackedWidget()

        # Страница "Главная" (дашборд)
        self.page_dashboard = self._build_dashboard_page()
        self.pages.addWidget(self.page_dashboard)

        # Страница "Архив отчетов"
        self.page_archive = self._build_simple_page(
            "Архив отчетов", "Здесь будет список архивных отчётов."
        )

        # Страница "Личный кабинет"
        self.page_profile = self._build_simple_page(
            "Личный кабинет", "Здесь будут настройки пользователя и профиль."
        )

        # Навигация между страницами
        self.btn_home.clicked.connect(lambda: self._switch_page(0))
        self.btn_archive.clicked.connect(lambda: self._switch_page(1))
        self.btn_profile.clicked.connect(lambda: self.pages.setCurrentIndex(2))
        body_layout.addWidget(self.pages, 3)

        # Правая боковая панель
        sidebar = self._build_sidebar()
        body_layout.addWidget(sidebar, 1)

        root_layout.addWidget(body)

        # Начальный язык
        self.set_language("ru")

    # ----------------- ПЕРЕКЛЮЧЕНИЕ СТРАНИЦ -----------------
    def _switch_page(self, index: int):
        self.pages.setCurrentIndex(index)
        # Обновляем состояние кнопок
        self.btn_home.setChecked(index == 0)
        self.btn_archive.setChecked(index == 1)
        self.btn_profile.setChecked(index == 2)

    # ----------------- СТРАНИЦЫ -----------------
    def _build_simple_page(self, title: str, text: str) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
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

        # ---- Триггеры ----
        triggers_title = QLabel("Триггеры")
        triggers_title.setObjectName("sectionTitle")
        layout.addWidget(triggers_title)

        self.trigger_carousel = TriggerCarousel()
        layout.addWidget(self.trigger_carousel)

        # ---- Статистика (collapsible) ----
        stats_section = CollapsibleSection("Статистика")
        stats_layout = QVBoxLayout()
        stats_widget = StatisticsWidget()
        stats_layout.addWidget(stats_widget)
        stats_section.setContentLayout(stats_layout)
        layout.addWidget(stats_section)

        layout.addStretch()

        # сохраним ссылки для перевода
        self.dashboard_triggers_title = triggers_title
        self.dashboard_stats_section = stats_section

        return page

    # ----------------- САЙДБАР -----------------
    def _build_sidebar(self) -> QWidget:
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")

        # Основной лейаут: две зоны (1/3 и 2/3)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ====================== НАПОМИНАНИЯ (верхний блок, 1/3) ======================
        reminders_group = QGroupBox("Напоминания")
        reminders_group.setObjectName("sidebarGroup")
        rg_layout = QVBoxLayout(reminders_group)
        rg_layout.setContentsMargins(16, 8, 16, 8)   # небольшие внутренние отступы
        rg_layout.setSpacing(8)

        reminders_scroll = QScrollArea()
        reminders_scroll.setObjectName("sidebarScroll")
        reminders_scroll.setWidgetResizable(True)
        reminders_scroll.setFrameShape(QFrame.NoFrame)
        reminders_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        reminders_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        reminders_scroll.setViewportMargins(0, 0, 0, 0)

        reminders_container = QWidget()
        reminders_layout = QVBoxLayout(reminders_container)
        reminders_layout.setContentsMargins(0, 0, 0, 0)
        reminders_layout.setSpacing(12)

        # хотя бы одно напоминание
        reminders_layout.addWidget(self._create_reminder_item(
            "Необходимо заполнить отчёт о происшествии на переезде пересечений "
            "улиц Чернопрудной и Поморской г. Ярославль"
        ))
        # можно добавить ещё, если нужно
        # reminders_layout.addWidget(self._create_reminder_item("..."))

        reminders_layout.addStretch()

        reminders_scroll.setWidget(reminders_container)
        reminders_container.setStyleSheet("background:#ffffff;")

        rg_layout.addWidget(reminders_scroll)
        layout.addWidget(reminders_group, 1)   # вес 1 → 1/3 высоты

        # ====================== НОВОСТИ (нижний блок, 2/3) ======================
        news_group = QGroupBox("Новости")
        news_group.setObjectName("sidebarGroup")
        ng_layout = QVBoxLayout(news_group)
        ng_layout.setContentsMargins(16, 8, 16, 8)
        ng_layout.setSpacing(8)

        news_scroll = QScrollArea()
        news_scroll.setObjectName("sidebarScroll")
        news_scroll.setWidgetResizable(True)
        news_scroll.setFrameShape(QFrame.NoFrame)
        news_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        news_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        news_scroll.setViewportMargins(0, 0, 0, 0)

        news_container = QWidget()
        news_layout = QVBoxLayout(news_container)
        news_layout.setContentsMargins(0, 0, 0, 0)
        news_layout.setSpacing(20)

        news_layout.addWidget(self._create_news_item(
            "Внимание! Новый протокол",
            "Новый протокол безопасности для работы с аварийными ситуациями "
            "вступит в силу с 01.01.2026",
            "assets/img/news_1.jpg"
        ))
        news_layout.addWidget(self._create_news_item(
            "Прогнозы и плановые события",
            "Обновлён план тренингов и мероприятий по безопасности "
            "в Ярославской области.",
            "assets/img/news_2.jpg"
        ))
        news_layout.addStretch()

        news_scroll.setWidget(news_container)
        news_container.setStyleSheet("background:#ffffff;")

        ng_layout.addWidget(news_scroll)
        layout.addWidget(news_group, 2)   # вес 2 → 2/3 высоты

        # для смены языка
        self.sidebar_reminders_group = reminders_group
        self.sidebar_news_group = news_group

        return sidebar



    def _create_news_item(self, title: str, text: str, image_path: str) -> QWidget:
        card = QFrame()
        # БЫЛО: card.setObjectName("newsCard")
        card.setObjectName("newsItem")   # <-- имя как в QSS

        layout = QVBoxLayout(card)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        img_label = QLabel()
        # это имя в QSS не используется, можно оставить как есть или убрать
        img_label.setObjectName("newsImage")

        pixmap = QPixmap(image_path)
        target_width = 260

        if not pixmap.isNull():
            img_label.setPixmap(pixmap.scaledToWidth(
                target_width,
                Qt.SmoothTransformation
            ))
            img_label.setFixedWidth(target_width)
        else:
            img_label.setFixedWidth(target_width)

        img_label.setScaledContents(True)
        layout.addWidget(img_label)

        title_label = QLabel(title)
        title_label.setObjectName("newsTitle")
        title_label.setWordWrap(True)
        title_label.setMaximumWidth(target_width)
        layout.addWidget(title_label)

        text_label = QLabel(text)
        text_label.setObjectName("newsText")
        text_label.setWordWrap(True)
        text_label.setMaximumWidth(target_width)
        layout.addWidget(text_label)

        return card




    def _create_news_item(self, title: str, text: str, image_path: str) -> QWidget:
        card = QFrame()
        card.setObjectName("newsCard")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Картинка
        img_label = QLabel()
        img_label.setObjectName("newsImage")
        pixmap = QPixmap(image_path)
        target_width = 260  # фиксированная ширина карточки-изображения

        if not pixmap.isNull():
            img_label.setPixmap(pixmap.scaledToWidth(
                target_width,
                Qt.SmoothTransformation
            ))
            img_label.setFixedWidth(target_width)
        else:
            img_label.setFixedWidth(target_width)

        img_label.setScaledContents(True)
        layout.addWidget(img_label)

        # Заголовок по ширине картинки
        title_label = QLabel(title)
        title_label.setObjectName("newsTitle")
        title_label.setWordWrap(True)
        title_label.setMaximumWidth(target_width)
        layout.addWidget(title_label)

        # Текст по той же ширине
        text_label = QLabel(text)
        text_label.setObjectName("newsText")
        text_label.setWordWrap(True)
        text_label.setMaximumWidth(target_width)
        layout.addWidget(text_label)

        return card

    # ----------------- ПЕРЕВОД -----------------
    def toggle_language(self):
        if self.current_lang == "ru":
            self.set_language("en")
        else:
            self.set_language("ru")

    def set_language(self, lang: str):
        self.current_lang = lang

        if lang == "ru":
            self.btn_home.setText("ГЛАВНАЯ")
            self.btn_archive.setText("АРХИВ ОТЧЕТОВ")
            self.btn_profile.setText("ЛИЧНЫЙ КАБИНЕТ")
            self.dashboard_triggers_title.setText("Триггеры")
            self.dashboard_stats_section.setTitle("Статистика")
            self.sidebar_reminders_group.setTitle("Напоминания  2")
            self.sidebar_news_group.setTitle("Новости  4")
            self.lang_button.setText("EN")   # показываем, на какой язык переключимся
        else:
            self.btn_home.setText("HOME")
            self.btn_archive.setText("REPORTS ARCHIVE")
            self.btn_profile.setText("PROFILE")
            self.dashboard_triggers_title.setText("Triggers")
            self.dashboard_stats_section.setTitle("Statistics")
            self.sidebar_reminders_group.setTitle("Reminders  2")
            self.sidebar_news_group.setTitle("News  4")
            self.lang_button.setText("RU")



        # В реальном приложении сюда же можно добавить перевод динамического
        # контента (триггеры, новости) в зависимости от языка.

    
    def _build_profile_page(self) -> QWidget:
        page = QWidget()
        page.setObjectName("profilePage")

        root_layout = QHBoxLayout(page)
        root_layout.setContentsMargins(48, 24, 48, 24)
        root_layout.setSpacing(32)

        # ============== ЛЕВАЯ ЧАСТЬ (основной контент) ==============
        left = QFrame()
        left.setObjectName("profileMain")
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(24)

        # --- верхний блок: аватар + ФИО ---
        header_frame = QFrame()
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(16)

        avatar_label = QLabel()
        avatar_label.setObjectName("profileAvatar")
        avatar_pix = QPixmap("assets/img/profile_avatar.jpg")  # поменяешь путь
        if not avatar_pix.isNull():
            avatar_pix = avatar_pix.scaled(96, 96, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            avatar_label.setPixmap(avatar_pix)
        avatar_label.setFixedSize(96, 96)

        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(4)

        role_label = QLabel("оператор по железнодорожным переездам")
        role_label.setObjectName("profileRole")

        name_label = QLabel("Иванов Иван Иванович")
        name_label.setObjectName("profileName")

        dates_label = QLabel("Дата рождения: 01.01.2000    25 лет")
        dates_label.setObjectName("profileDates")

        exp_label = QLabel("Стаж: 3 года")
        exp_label.setObjectName("profileDates")

        info_layout.addWidget(role_label)
        info_layout.addWidget(name_label)
        info_layout.addSpacing(8)
        info_layout.addWidget(dates_label)
        info_layout.addWidget(exp_label)

        header_layout.addWidget(avatar_label, 0, Qt.AlignTop)
        header_layout.addLayout(info_layout)
        header_layout.addStretch()

        left_layout.addWidget(header_frame)

        # --- блок контактов ---
        contacts_card = QFrame()
        contacts_card.setObjectName("profileContactsCard")
        contacts_layout = QVBoxLayout(contacts_card)
        contacts_layout.setContentsMargins(24, 16, 24, 16)
        contacts_layout.setSpacing(12)

        # заголовок "Контакты  +"
        contacts_header = QHBoxLayout()
        contacts_title = QLabel("Контакты")
        contacts_title.setObjectName("profileContactsTitle")
        btn_add = QToolButton()
        btn_add.setText("+")
        btn_add.setObjectName("profileContactsAdd")
        btn_add.setAutoRaise(True)
        contacts_header.addWidget(contacts_title)
        contacts_header.addStretch()
        contacts_header.addWidget(btn_add)

        contacts_layout.addLayout(contacts_header)

        # строка: город
        row_city = QHBoxLayout()
        icon_city = QLabel()
        icon_city.setPixmap(QPixmap("assets/img/icon_location.png").scaled(16, 16, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        icon_city.setFixedSize(16, 16)
        lbl_city = QLabel("Ярославль")
        lbl_city.setObjectName("profileContactText")
        row_city.addWidget(icon_city)
        row_city.addSpacing(8)
        row_city.addWidget(lbl_city)
        row_city.addStretch()
        contacts_layout.addLayout(row_city)

        # строка: телефон + соцсети
        row_phone = QHBoxLayout()
        icon_phone = QLabel()
        icon_phone.setPixmap(QPixmap("assets/img/icon_phone.png").scaled(16, 16, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        icon_phone.setFixedSize(16, 16)
        lbl_phone = QLabel("8(800)-555-35-35")
        lbl_phone.setObjectName("profileContactText")

        row_phone.addWidget(icon_phone)
        row_phone.addSpacing(8)
        row_phone.addWidget(lbl_phone)

        row_phone.addStretch()

        # соцсети (кнопки)
        btn_tg = QToolButton()
        btn_tg.setObjectName("profileSocial")
        btn_tg.setIcon(QPixmap("assets/img/icon_telegram.png"))
        btn_vk = QToolButton()
        btn_vk.setObjectName("profileSocial")
        btn_vk.setIcon(QPixmap("assets/img/icon_vk.png"))
        btn_wh = QToolButton()
        btn_wh.setObjectName("profileSocial")
        btn_wh.setIcon(QPixmap("assets/img/icon_whatsapp.png"))

        for b in (btn_tg, btn_vk, btn_wh):
            b.setCursor(Qt.PointingHandCursor)
            b.setAutoRaise(True)

        btn_tg.clicked.connect(lambda: self.open_link("https://t.me/username"))
        btn_vk.clicked.connect(lambda: self.open_link("https://vk.com/username"))
        btn_wh.clicked.connect(lambda: self.open_link("https://wa.me/79999999999"))

        row_phone.addWidget(btn_tg)
        row_phone.addWidget(btn_vk)
        row_phone.addWidget(btn_wh)

        contacts_layout.addLayout(row_phone)

        # строка: email справа
        row_email = QHBoxLayout()
        row_email.addStretch()
        lbl_email_icon = QLabel()
        lbl_email_icon.setPixmap(QPixmap("assets/img/icon_mail.png").scaled(16, 16, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        lbl_email_icon.setFixedSize(16, 16)
        lbl_email = QLabel("ivanov_20cool@mail.ru")
        lbl_email.setObjectName("profileContactText")
        row_email.addWidget(lbl_email_icon)
        row_email.addSpacing(8)
        row_email.addWidget(lbl_email)
        contacts_layout.addLayout(row_email)

        left_layout.addWidget(contacts_card)
        left_layout.addStretch()

        # нижняя строка: выход
        logout_row = QHBoxLayout()
        logout_row.setContentsMargins(0, 0, 0, 0)
        logout_row.setSpacing(8)
        logout_icon = QLabel()
        logout_icon.setPixmap(QPixmap("assets/img/icon_logout.png").scaled(16, 16, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logout_icon.setFixedSize(16, 16)
        logout_label = QLabel("Выход")
        logout_label.setObjectName("profileLogout")
        logout_row.addWidget(logout_icon)
        logout_row.addWidget(logout_label)
        logout_row.addStretch()
        left_layout.addLayout(logout_row)

        root_layout.addWidget(left, 3)

        # ============== ПРАВАЯ ЧАСТЬ (сайдбар профиля) ==============
        right = QFrame()
        right.setObjectName("profileSidebar")
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(24, 8, 24, 24)
        right_layout.setSpacing(8)

        menu_items = ["О себе", "Фото", "Календарь", "Инструкции", "Документы", "Зарплата", "Приватность"]
        self.profile_menu_buttons = []

        for i, text in enumerate(menu_items):
            btn = QPushButton(text)
            btn.setObjectName("profileMenuButton")
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setMinimumWidth(180)
            btn.setMaximumWidth(180)
            if i == 0:
                btn.setChecked(True)
            btn.clicked.connect(lambda checked, b=btn: self._set_profile_menu_active(b))
            right_layout.addWidget(btn)
            self.profile_menu_buttons.append(btn)

        right_layout.addStretch()

        # нижний right: красный круг с вопросом (help)
        help_btn = QToolButton()
        help_btn.setObjectName("profileHelpButton")
        help_btn.setText("?")
        help_btn.setCursor(Qt.PointingHandCursor)
        help_btn.setFixedSize(40, 40)
        right_layout.addWidget(help_btn, 0, Qt.AlignRight | Qt.AlignBottom)

        root_layout.addWidget(right, 1)

        return page
    
    def _set_profile_menu_active(self, active_btn: QPushButton):
        for btn in self.profile_menu_buttons:
            btn.setChecked(btn is active_btn)

    def open_link(self, url: str):
        QDesktopServices.openUrl(QUrl(url))

