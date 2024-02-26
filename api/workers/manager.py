from queue import Queue
from uuid import UUID
from threading import (
    Thread,
    Event)
import asyncio
from core.config import setting
from database import engine
from workers.worker import work

__task_queue: Queue = Queue()
__worker_event: list[Event] = []
__worker_list: list[Thread] = []
__session_list: list = []


def __wrapper(wid: int, q: Queue, e: Event, async_session):
    asyncio.run(work(wid, q, e, async_session))


def get_status() -> tuple[int, int]:
    return __task_queue.qsize(), len(__worker_list)


def add_task(tid: UUID,
             indx_fnames: list[tuple[int, str]],
             model_fname: str
             ) -> bool:
    try:
        __task_queue.put(
            (str(tid),
             indx_fnames,
             model_fname
             ))
        return True
    except:
        False


async def init_worker(dsn):

    for i in range(setting.NUMBER_WORKER):
        async_eng, async_session = await engine.init_engine(dsn)
        __session_list.append(async_eng)

        event = Event()
        thread = Thread(
            target=__wrapper,
            args=(i, __task_queue, event, async_session))
        event.set()
        __worker_event.append(event)
        __worker_list.append(thread)
        thread.start()


async def close_all():
    for worker in __worker_event:
        worker.clear()
    for thread in __worker_list:
        thread.join()
    for index, eng in enumerate(__session_list):
        if not eng:
            continue
        await eng.dispose()
        print(f'Worker {index} engine terminated')
