# run_desktop.py
"""
Единая точка входа:
- в фоне слушает events_log.jsonl и пишет события в БД
- запускает твой PyQt5 интерфейс из ui_desktop/main.py
"""

import sys
import threading
from pathlib import Path

# --- пути проекта ---
BASE_DIR = Path(__file__).resolve().parent
UI_DIR = BASE_DIR / "ui_desktop"

# чтобы import main, ui.*, widgets.* работали как раньше
sys.path.insert(0, str(UI_DIR))

# импортируем то, что уже есть в "папке с БД"
from event_stream import follow_events
from db import insert_trigger_event_from_nn

# импортируем функцию main() из PyQt5-приложения на рабочем столе
from main import main as ui_main  # это main() из ui_desktop/main.py


def start_nn_ingestor_in_background():
    """
    Фоновый поток: слушает events_log.jsonl и пишет в trigger_events.
    Точно такая же логика, как в nn_event_ingestor.py,
    только запускается внутри этого процесса.
    """
    def worker():
        print("NN ingestor: слушаю events_log.jsonl ...")
        try:
            for ev in follow_events():
                try:
                    insert_trigger_event_from_nn(ev)
                    print(
                        "NN ingestor: событие записано в БД:",
                        ev.get("type"), ev.get("event_id")
                    )
                except Exception as e:
                    print("NN ingestor: ошибка при записи в БД:", e)
        except Exception as e:
            print("NN ingestor: фатальная ошибка:", e)

    t = threading.Thread(target=worker, daemon=True)
    t.start()


def main():
    # 1) стартуем фоновое чтение событий нейросети -> БД
    start_nn_ingestor_in_background()

    # 2) запускаем уже готовый PyQt5 интерфейс (логин + главное окно)
    ui_main()


if __name__ == "__main__":
    main()
