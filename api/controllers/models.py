import aiofiles
from os import path
from fastapi import (
    APIRouter,
    HTTPException,
    status,
    Depends)
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    AsyncSession)
from sqlalchemy import (
    select,
    func,
    desc)
from core.security import (
    AuthContext)
from database.models import Model
from schemas.base import (
    QueryBase,
    last_page)
from schemas.models import (
    ModelDisplay,
    ModelList,
    ModelUpload)
from depends import (
    get_auth,
    get_session)

router = APIRouter(prefix='/models')


@router.get("", response_model=ModelList)
async def get_models(
    q: QueryBase = Depends(),
    _: AuthContext = Depends(get_auth),
    async_session: async_sessionmaker[
        AsyncSession] = Depends(get_session)):

    async with async_session() as session:
        models = (await session.execute(
            select(Model, func.count(Model.name).over().label('total')).
            order_by(desc(Model.name) if q.desc else Model.name).
            offset((q.page - 1) * q.size).
            limit(q.size)
        )).all()
    count = models[0].total if models else 0
    models = [model.Model for model in models]
    return ModelList(page_number=q.page,
                     page_size=q.size,
                     last_page=last_page(count, q.size),
                     count=count,
                     models=models)


async def create_default(
    base_dir: str,
    async_session:
        async_sessionmaker[AsyncSession]
) -> None:
    path1 = path.join(base_dir, 'data1.pk')
    path2 = path.join(base_dir, 'data2.pk')
    path3 = path.join(base_dir, 'data3.pk')

    if not (path.exists(path1) and path.exists(path2) and path.exists(path2)):
        raise ValueError('invalid path for default model data')

    async with aiofiles.open(path1, mode='rb') as f:
        data1 = await f.read()
    async with aiofiles.open(path2, mode='rb') as f:
        data2 = await f.read()
    async with aiofiles.open(path3, mode='rb') as f:
        data3 = await f.read()

    async with async_session() as session:
        if await session.get(Model, 'default'):
            return

        session.add(
            Model(name='default',
                  data1=data1,
                  data2=data2,
                  data3=data3))

        await session.commit()
