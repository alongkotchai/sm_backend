import os
from datetime import datetime
from ultralytics import YOLO
import pickle
import aiofiles
from threading import Event
from queue import Queue, Empty
from sqlalchemy import update
from sqlalchemy.ext.asyncio import (
    async_sessionmaker as asess,
    AsyncSession)
from schemas.tasks import TaskStatus
from database.models import Output, Tasks

BASE_IN: str
BASE_OUT: str
BASE_MODEL: str


async def load_model(name: str) -> YOLO | None:
    m_path = os.path.join(BASE_MODEL, name)
    if not os.path.exists(m_path):
        return
    async with aiofiles.open(m_path, mode='rb') as model:
        return pickle.loads(await model.read())


async def get_bounding_box(model: YOLO,
                           image_path: str,
                           tid: str) -> dict:

    results = model(image_path,
                    save=True,
                    project=BASE_OUT,
                    name=tid,
                    exist_ok=True,
                    verbose=False)

    bounding_box = dict()
    for i in range(len(results[0].boxes.cls)):
        cls = results[0].boxes.cls[i].tolist()
        bbox = results[0].boxes.xywh[i].tolist()
        bounding_box[cls] = bbox

    return bounding_box


def predicted_fat_length(bbox: dict) -> dict:
    # ---------------- enter measure code here ----------------
    pred_length = dict()
    for key in bbox:
        width = bbox[key][2]
        pred_length[key] = (0.0626511240488297*width) + 1.0363981961391178
    return pred_length


async def update_result(tid: str,
                        index:  int,
                        source: str,
                        pred: dict,
                        bbox: dict,
                        async_session: asess[AsyncSession]):
    data = {}

    for key in pred:
        if key < 0.5:
            data['p1_predict'] = pred[key]
        else:
            data['p2_predict'] = pred[key]

    for key in bbox:

        box = pred[key]
        if len(box) < 4:
            continue

        if key < 0.5:
            data['p1_x'] = box[0]
            data['p1_y'] = box[1]
            data['p1_w'] = box[2]
            data['p1_h'] = box[3]
        else:
            data['p2_x'] = box[0]
            data['p2_y'] = box[1]
            data['p2_w'] = box[2]
            data['p2_h'] = box[3]

    output = Output(tid=tid, index=index, source_ref=source, **data)

    async with async_session() as session:
        session.add(output)
        await session.commit()


async def update_status(tid: str, status: TaskStatus, async_session: asess[AsyncSession]):
    data = {'status': status}
    if status == TaskStatus.RUN:
        data['start_time'] = datetime.now()
    elif status == TaskStatus.FINISH:
        data['finish_time'] = datetime.now()
    async with async_session() as session:
        await session.execute(
            update(Tasks).where(Tasks.tid == tid).values(data)
        )
        await session.commit()


async def work(wid: int, q: Queue, e: Event, async_session: asess[AsyncSession]):

    print(f'worker {wid} start')

    while e.is_set():

        try:
            tid, indx_fnames, model_name = q.get(timeout=5)
        except Empty:
            continue

        await update_status(tid, TaskStatus.RUN, async_session)

        model = await load_model(model_name)
        if not model:
            print(f'canot locate model file {model_name}')
            continue

        for index, filename in indx_fnames:
            path = os.path.join(BASE_IN, tid, filename)
            bbox = await get_bounding_box(model, path, tid)
            pred = predicted_fat_length(bbox)

            print(f'{filename=}', pred, bbox)
            await update_result(tid, index, filename, pred, bbox, async_session)

        await update_status(tid, TaskStatus.FINISH, async_session)
        print(f'task {tid} is done')
    print(f'worker {wid} terminated')
