from datetime import datetime
from queue import Queue
from uuid import UUID
from threading import (
    Thread,
    Event,
    Lock)
import asyncio
from core.config import setting
from database import engine
from workers.worker import work
from workers.rt_worker import predict
from workers.repo_worker import repo_work

__task_queue: Queue = Queue()
__repo_queue: Queue = Queue()
__worker_event: list[Event] = []
__worker_list: list[Thread] = []
__session_list: list = []
__rt_task_dict: dict[str, dict] = dict()
__rt_set_lock: Lock = Lock()


def __wrapper(wid: int, q: Queue, e: Event, async_session):
    asyncio.run(work(wid, q, e, async_session))


def __wrapper_repo(q: Queue, e: Event, async_session):
    asyncio.run(repo_work(q, e, async_session))


def get_status() -> tuple[int, int]:
    return __task_queue.qsize(), len(__worker_list)


def get_rt_status():
    return [{'tid': k,
             'start_time': v.get('start_time')}
            for k, v in __rt_task_dict.items()]


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


def add_rt(tid: UUID, e: Event):
    with __rt_set_lock:
        __rt_task_dict[str(tid)] = {
            'start_time': datetime.now(),
            'run_flag': e
        }


def remove_rt(tid: UUID):
    with __rt_set_lock:
        if str(tid) in __rt_task_dict:
            __rt_task_dict.pop(str(tid))


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

    # repo worker
    async_eng, async_session = await engine.init_engine(dsn)
    __session_list.append(async_eng)
    event = Event()
    thread = Thread(
        target=__wrapper_repo,
        args=(__repo_queue, event, async_session))
    event.set()
    __worker_event.append(event)
    __worker_list.append(thread)
    thread.start()


async def close_all():
    __repo_queue.put('q')

    for worker in __worker_event:
        worker.clear()
    for thread in __worker_list:
        thread.join()
    for index, eng in enumerate(__session_list):
        if not eng:
            continue
        await eng.dispose()
        print(f'Worker {index} engine terminated')

    for k, v in __rt_task_dict.items():
        e: Event = v.get('run_flag')
        if not e:
            continue
        e.clear()


async def run_rt_task(tid: UUID, qin: Queue, qout: Queue, e: Event):
    e.set()
    thread = Thread(
        target=predict,
        args=(qin, qout, __repo_queue, e, remove_rt, tid))
    thread.start()
    print(f'task-rt:{str(tid)} start')
    add_rt(tid, e)
