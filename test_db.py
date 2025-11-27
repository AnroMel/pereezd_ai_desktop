from db import fetch_latest_trigger_events
import traceback


def main():
    print("Пробую запрос к БД...")
    try:
        events = fetch_latest_trigger_events(limit=5)
        print("Успех! Событий получено:", len(events))
        for ev in events:
            print(ev["id"], ev["title"], ev["status"], ev["created_at"])
    except Exception as e:
        print("=== ОШИБКА ===")
        print("Тип:", type(e))
        print("Сообщение:", e)
        print("Полный traceback:")
        traceback.print_exc()


if __name__ == "__main__":
    main()