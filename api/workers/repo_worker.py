from queue import Queue, Empty
from threading import Event
from io import BytesIO
from PIL import Image
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    AsyncSession)
from database.models import Output
from workers.file_handler import write_output


async def update_result(tid: str,
                        index:  int,
                        source: str,
                        pred: dict,
                        bbox: dict,
                        async_session: async_sessionmaker[AsyncSession]):
    data = {}

    for key in pred:
        if key < 0.5:
            data['p1_predict'] = pred[key]
        else:
            data['p2_predict'] = pred[key]

    # for key in bbox:

    #     box = bbox[key]
    #     if len(box) < 4:
    #         continue

    #     if key < 0.5:
    #         data['p1_x'] = box[0]
    #         data['p1_y'] = box[1]
    #         data['p1_w'] = box[2]
    #         data['p1_h'] = box[3]
    #     else:
    #         data['p2_x'] = box[0]
    #         data['p2_y'] = box[1]
    #         data['p2_w'] = box[2]
    #         data['p2_h'] = box[3]

    output = Output(tid=tid, index=index, source_ref=source, **data)

    async with async_session() as session:
        session.add(output)
        await session.commit()


async def save_output(tid, img, fname):
    data = Image.fromarray(img)
    print('byte io')
    buffered = BytesIO()
    data.save(buffered, format="JPEG", optimize=True, quality=70)
    await write_output(tid, buffered.read(), fname)


async def repo_work(
        qin: Queue,
        e: Event,
        async_session: async_sessionmaker[AsyncSession]):

    print(f'repo worker start')
    while True:
        try:
            data = qin.get(timeout=5)
            print('repo worker get data')
        except Empty:
            if not e.is_set():
                break
            continue

        if data == 'q':
            break

        tid = data.get('tid')
        name = data.get('name') + '.jpg'

        try:
            print(f'repo worker save file {tid}:{name}')
            await save_output(
                tid,
                data.get('image'),
                name,
            )
            print(f'repo worker save output {tid}:{name}')
            await update_result(
                tid,
                data.get('swine_number'),
                name,
                data.get('length'),
                {},
                async_session)
            print(f'repo woker done {tid}:{name}')
        except Exception as error:
            print('repo worker error', type(error), error)

    print(f'repo worker terminate')
