from uuid import UUID
from typing import TypeVar, Type, Optional
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    AsyncSession)
from sqlalchemy import (
    update,
    select,
    delete)
from database.models import User, Base
Entity = TypeVar('Entity', User, Base)


async def create_entity(async_session: async_sessionmaker[AsyncSession],
                        entity: Entity
                        ) -> Entity:
    async with async_session() as session:
        session.add(entity)
        await session.commit()
        await session.refresh(entity)
        return entity


async def update_entity(async_session: async_sessionmaker[AsyncSession],
                        id: UUID,
                        data_update: dict,
                        entity_type: Type[Entity]
                        ) -> Optional[Entity]:
    async with async_session() as session:
        await session.execute(
            update(entity_type).where(
                entity_type.id == str(id)).values(data_update))
        await session.commit()
        return await session.get(entity_type, id)


async def read_entity(async_session: async_sessionmaker[AsyncSession],
                      id: UUID,
                      entity_type: Type[Entity]
                      ) -> Optional[Entity]:
    async with async_session() as session:
        return await session.get(entity_type, id)


async def read_list_entity(async_session: async_sessionmaker[AsyncSession],
                           entity_type: Type[Entity]
                           ) -> list[Entity]:
    async with async_session() as session:
        results = await session.execute(select(entity_type))
        return [result._data[0] for result in results]


async def delete_entity(async_session: async_sessionmaker[AsyncSession],
                        id: UUID,
                        entity_type: Type[Entity]
                        ) -> bool:
    async with async_session() as session:
        if not await session.get(entity_type, id):
            return False
        await session.execute(
            delete(entity_type).where(entity_type.id == str(id)))
        await session.commit()
        return await session.get(entity_type, id) == None
