from queue import Queue
from threading import Event
from uuid import uuid4
from time import time, sleep
from datetime import datetime
from PIL import Image
import base64
from io import BytesIO
from fastapi import WebSocket
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    AsyncSession)
from core.security import decode_access_token
from schemas.tasks import (
    TaskCreate,
    TaskType)
from workers.manager import run_rt_task
from controllers.tasks import (
    create_rt_task,
    finish_rt_task)

RATE = 1/25

async_session: async_sessionmaker[AsyncSession] = None


def array_resize_to_base64(img_array) -> str:
    data = Image.fromarray(img_array)
    buffered = BytesIO()
    data.save(buffered, format="JPEG", optimize=True, quality=50)
    return 'data:image/jpg;base64,' + base64.b64encode(buffered.getvalue()).decode()


async def handle_rt(ws: WebSocket, access_token: str):
    try:
        auth = decode_access_token(access_token)
    except:
        await ws.close()
    await ws.accept()
    print('accept')
    tid = uuid4()

    while True:
        data_in = await ws.receive_text()
        if data_in == 'start':
            await create_rt_task(
                tid,
                TaskCreate(
                    name=tid.hex,
                    m_name='default',
                    task_type=TaskType.CAMERA,
                    input_list=[]),
                auth,
                async_session)
            await ws.send_json({'tid': str(tid)})
            break
        await ws.send_json({'message': 'send start to begin'})

    end_msg = 'q'

    try:
        buffer_in: Queue = Queue(maxsize=300)
        buffer_out: Queue = Queue(maxsize=300)
        flag: Event = Event()

        # thread manager start doing work
        await run_rt_task(tid, buffer_in, buffer_out, flag)

        last_time = time()
        while True:
            # receive input
            print('wait for input')
            data_in = await ws.receive_text()
            if data_in == 'q':
                break
            buffer_in.put(data_in, timeout=10)

            # wait for output
            print('wait for output')
            out = buffer_out.get(timeout=10)
            if out in ('f', 'q'):
                end_msg = out
                break

            if 'image' not in out or out['image'].size == 0:
                continue

            try:
                out['image'] = array_resize_to_base64(out['image'])
            except Exception as error:
                print(error, 'arr to b64')
                continue

            # send output
            print('send out')
            await ws.send_json(out)

            #  rate limit
            current_time = time()
            delta_time = current_time-last_time
            if abs(delta_time) < RATE:
                sleep(RATE - delta_time)
            last_time = current_time

        sleep(0.5)
        last_time = time()
        while not buffer_out.empty():
            print('tailing part')
            out = buffer_out.get(timeout=2)
            if out in ('f', 'q'):
                end_msg = out
                break

            if 'image' not in out or out['image'].size == 0:
                continue

            try:
                out['image'] = array_resize_to_base64(out['image'])
            except Exception as error:
                print(error, 'arr to b64')
                continue

            current_time = time()
            delta_time = current_time-last_time
            if abs(delta_time) < RATE:
                sleep(RATE - delta_time)
            last_time = current_time

        print('send end message')
        await ws.send_json({'end_message': end_msg})
        await ws.close()

    except Exception as error:
        print(error, 'rt error')
    finally:
        flag.clear()
        await finish_rt_task(tid, async_session)
