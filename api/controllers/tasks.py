from uuid import (
    uuid4,
    UUID)
import base64
from datetime import datetime
from fastapi import (
    APIRouter,
    HTTPException,
    status,
    Depends)
from sqlalchemy.exc import (
    IntegrityError,
    NoResultFound)
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    AsyncSession)
from sqlalchemy import (
    select,
    delete,
    update,
    func,
    desc)
from core.security import (
    AuthContext,
    Role)
from database.models import (
    Tasks,
    Input)
from workers.file_handler import (
    delete_input_from_list,
    delete_task_folder,
    write_input_from_list)
from schemas.base import (
    ConfirmRes,
    last_page,
    QueryBase,
    TaskStatus,
    TaskType)
from schemas.tasks import (
    TaskCreate,
    TaskDisplay,
    TaskList,
    TaskModify)
from depends import (
    get_auth,
    get_session)


router = APIRouter(prefix='/tasks')


@router.get("", response_model=TaskList)
async def get_tasks(
    q: QueryBase = Depends(),
    auth_context: AuthContext = Depends(get_auth),
    async_session: async_sessionmaker[
        AsyncSession] = Depends(get_session)):

    stmt = select(Tasks,
                  func.count(Tasks.uid).
                  over().
                  label('total'))
    if auth_context.role == Role.USER:
        stmt = stmt.where(Tasks.uid == str(auth_context.sub))

    async with async_session() as session:
        res = (await session.execute(
            stmt.order_by(desc(Tasks.create_at)
                          if q.desc
                          else Tasks.create_at).
            offset((q.page - 1) * q.size).
            limit(q.size)
        )).all()
        tids = [row.Tasks.tid for row in res]
        ires = (await session.execute(
            select(Input).where(Input.tid.in_(tids))
        )).all()

    count = res[0].total if res else 0

    tasks_dict: dict[UUID, int] = {}
    tasks: list[Tasks] = []
    for i, row in enumerate(res):
        setattr(row.Tasks, 'number_of_input', 0)
        setattr(row.Tasks, 'input_list', [])
        tasks.append(row.Tasks)
        tasks_dict[row.Tasks.tid] = i

    for row in ires:
        if row.Input.tid not in tasks_dict:
            continue
        idx = tasks_dict[row.Input.tid]
        tasks[idx].number_of_input += 1
        tasks[idx].input_list.append(
            {'index': row.Input.index,
             'source_ref': row.Input.source_ref})

    return TaskList(page_number=q.page,
                    page_size=q.size,
                    last_page=last_page(count, q.size),
                    count=count,
                    tasks=tasks)


@router.get("/{tid}", response_model=TaskDisplay)
async def get_one_tasks(
    tid: UUID,
    auth_context: AuthContext = Depends(get_auth),
    async_session: async_sessionmaker[
        AsyncSession] = Depends(get_session)):

    async with async_session() as session:
        res = await session.get(Tasks, tid)

        if not res \
            or (auth_context.role != Role.ADMIN
                and auth_context.sub != res.uid):
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail=f'Task :{tid} Not Found')

        ires = (await session.execute(
            select(Input).where(Input.tid == str(tid))
        )).scalars().all()

    setattr(res, 'number_of_input', len(ires))
    setattr(res, 'input_list', ires)

    return res


@router.post("", response_model=TaskDisplay)
async def post_tasks(
    task: TaskCreate,
    auth_context: AuthContext = Depends(get_auth),
    async_session: async_sessionmaker[
        AsyncSession] = Depends(get_session)):

    tid = uuid4()
    task_temp = Tasks(**task.model_dump(exclude='input_list'),
                      tid=tid,
                      uid=auth_context.sub,
                      create_at=datetime.now(),
                      status=TaskStatus.CREATE)

    input_list: list[Input] = []
    files_list: list[tuple[bytes, str]] = []

    for i, s in enumerate(task.input_list):
        try:
            data, fname = __prepare_image(s, i)
        except ValueError:
            continue
        files_list.append((data, fname))
        input_list.append(Input(tid=tid,
                                index=i,
                                source_ref=fname))

    async with async_session() as session:
        try:
            session.add(task_temp)
            await session.flush()
            session.add_all(input_list)
            await session.commit()
            await session.refresh(task_temp)
        except IntegrityError as e:
            print(e)
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail="connot create task, check if model's name is correct")

        ires = (await session.execute(
            select(Input).where(Input.tid == str(task_temp.tid))
        )).scalars().all()

    setattr(task_temp, 'number_of_input', len(ires))
    setattr(task_temp, 'input_list', ires)

    await write_input_from_list(tid, files_list)

    return task_temp


