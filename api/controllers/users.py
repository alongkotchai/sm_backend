from uuid import UUID, uuid4
from datetime import datetime
from fastapi import (
    APIRouter,
    HTTPException,
    status,
    Depends)
from sqlalchemy import (
    func,
    desc,
    select,
    update,
    delete)
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    AsyncSession)
from sqlalchemy.exc import IntegrityError
from core.security import (
    AuthContext,
    Role,
    hash_password)
from database.models import User
from database import crud
from schemas.base import (
    QueryBase,
    last_page)
from schemas.users import (
    UserDisplay,
    UserModify,
    UserList,
    UserCreate)
from depends import (
    get_auth,
    get_session)

router = APIRouter(prefix='/users')


@router.get('', response_model=UserList)
async def get_users(
    q: QueryBase = Depends(),
    auth_context: AuthContext = Depends(get_auth),
    async_session: async_sessionmaker[
        AsyncSession] = Depends(get_session)
):
    if auth_context.role != Role.ADMIN:
        return UserList(page_number=q.page,
                        page_size=q.size,
                        last_page=1,
                        count=0,
                        users=[])

    async with async_session() as session:
        users = (await session.execute(
            select(User,
                   func.count(User.uid).
                   over().
                   label('total')).
            order_by(desc(User.create_at)
                     if q.desc
                     else User.create_at).
            offset((q.page - 1) * q.size).
            limit(q.size)
        )).all()

    count = users[0].total if users else 0
    users = [user.User for user in users]

    return UserList(page_number=q.page,
                    page_size=q.size,
                    last_page=last_page(count, q.size),
                    count=count,
                    users=users)


@router.get('/{uid}', response_model=UserDisplay)
async def get_user(
    uid: UUID,
    auth_context: AuthContext = Depends(get_auth),
    async_session: async_sessionmaker[
        AsyncSession] = Depends(get_session)
):
    async with async_session() as session:
        user = await session.get(User, uid)

    if not user \
        or (auth_context.role != Role.ADMIN
            and auth_context.sub != uid):
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail=f'User :{uid} Not Found')

    return user


@router.post('', response_model=UserDisplay)
async def create_user(
    user: UserCreate,
    auth_context: AuthContext = Depends(get_auth),
    async_session: async_sessionmaker[
        AsyncSession] = Depends(get_session)
):
    if auth_context.role != Role.ADMIN:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail='UNAUTHORIZED')

    temp = User(**user.model_dump())
    temp.create_at = datetime.now()
    temp.password = hash_password(temp.password)
    temp.uid = uuid4()

    async with async_session() as session:
        session.add(temp)
        try:
            await session.commit()
            await session.refresh(temp)
        except IntegrityError:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail='email is already in used')

    return temp


@router.put('/{uid}', response_model=UserDisplay)
async def update_user(
    uid: UUID,
    user: UserModify,
    auth_context: AuthContext = Depends(get_auth),
    async_session: async_sessionmaker[
        AsyncSession] = Depends(get_session)
):

    if (auth_context.role != Role.ADMIN
            and auth_context.sub != uid):
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail='User Not Found (1)')

    async with async_session() as session:

        try:
            res = (await session.execute(
                update(User).
                where(User.uid == str(uid)).
                values(**user.model_dump(exclude_none=True))
            )).rowcount
            await session.commit()
            temp = await session.get(User, uid)
        except IntegrityError:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail='email is already in used')

    if not (temp and res):
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail='User Not Found (2)')

    return temp


@router.delete('/{uid}')
async def update_user(
    uid: UUID,
    auth_context: AuthContext = Depends(get_auth),
    async_session: async_sessionmaker[
        AsyncSession] = Depends(get_session)
):

    if auth_context.role != Role.ADMIN \
            or uid == auth_context.sub:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail='UNAUTHORIZED')

    async with async_session() as session:
        res = (await session.execute(
            delete(User).
            where(User.uid == str(uid))
        ))
        await session.commit()
    if not res.rowcount:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail=f'User :{uid} Not Found')
    return {'success': True}


async def __create_default_user(
        async_session: async_sessionmaker[AsyncSession]) -> None:
    if (await crud.read_entity(async_session,
                               UUID(int=0),
                               User)):
        return
    user = User(uid=UUID(int=0),
                email='admin@admin.com',
                password=hash_password("password"),
                role=Role.ADMIN,
                create_at=datetime.now(),
                is_active=True)
    await crud.create_entity(async_session, user)
