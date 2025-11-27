# nn_event_ingestor.py
from event_stream import follow_events
from db import insert_trigger_event_from_nn


def worker():
    print("NN ingestor: слушаю events_log.jsonl ...")
    for ev in follow_events():
        try:
            insert_trigger_event_from_nn(ev)
            print("NN ingestor: записал событие в trigger_events и ai_raw_events:", ev.get("type"), ev.get("event_id"))
        except Exception as e:
            print("NN ingestor: ошибка при записи в БД:", e)


if __name__ == "__main__":
    worker()
