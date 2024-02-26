from uuid import UUID
from fastapi import (
    APIRouter,
    HTTPException,
    status,
    Depends)
from sqlalchemy import (
    func,
    desc,
    select)
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    AsyncSession)
from core.security import (
    AuthContext,
    Role)
from database.models import (
    Output,
    Input,
    Tasks)
from schemas.base import (
    TaskStatus,
    QueryBase,
    last_page)
from schemas.results import (
    ResultDetail,
    ResultList)
from depends import (
    get_auth,
    get_session)

router = APIRouter(prefix='/results')


@router.get("/summary", response_model=ResultList)
async def get_summary(
    q: QueryBase = Depends(),
    auth_context: AuthContext = Depends(get_auth),
    async_session: async_sessionmaker[
        AsyncSession] = Depends(get_session)):

    stmt_task = (select(Tasks.tid,
                        func.count(Tasks.tid).
                        over().
                        label('total'))
                 .where(Tasks.status != TaskStatus.CREATE))

    if auth_context.role == Role.USER:
        stmt_task = stmt_task.where(
            Tasks.uid == str(auth_context.sub))

    async with async_session() as session:
        tasks = (await session.execute(
            stmt_task.
            order_by(desc(Tasks.create_at)
                     if q.desc
                     else Tasks.create_at).
            offset((q.page - 1) * q.size).
            limit(q.size)
        )).all()

        count = tasks[0].total if tasks else 0
        tids = [task._data[0] for task in tasks]

        outputs = (await session.execute(
            select(Output).
            where(Output.tid.in_(tids))
        )).scalars().all()

    _tasks_dict = {}
    result_list = []

    for i, task in enumerate(tids):
        result_list.append({'tid': task, 'outputs': []})
        _tasks_dict[task] = i

    for output in outputs:
        if output.tid not in _tasks_dict:
            continue
        result_list[_tasks_dict[output.tid]]['outputs'].append(
            {
                'p1': {
                    'center_x': output.p1_x,
                    'center_y': output.p1_y,
                    'width': output.p1_w,
                    'height': output.p1_h,
                    'predict': output.p1_predict
                },
                'p2': {
                    'center_x': output.p2_x,
                    'center_y': output.p2_y,
                    'width': output.p2_w,
                    'height': output.p2_h,
                    'predict': output.p2_predict
                },
                'input_file': output.source_ref,
                'output_file': output.source_ref
            }
        )

    return ResultList(page_number=q.page,
                      page_size=q.size,
                      last_page=last_page(count, q.size),
                      count=count,
                      results=result_list)


@router.get("/{tid}", response_model=ResultDetail)
async def get_detail(
    tid: UUID,
    auth_context: AuthContext = Depends(get_auth),
    async_session: async_sessionmaker[
        AsyncSession] = Depends(get_session)):

    async with async_session() as session:
        task = (await session.execute(
            select(Tasks).
            where(Tasks.tid == str(tid),
                  Tasks.uid == str(auth_context.sub))
        )).scalar_one_or_none()

        if not task:
            raise HTTPException(status.HTTP_404_NOT_FOUND,
                                f'Not Found task {str(tid)}')

        if task.status == TaskStatus.CREATE:
            raise HTTPException(status.HTTP_400_BAD_REQUEST,
                                f'tasks has not been start')

        outputs = (await session.execute(
            select(Output).
            where(Output.tid == str(tid))
        )).scalars().all()

        in_count = (await session.execute(
            select(func.count(Input.tid)).
            where(Input.tid == str(tid))
        )).scalars().one_or_none() or 0

    results = []

    for output in outputs:
        results.append(
            {
                'p1': {
                    'center_x': output.p1_x,
                    'center_y': output.p1_y,
                    'width': output.p1_w,
                    'height': output.p1_h,
                    'predict': output.p1_predict
                },
                'p2': {
                    'center_x': output.p2_x,
                    'center_y': output.p2_y,
                    'width': output.p2_w,
                    'height': output.p2_h,
                    'predict': output.p2_predict
                },
                'input_file': output.source_ref,
                'output_file': output.source_ref
            }
        )
        setattr(task, 'outputs', results)
        setattr(task, 'number_of_input', in_count)
        setattr(task, 'processed', len(results))

    return task
