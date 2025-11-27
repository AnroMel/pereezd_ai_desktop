-- Роли
INSERT INTO roles (code, name) VALUES
('admin', 'Администратор'),
('operator', 'Оператор'),
('supervisor', 'Старший смены')
ON CONFLICT (code) DO NOTHING;

-- Пользователь-админ
INSERT INTO users (login, password_hash, role_id, is_active)
VALUES ('admin', '123', 1, TRUE)
ON CONFLICT (login) DO NOTHING;

-- Типы триггеров
INSERT INTO trigger_types (code, name) VALUES
('car_cross', 'Пересечение линии'),
('car_stop', 'Остановка ТС'),
('crowd', 'Скопление людей')
ON CONFLICT (code) DO NOTHING;

-- Тестовый переезд, камера и событие
INSERT INTO crossings (id, name)
VALUES (1, 'Тестовый переезд')
ON CONFLICT (id) DO NOTHING;

INSERT INTO cameras (id, crossing_id, name)
VALUES (1, 1, 'Камера 1')
ON CONFLICT (id) DO NOTHING;

INSERT INTO trigger_events (
    raw_event_id, crossing_id, camera_id, trigger_type_id,
    priority, status, title, created_at
)
VALUES (
    NULL, 1, 1, 1,
    3, 'Новая', 'Тестовое событие', NOW()
);
