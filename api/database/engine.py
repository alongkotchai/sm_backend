from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    AsyncSession,
    AsyncEngine,
    create_async_engine)

async_session: async_sessionmaker[AsyncSession] = None
engine: AsyncEngine = None


async def init_engine(dsn: str) -> tuple[AsyncEngine, AsyncSession]:
    """initial mysql async engine and async session factory

    Args:
        dsn (str): mysql data source name url

    Returns:
        tuple[AsyncEngine, AsyncSession]: async engine, async session factory
    """
    engine = create_async_engine(dsn, echo=False)
    return engine, async_sessionmaker(engine, expire_on_commit=False)


async def ping_db(async_session: async_sessionmaker[AsyncSession]) -> None:
    """Ping mysql with async session

    Args:
        async_session (AsyncSession): async session factory

    """
    async with async_session() as session:
        await session.execute(text('SELECT 1'))


async def dispose_engine(eng: AsyncEngine) -> None:
    """free async mysql engine

    Args:
        eng (AsyncEngine):
    """
    if eng:
        await eng.dispose()
