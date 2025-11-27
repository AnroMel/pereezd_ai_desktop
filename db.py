# db.py
import os
from datetime import datetime, timezone

import psycopg2
from psycopg2.extras import Json, DictCursor

DB_CONFIG = {
    "host": "aws-1-eu-west-1.pooler.supabase.com",
    "port": 5432,
    "dbname": "postgres",
    "user": "postgres.nkkyxflxcrqueydzoqvs",
    "password": "9C086908r.,",
    "sslmode": "require",
}


def get_conn():
    return psycopg2.connect(**DB_CONFIG)


# ===== ВСПОМОГАТЕЛЬНЫЕ МАППЕРЫ =====

def map_event_type_to_trigger_type_id(event_type: str) -> int:
    """
    Соответствие event.type -> trigger_types.id
    Таблица trigger_types сейчас такая:
      1 vehicle_on_crossing
      2 train_on_crossing
      3 gate_violation
      4 stopped_on_tracks

    Ты можешь потом подправить эту маппу под свои коды.
    """
    mapping = {
        "car_dwell_on_tracks": 4,            # остановка на путях
        "obstacle_on_tracks": 4,             # тоже по сути "stopped_on_tracks"
        "person_on_tracks_with_train": 2,    # поезд + люди
        "train_with_barrier_up": 3,          # поезд + открытый шлагбаум
        "barrier_stuck_down_without_train": 3,
        # всё неизвестное — просто "vehicle_on_crossing"
    }
    return mapping.get(event_type, 1)


def map_event_type_to_priority(event_type: str) -> int:
    """
    1 – низкий, 2 – средний, 3 – высокий, 4 – критический.
    """
    critical = {"person_on_tracks_with_train", "train_with_barrier_up"}
    high = {"car_dwell_on_tracks", "obstacle_on_tracks"}
    medium = {"barrier_stuck_down_without_train"}

    if event_type in critical:
        return 4
    if event_type in high:
        return 3
    if event_type in medium:
        return 2
    return 1


def build_trigger_title(ev: dict) -> str:
    """Короткий заголовок для operator UI."""
    event_type = ev.get("type", "event")
    cls = ev.get("object_class") or ev.get("cls")

    titles = {
        "car_dwell_on_tracks": "Автомобиль на путях",
        "obstacle_on_tracks": "Препятствие на путях",
        "person_on_tracks_with_train": "Люди на путях при приближении поезда",
        "train_with_barrier_up": "Поезд при поднятых шлагбаумах",
        "barrier_stuck_down_without_train": "Шлагбаум опущен без поезда",
    }

    base = titles.get(event_type)
    if base:
        return base
    return f"Событие от нейросети ({cls or event_type})"


def build_ai_analysis(ev: dict) -> str:
    """Текстовый разбор (можно тупо использовать description из события)."""
    desc = ev.get("description")
    if desc:
        return desc

    event_type = ev.get("type", "event")
    cls = ev.get("object_class") or ev.get("cls")
    dwell = ev.get("dwell_time_sec") or ev.get("dwell_time")

    parts = [f"Тип события: {event_type}"]
    if cls:
        parts.append(f"Класс объекта: {cls}")
    if dwell:
        parts.append(f"Время в зоне: {dwell:.1f} сек.")
    return " | ".join(parts)


def build_ai_recommendation(ev: dict) -> str:
    """Простые рекомендации по типу события."""
    event_type = ev.get("type", "event")

    if event_type in {"car_dwell_on_tracks", "obstacle_on_tracks"}:
        return "Немедленно связаться с машинистом/водителем и сообщить об препятствии на путях."
    if event_type == "person_on_tracks_with_train":
        return (
            "Немедленно оповестить людей о приближении поезда и запросить экстренное торможение поезда."
        )
    if event_type == "train_with_barrier_up":
        return "Сообщить дежурному, проверить исправность шлагбаумов и закрыть переезд."
    if event_type == "barrier_stuck_down_without_train":
        return "Сообщить дежурному о возможной неисправности шлагбаума, направить техников."

    return "Проверить ситуацию на переезде и при необходимости связаться с машинистом/водителями."


def resolve_camera_and_crossing_ids(camera_code: str) -> tuple[int, int]:
    """
    Заглушка. Сейчас просто возвращаем (1,1).
    Потом можно сделать SELECT из таблиц cameras / crossings по camera_code.
    """
    return 1, 1


def resolve_ai_model_id() -> int:
    """Пока модель одна — просто 1."""
    return 1


# ===== ЗАПИСЬ RAW-СОБЫТИЙ НЕЙРОСЕТИ =====