@router.delete("/{tid}", response_model=ConfirmRes)
async def delete_tasks(
    tid: UUID,
    auth_context: AuthContext = Depends(get_auth),
    async_session: async_sessionmaker[
        AsyncSession] = Depends(get_session)):

    async with async_session() as session:
        task = await session.get(Tasks, tid)

        if task.status in (TaskStatus.RUN, TaskStatus.WAIT):
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail=f'Task :{tid} is processing')

        if not task \
            or (auth_context.role != Role.ADMIN
                and auth_context.sub != task.uid):
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail=f'Task :{tid} Not Found')

        await session.execute(
            delete(Input).
            where(Input.tid == str(tid)))

        await session.execute(
            delete(Tasks).
            where(Tasks.tid == str(tid)))

        await session.commit()

    await delete_task_folder(tid)

    return ConfirmRes(success=True)


@router.put("/{tid}")
async def put_tasks(
    tid: UUID,
    task: TaskModify,
    auth_context: AuthContext = Depends(get_auth),
    async_session: async_sessionmaker[
        AsyncSession] = Depends(get_session)):

    update_dict = task.model_dump(
        exclude_none=True,
        exclude=['input_to_remove', 'input_to_add'])

    input_list: list[Input] = []
    files_list: list[tuple[bytes, str]] = []
    rm_list: list[str] = []

    async with async_session() as session:
        res = await session.get(Tasks, tid)

        if not res:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail=f'Task :{tid} not found')

        if res.status in (TaskStatus.RUN, TaskStatus.WAIT):
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail=f'Task :{tid} is processing')

        if not res \
            or (auth_context.role != Role.ADMIN
                and auth_context.sub != res.uid):
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail=f'Task :{tid} Not Found')

        try:
            m = (await session.execute(
                select(func.max(Input.index)).
                where(Input.tid == str(tid))
            )).scalar_one() + 1
        except NoResultFound:
            m = 0

        for i, s in enumerate(task.input_to_add):
            try:
                data, fname = __prepare_image(s, i+m)
            except ValueError:
                continue
            files_list.append((data, fname))
            input_list.append(Input(tid=tid,
                                    index=i+m,
                                    source_ref=fname))

        if update_dict:
            await session.execute(
                update(Tasks).
                where(Tasks.tid == str(tid)).
                values(update_dict)
            )

        if task.input_to_remove:
            rm_list = (await session.execute(
                select(Input.source_ref).
                where(Input.tid == str(tid),
                      Input.index.in_(task.input_to_remove))
            )).scalars().all()

            await session.execute(
                delete(Input).
                where(Input.tid == str(tid),
                      Input.index.in_(task.input_to_remove))
            )

        if input_list:
            session.add_all(input_list)

        await session.commit()

        await session.refresh(res)

        ires = (await session.execute(
            select(Input).where(Input.tid == str(tid))
        )).scalars().all()

    setattr(res, 'number_of_input', len(ires))
    setattr(res, 'input_list', ires)

    if rm_list:
        await delete_input_from_list(tid, [name for name in rm_list])
    if files_list:
        await write_input_from_list(tid, files_list)

    return res


@router.post("/{tid}/start", response_model=ConfirmRes)
async def start_task(tid: UUID):
    return {
        "success": True
    }


@router.post("/{tid}/stop", response_model=ConfirmRes)
async def start_task(tid: UUID):
    return {
        "success": True
    }


def __prepare_image(data: str, idx: int) -> tuple[bytes, str]:
    data_list = data.split(',')

    if len(data_list) != 2:
        raise ValueError()

    head, data = data_list

    if head == 'data:image/png;base64':
        ftype = '.png'
    elif head == 'data:image/jpg;base64':
        ftype = '.jpg'
    elif head == 'data:image/jpeg;base64':
        ftype = '.jpg'
    else:
        raise ValueError()

    try:
        b_data = base64.b64decode(data)
    except:
        raise ValueError()

    return b_data, f'{idx}_{uuid4().hex[:7]}_{ftype}'
