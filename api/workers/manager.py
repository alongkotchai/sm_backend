from queue import Queue
from uuid import UUID
from threading import (
    Thread,
    Event)
import asyncio
from core.config import setting
from database.engine import async_session
from workers.worker import work

__task_queue: Queue = Queue()
__worker_event: list[Event] = []
__worker_list: list[Thread] = []


def __wrapper(wid: int, q: Queue, e: Event, async_session):
    asyncio.run(work(wid, q, e, async_session))


def get_status() -> tuple[int, int]:
    return __task_queue.qsize(), len(__worker_list)


def add_task(tid: UUID, filenames: list[str], model_fname: str) -> bool:
    try:
        __task_queue.put((str(tid), filenames, model_fname))
        return True
    except:
        False


def init_worker():
    for i in range(setting.NUMBER_WORKER):
        event = Event()
        thread = Thread(
            target=__wrapper,
            args=(i, __task_queue, event, async_session))
        event.set()
        __worker_event.append(event)
        __worker_list.append(thread)
        thread.start()


def close_all():
    for worker in __worker_event:
        worker.clear()
    for thread in __worker_list:
        thread.join()
