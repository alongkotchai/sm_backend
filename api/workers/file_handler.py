import aiofiles
import shutil
import asyncio
import os
from uuid import uuid4, UUID


INPUT_PATH: str
OUTPUT_PATH: str
MODEL_PATH: str


async def __write_file(base_path: str,
                       tid: UUID,
                       data: bytes,
                       filename: str) -> None:

    path = os.path.join(base_path, str(tid))
    if not os.path.exists(path):
        os.mkdir(path)
    path = os.path.join(path, filename)

    async with aiofiles.open(path, mode='wb') as f:
        await f.write(data)


async def write_output(tid: UUID, data: bytes, filename: str) -> None:

    await __write_file(OUTPUT_PATH, tid, data, filename)


async def write_input(tid: UUID, data: bytes, filename: str) -> None:

    await __write_file(INPUT_PATH, tid, data, filename)


async def write_input_from_list(tid: UUID,
                                data: list[tuple[bytes, str]]
                                ) -> None:
    n = [__write_file(INPUT_PATH, tid, bdata, filename)
         for bdata, filename in data]

    await asyncio.gather(*n)


async def __read_file(base_path: str,
                      tid: UUID,
                      filename: str) -> bytes:

    path = os.path.join(base_path, str(tid), filename)

    if not os.path.exists(path):
        raise ValueError('file not existed')

    async with aiofiles.open(path, mode='rb') as f:
        return await f.read()


async def read_input(tid: UUID, filename: str) -> bytes:

    return await __read_file(INPUT_PATH, tid, filename)


def __delete_file(base_path: str, tid: UUID, filename: str):
    path = os.path.join(base_path, str(tid), filename)
    if not os.path.exists(path):
        return
    os.remove(path)


async def delete_input(tid: UUID, filename: str) -> bytes:

    return await __delete_file(INPUT_PATH, tid, filename)


async def delete_output(tid: UUID, filename: str) -> bytes:

    return await __delete_file(OUTPUT_PATH, tid, filename)


async def delete_input_from_list(tid: UUID, filenames: list[str]) -> None:

    for filename in filenames:
        __delete_file(INPUT_PATH, tid, filename)


async def delete_task_folder(tid: UUID) -> None:

    path1 = os.path.join(INPUT_PATH, str(tid))
    path2 = os.path.join(OUTPUT_PATH, str(tid))
    if os.path.exists(path1):
        shutil.rmtree(path1)
    if os.path.exists(path2):
        shutil.rmtree(path2)
