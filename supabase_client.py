# supabase_client.py
from supabase import create_client, Client
import os

# ==== 1. НАСТРОЙКИ SUPABASE ====
SUPABASE_URL = "https://nkkyxflxcrqueydzoqvs.supabase.co"   # <-- сюда Project URL
SUPABASE_KEY = "sb_publishable_JLczoWaN4FDxjrliIhIw2g_TLXnHoE1"             # <-- сюда anon public key

# Вариант 2 (лучше): взять из переменных окружения
# SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
# SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY", "")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("Не заданы SUPABASE_URL / SUPABASE_KEY")


_supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def fetch_latest_ai_events(limit: int = 100):
    """
    Забирает последние события из таблицы ai_raw_events в Supabase.

    Возвращает список словарей:
    [{ 'id': ..., 'detected_at': ..., 'confidence': ..., ... }, ...]
    """
    resp = (
        _supabase
        .table("ai_raw_events")
        .select(
            "id, detected_at, confidence, trigger_type_id, camera_id, crossing_id, raw_metadata"
        )
        .order("detected_at", desc=True)
        .limit(limit)
        .execute()
    )

    # resp.data — это уже список dict
    return resp.data


def fetch_latest_operator_triggers(limit: int = 100):
    """
    Пример: забрать данные из trigger_operator_reports (то, что видит оператор).
    Подстрой список колонок под свою схему.
    """
    resp = (
        _supabase
        .table("trigger_operator_reports")
        .select("*")  # можно указать конкретные поля
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    return resp.data