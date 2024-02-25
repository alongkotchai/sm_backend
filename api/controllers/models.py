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


async def create_default_model(
    base_dir: str,
    filename: str,
    async_session:
        async_sessionmaker[AsyncSession]
) -> None:
    dir = path.join(base_dir, filename)
    if not (path.exists(dir)):
        raise ValueError('invalid path for default model data')

    async with async_session() as session:
        if await session.get(Model, 'default'):
            return

        session.add(
            Model(name='default',
                  version='1.0',
                  source_ref=filename))

        await session.commit()
