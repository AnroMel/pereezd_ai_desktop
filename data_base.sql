
CREATE TABLE roles (
    id          SERIAL PRIMARY KEY,
    code        TEXT NOT NULL UNIQUE,
    name        TEXT NOT NULL
);

CREATE TABLE users (
    id              SERIAL PRIMARY KEY,
    login           TEXT NOT NULL UNIQUE,
    password_hash   TEXT NOT NULL,
    password_salt   TEXT,
    role_id         INT NOT NULL REFERENCES roles(id),
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_login_at   TIMESTAMPTZ
);

CREATE TABLE user_profiles (
    user_id          INT PRIMARY KEY REFERENCES users(id),
    full_name        TEXT NOT NULL,
    position         TEXT,
    birth_date       DATE,
    experience_years INT,
    city             TEXT,
    phone            TEXT,
    email            TEXT,
    vk_link          TEXT,
    telegram_link    TEXT,
    whatsapp_link    TEXT
);

CREATE TABLE user_photos (
    id          SERIAL PRIMARY KEY,
    user_id     INT NOT NULL REFERENCES users(id),
    file_path   TEXT NOT NULL,
    is_profile  BOOLEAN NOT NULL DEFAULT FALSE,
    uploaded_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE user_privacy_settings (
    user_id             INT PRIMARY KEY REFERENCES users(id),
    show_phone          BOOLEAN NOT NULL DEFAULT TRUE,
    show_email          BOOLEAN NOT NULL DEFAULT TRUE,
    show_social_links   BOOLEAN NOT NULL DEFAULT TRUE,
    show_birth_date     BOOLEAN NOT NULL DEFAULT FALSE,
    other_settings      JSONB
);

-- Журнал авторизаций
CREATE TABLE auth_logs (
    id          SERIAL PRIMARY KEY,
    user_id     INT REFERENCES users(id),
    login_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    success     BOOLEAN NOT NULL,
    ip_address  TEXT,
    user_agent  TEXT
);

-- История зарплаты
CREATE TABLE user_salary_history (
    id              SERIAL PRIMARY KEY,
    user_id         INT NOT NULL REFERENCES users(id),
    effective_from  DATE NOT NULL,
    base_salary     NUMERIC(12,2) NOT NULL,
    bonus           NUMERIC(12,2),
    comment         TEXT
);

-- =========================
-- ОБЪЕКТЫ ИНФРАСТРУКТУРЫ
-- =========================

CREATE TABLE crossings (
    id          SERIAL PRIMARY KEY,
    name        TEXT NOT NULL,
    address     TEXT,
    latitude    NUMERIC(9,6),
    longitude   NUMERIC(9,6),
    owner_org   TEXT,
    is_active   BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE cameras (
    id          SERIAL PRIMARY KEY,
    crossing_id INT NOT NULL REFERENCES crossings(id),
    name        TEXT NOT NULL,
    stream_url  TEXT,
    is_active   BOOLEAN NOT NULL DEFAULT TRUE
);

-- Оборудование (шлагбаумы, датчики и т.п.)
CREATE TABLE devices (
    id          SERIAL PRIMARY KEY,
    crossing_id INT NOT NULL REFERENCES crossings(id),
    device_type TEXT NOT NULL,
    name        TEXT NOT NULL,
    is_active   BOOLEAN NOT NULL DEFAULT TRUE
);

-- =========================
-- СПРАВОЧНИКИ ТРИГГЕРОВ, ПРИЧИН, ТС
-- =========================

CREATE TABLE trigger_types (
    id          SERIAL PRIMARY KEY,
    code        TEXT NOT NULL UNIQUE,
    name        TEXT NOT NULL,
    description TEXT
);

CREATE TABLE incident_cause_types (
    id      SERIAL PRIMARY KEY,
    code    TEXT NOT NULL UNIQUE,
    name    TEXT NOT NULL
);

CREATE TABLE vehicle_types (
    id      SERIAL PRIMARY KEY,
    code    TEXT NOT NULL UNIQUE,
    name    TEXT NOT NULL
);

-- =========================
-- МОДЕЛИ ИИ И ЛОГИ ДЕТЕКЦИЙ
-- =========================

CREATE TABLE ai_models (
    id          SERIAL PRIMARY KEY,
    name        TEXT NOT NULL,
    version     TEXT NOT NULL,
    deployed_at TIMESTAMPTZ
);

CREATE TABLE ai_raw_events (
    id               BIGSERIAL PRIMARY KEY,
    ai_model_id      INT NOT NULL REFERENCES ai_models(id),
    camera_id        INT NOT NULL REFERENCES cameras(id),
    crossing_id      INT NOT NULL REFERENCES crossings(id),
    trigger_type_id  INT NOT NULL REFERENCES trigger_types(id),
    detected_at      TIMESTAMPTZ NOT NULL,
    confidence       NUMERIC(5,2),
    frame_image_path TEXT,
    video_clip_path  TEXT,
    raw_metadata     JSONB
);

CREATE TABLE trigger_events (
    id                   BIGSERIAL PRIMARY KEY,
    raw_event_id         BIGINT REFERENCES ai_raw_events(id),
    crossing_id          INT NOT NULL REFERENCES crossings(id),
    camera_id            INT NOT NULL REFERENCES cameras(id),
    trigger_type_id      INT NOT NULL REFERENCES trigger_types(id),
    priority             SMALLINT NOT NULL,
    status               TEXT NOT NULL,
    title                TEXT NOT NULL,
    ai_analysis          TEXT,
    ai_recommendation    TEXT,
    video_clip_path      TEXT,
    created_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
    assigned_operator_id INT REFERENCES users(id),
    assigned_at          TIMESTAMPTZ,
    resolved_at          TIMESTAMPTZ
);

CREATE TABLE trigger_operator_reports (
    id                          BIGSERIAL PRIMARY KEY,
    trigger_event_id            BIGINT NOT NULL UNIQUE REFERENCES trigger_events(id),
    operator_id                 INT NOT NULL REFERENCES users(id),
    created_at                  TIMESTAMPTZ NOT NULL DEFAULT now(),
    operator_report             TEXT NOT NULL,
    ai_detection_score          SMALLINT,
    ai_detection_comment        TEXT,
    ai_recommendation_score     SMALLINT,
    ai_recommendation_comment   TEXT
);

-- =========================
-- ИНЦИДЕНТЫ / ДТП
-- =========================

CREATE TABLE incidents (
    id                      BIGSERIAL PRIMARY KEY,
    trigger_event_id        BIGINT REFERENCES trigger_events(id),
    crossing_id             INT NOT NULL REFERENCES crossings(id),
    incident_cause_type_id  INT NOT NULL REFERENCES incident_cause_types(id),
    vehicle_type_id         INT NOT NULL REFERENCES vehicle_types(id),
    occurred_at             TIMESTAMPTZ NOT NULL,
    location_description    TEXT,
    description             TEXT,
    severity                SMALLINT
);

-- =========================
-- НАПОМИНАНИЯ, НОВОСТИ, ДОКУМЕНТЫ
-- =========================

CREATE TABLE reminders (
    id               SERIAL PRIMARY KEY,
    user_id          INT NOT NULL REFERENCES users(id),
    trigger_event_id BIGINT REFERENCES trigger_events(id),
    title            TEXT NOT NULL,
    description      TEXT,
    due_at           TIMESTAMPTZ,
    is_completed     BOOLEAN NOT NULL DEFAULT FALSE,
    completed_at     TIMESTAMPTZ,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE news (
    id          SERIAL PRIMARY KEY,
    title       TEXT NOT NULL,
    body        TEXT NOT NULL,
    image_path  TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by  INT REFERENCES users(id),
    extra_data  JSONB
);

-- Инструкции, документы, зарплатные документы и т.д.
CREATE TABLE documents (
    id          SERIAL PRIMARY KEY,
    title       TEXT NOT NULL,
    category    TEXT NOT NULL,        -- instruction, policy, salary_info, other...
    file_path   TEXT NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by  INT REFERENCES users(id),
    is_active   BOOLEAN NOT NULL DEFAULT TRUE
);

-- Доступ к документам на уровне пользователя (опционально)
CREATE TABLE document_user_access (
    document_id INT NOT NULL REFERENCES documents(id),
    user_id     INT NOT NULL REFERENCES users(id),
    PRIMARY KEY (document_id, user_id)
);

-- =========================
-- КАЛЕНДАРЬ РАБОТЫ
-- =========================

CREATE TABLE work_status_types (
    id      SERIAL PRIMARY KEY,
    code    TEXT NOT NULL UNIQUE,  -- work, vacation, sick_leave, day_off ...
    name    TEXT NOT NULL
);

CREATE TABLE work_calendar_entries (
    id                  SERIAL PRIMARY KEY,
    user_id             INT NOT NULL REFERENCES users(id),
    date                DATE NOT NULL,
    status_type_id      INT NOT NULL REFERENCES work_status_types(id),
    work_start_time     TIME,
    work_end_time       TIME,
    break_start_time    TIME,
    break_end_time      TIME,
    comment             TEXT,
    UNIQUE (user_id, date)
);

-- =========================
-- NOTE / COMMENT ДЛЯ ДИАГРАММЫ
-- =========================

COMMENT ON TABLE roles IS
    'Справочник ролей пользователей (админ, оператор и т.п.).';

COMMENT ON TABLE users IS
    'Учетные записи пользователей для авторизации (логин/пароль, роль, активность).';

COMMENT ON TABLE user_profiles IS
    'Профиль пользователя: ФИО, должность, контакты и соцсети.';

COMMENT ON TABLE user_photos IS
    'Фотографии пользователей, с пометкой основной (фото профиля).';

COMMENT ON TABLE user_privacy_settings IS
    'Настройки приватности профиля (что показывать другим).';

COMMENT ON TABLE auth_logs IS
    'Журнал попыток авторизации пользователей (успешных и неуспешных).';

COMMENT ON TABLE user_salary_history IS
    'История изменений зарплаты и бонусов по пользователям.';

COMMENT ON TABLE crossings IS
    'Железнодорожные переезды (место, координаты, владелец).';

COMMENT ON TABLE cameras IS
    'Камеры видеонаблюдения, привязанные к переездам, с URL трансляции.';

COMMENT ON TABLE devices IS
    'Оборудование на переездах (шлагбаумы, датчики, громкоговорители и др.).';

COMMENT ON TABLE trigger_types IS
    'Типы триггерных ситуаций, детектируемых нейросетью (ТС между шлагбаумами и т.д.).';

COMMENT ON TABLE incident_cause_types IS
    'Справочник причин ДТП/инцидентов (выезд на закрытый шлагбаум, остановка на пути и др.).';

COMMENT ON TABLE vehicle_types IS
    'Типы транспортных средств (легковой, грузовой, автобус, поезд и т.п.).';

COMMENT ON TABLE ai_models IS
    'Версии моделей ИИ (нейросети), используемых для детекции.';

COMMENT ON TABLE ai_raw_events IS
    'Сырые события от ИИ: детекции по кадрам/видео (с метаданными).';

COMMENT ON TABLE trigger_events IS
    'Агрегированные триггерные события для оператора (карточки инцидентов в ленте).';

COMMENT ON TABLE trigger_operator_reports IS
    'Отчёты операторов по триггерным событиям, оценки качества детекции и рекомендаций ИИ.';

COMMENT ON TABLE incidents IS
    'Зарегистрированные ДТП/инциденты на переездах, для статистики и карты.';

COMMENT ON TABLE reminders IS
    'Напоминания для операторов: например, о необходимости заполнить отчёт.';

COMMENT ON TABLE news IS
    'Новости в системе: заголовок, текст, фото, дополнительные данные.';

COMMENT ON TABLE documents IS
    'Инструкции и прочие документы (в т.ч. по зарплате), доступные в системе.';

COMMENT ON TABLE document_user_access IS
    'Связь документов и пользователей для управления индивидуальным доступом.';

COMMENT ON TABLE work_status_types IS
    'Справочник типов статусов на день (работа, отпуск, больничный, отгул и пр.).';

COMMENT ON TABLE work_calendar_entries IS
    'Календарь работы пользователей: статусы по дням, время работы и перерыва.';
