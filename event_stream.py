import json
import time
from pathlib import Path
from typing import Iterator, Dict, Any

LOG_PATH = Path(r"C:\Users\vlad-\Documents\pereezd.ai\events_log.jsonl")


def follow_events(poll_interval: float = 0.2) -> Iterator[Dict[str, Any]]:
    """
    Читает новые строки из events_log.jsonl и отдаёт их как dict.
    """
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    LOG_PATH.touch(exist_ok=True)

    with LOG_PATH.open("r", encoding="utf-8") as f:
        # сразу перемещаемся в конец файла — слушаем только новые события
        f.seek(0, 2)

        while True:
            line = f.readline()
            if not line:
                time.sleep(poll_interval)
                continue

            line = line.strip()
            if not line:
                continue

            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                print("⚠ Некорректная строка в events_log.jsonl:", line)
                continue

            yield event
