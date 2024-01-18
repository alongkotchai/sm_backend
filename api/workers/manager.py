from queue import Queue
from threading import (
    Thread,
    Lock,
    Event)

__task_queue: Queue = Queue()
__worker_list: list[Event] = []
__worker_list_lock: Lock = Lock()
