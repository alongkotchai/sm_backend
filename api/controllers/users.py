from uuid import UUID, uuid4
from datetime import datetime
from fastapi import (
    APIRouter,
    HTTPException,
    status,
    Depends)
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
    auth_context: AuthContext = Depends(get_auth),
    async_session: async_sessionmaker[
        AsyncSession] = Depends(get_session)
):
    if auth_context.role != Role.ADMIN:
        return {'users': []}

    return {'users': await crud.read_list_entity(async_session, User)}


@router.get('/{id}', response_model=UserDisplay)
async def get_user(
    id: UUID,
    auth_context: AuthContext = Depends(get_auth),
    async_session: async_sessionmaker[
        AsyncSession] = Depends(get_session)
):
    user = await crud.read_entity(async_session, id, User)

    if not user or \
            (auth_context.role != Role.ADMIN
             and auth_context.sub != id):
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail='User Not Found')

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
    temp.id = uuid4()

    try:
        return await crud.create_entity(async_session, temp)
    except IntegrityError:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail='email is already in used')


@router.put('/{id}', response_model=UserDisplay)
async def update_user(
    id: UUID,
    user: UserModify,
    auth_context: AuthContext = Depends(get_auth),
    async_session: async_sessionmaker[
        AsyncSession] = Depends(get_session)
):
    res = await crud.read_entity(async_session, id, User)

    if not res or \
            (auth_context.role != Role.ADMIN
             and auth_context.sub != id):
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail='User Not Found')

    try:
        return await crud.update_entity(async_session,
                                        id,
                                        user.model_dump(exclude_none=True),
                                        User)
    except IntegrityError:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail='email is already in used')


@router.delete('/{id}')
async def update_user(
    id: UUID,
    auth_context: AuthContext = Depends(get_auth),
    async_session: async_sessionmaker[
        AsyncSession] = Depends(get_session)
):

    if auth_context.role != Role.ADMIN:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail='UNAUTHORIZED')

    res = await crud.delete_entity(async_session, id, User)
    if not res:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail='User Not Found')
    return {'success': True}


async def __create_default_user(
        async_session: async_sessionmaker[AsyncSession]) -> None:
    if (await crud.read_entity(async_session,
                               UUID(int=0),
                               User)):
        return
    user = User(id=UUID(int=0),
                email='admin@admin.com',
                password=hash_password("password"),
                role=Role.ADMIN,
                create_at=datetime.now(),
                is_activate=True)
    await crud.create_entity(async_session, user)
