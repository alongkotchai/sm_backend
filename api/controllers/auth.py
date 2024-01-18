from datetime import datetime
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
    update)
from core.security import (
    compare_hash,
    create_access_token,
    AuthContext)
from database.models import User
from database import crud
from schemas.users import (
    UserDisplay,
    UserContext,
    UserLogin)
from depends import (
    get_auth,
    get_session)

router = APIRouter(prefix='/auth')


@router.post('/login', response_model=UserContext)
async def login(
    user: UserLogin,
    async_session: async_sessionmaker[
        AsyncSession] = Depends(get_session)
):
    async with async_session() as session:
        res = (await session.execute(
            select(User).where(User.email == user.email)
        )).first()

        if not res or not compare_hash(user.password,
                                       res._data[0].password):
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED)
        temp = user = res._data[0]
        print('aaaaa')
        await session.execute(
            update(User).where(
                User.id == temp.id).values(
                    {'last_login': datetime.now()}))
        await session.commit()

    auth = AuthContext(sub=temp.id,
                       role=temp.role)
    return UserContext(user=user,
                       access_token=create_access_token(auth))


@router.get('/me', response_model=UserDisplay)
async def get_users(
    auth_context: AuthContext = Depends(get_auth),
    async_session: async_sessionmaker[
        AsyncSession] = Depends(get_session)
):

    return await crud.read_entity(async_session, auth_context.sub, User)