def insert_ai_raw_event(ev: dict) -> int:
    """
    Вставляет запись в ai_raw_events и возвращает её id.
    """
    conn = get_conn()
    try:
        with conn, conn.cursor() as cur:
            camera_id, crossing_id = resolve_camera_and_crossing_ids(ev.get("camera_id", "camera_1"))

            detected_at = ev.get("timestamp")
            if isinstance(detected_at, str):
                # в БД timestamptz → лучше конвертировать в UTC
                detected_at = datetime.fromisoformat(detected_at.replace("Z", "+00:00"))
            elif detected_at is None:
                detected_at = datetime.now(timezone.utc)

            confidence = ev.get("dwell_time_sec") or ev.get("confidence") or 0.0

            cur.execute(
                """
                INSERT INTO ai_raw_events (
                    ai_model_id,
                    camera_id,
                    crossing_id,
                    trigger_type_id,
                    detected_at,
                    confidence,
                    frame_image_path,
                    video_clip_path,
                    raw_metadata
                )
                VALUES (
                    %(ai_model_id)s,
                    %(camera_id)s,
                    %(crossing_id)s,
                    %(trigger_type_id)s,
                    %(detected_at)s,
                    %(confidence)s,
                    %(frame_image_path)s,
                    %(video_clip_path)s,
                    %(raw_metadata)s
                )
                RETURNING id;
                """,
                {
                    "ai_model_id": resolve_ai_model_id(),
                    "camera_id": camera_id,
                    "crossing_id": crossing_id,
                    "trigger_type_id": map_event_type_to_trigger_type_id(ev.get("type", "")),
                    "detected_at": detected_at,
                    "confidence": float(confidence),
                    "frame_image_path": None,
                    "video_clip_path": None,
                    "raw_metadata": Json(ev),
                },
            )
            new_id = cur.fetchone()[0]
            return new_id
    finally:
        conn.close()


# ===== ЗАПИСЬ В trigger_events =====

def insert_trigger_event_from_nn(ev: dict) -> None:
    """
    Создаёт запись в ai_raw_events (raw) и на её основе вставляет строку в trigger_events.
    """
    conn = get_conn()
    try:
        with conn, conn.cursor() as cur:
            # 1) сначала сохраняем raw-событие и получаем его id
            raw_event_id = insert_ai_raw_event(ev)

            camera_id, crossing_id = resolve_camera_and_crossing_ids(ev.get("camera_id", "camera_1"))
            trigger_type_id = map_event_type_to_trigger_type_id(ev.get("type", ""))

            priority = map_event_type_to_priority(ev.get("type", ""))
            status = "new"  # исходный статус

            title = build_trigger_title(ev)
            ai_analysis = build_ai_analysis(ev)
            ai_recommendation = build_ai_recommendation(ev)

            cur.execute(
                """
                INSERT INTO trigger_events (
                    raw_event_id,
                    crossing_id,
                    camera_id,
                    trigger_type_id,
                    priority,
                    status,
                    title,
                    ai_analysis,
                    ai_recommendation,
                    video_clip_path
                )
                VALUES (
                    %(raw_event_id)s,
                    %(crossing_id)s,
                    %(camera_id)s,
                    %(trigger_type_id)s,
                    %(priority)s,
                    %(status)s,
                    %(title)s,
                    %(ai_analysis)s,
                    %(ai_recommendation)s,
                    %(video_clip_path)s
                );
                """,
                {
                    "raw_event_id": raw_event_id,
                    "crossing_id": crossing_id,
                    "camera_id": camera_id,
                    "trigger_type_id": trigger_type_id,
                    "priority": priority,
                    "status": status,
                    "title": title,
                    "ai_analysis": ai_analysis,
                    "ai_recommendation": ai_recommendation,
                    "video_clip_path": None,
                },
            )
    finally:
        conn.close()


# ===== ЧТЕНИЕ ТРИГГЕРОВ ДЛЯ UI =====

def fetch_latest_trigger_events(limit: int = 100):
    """
    Возвращает последние события из trigger_events + базовые поля для UI.
    """
    conn = get_conn()
    try:
        with conn, conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(
                """
                SELECT
                    te.id,
                    te.title,
                    te.priority,
                    te.status,
                    te.created_at,
                    te.camera_id,
                    te.crossing_id
                FROM trigger_events te
                ORDER BY te.created_at DESC
                LIMIT %s;
                """,
                (limit,),
            )
            rows = cur.fetchall()
            return [dict(r) for r in rows]
    finally:
        conn.close()
