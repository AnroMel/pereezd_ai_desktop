# test_list_ai_events.py
from db import fetch_latest_ai_raw_events

def main():
    events = fetch_latest_ai_raw_events(limit=10)
    print(f"Нашли {len(events)} событий:")
    for ev in events:
        print(
            ev["id"],
            "|", ev["detected_at"],
            "| camera_id:", ev["camera_id"],
            "| crossing_id:", ev["crossing_id"],
            "| trigger_type_id:", ev["trigger_type_id"],
            "| conf:", ev["confidence"],
        )

if __name__ == "__main__":
    main()
