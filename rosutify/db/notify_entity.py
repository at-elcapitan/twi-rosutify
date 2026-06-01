from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .scheme import NotifyEntity, UserInCommunity, Community


async def get_communities_for_notify_entity(
    session: AsyncSession,
    notify_entity_id: int
) -> list[Community]:
    res = await session.execute(
        select(Community)
            .join(Community.notify_entity)
            .where(NotifyEntity.id == notify_entity_id)
    )

    return res.scalars().all()


async def create_notify_entity(
    session: AsyncSession,
    twi_id: int,
    twi_username: str,
    twi_name: str
) -> NotifyEntity:
    notify_entity = NotifyEntity(
        twi_id=twi_id,
        twi_username=twi_username,
        twi_name=twi_name
    )

    session.add(notify_entity)
    await session.commit()
    await session.refresh(notify_entity)

    return notify_entity


async def get_notify_entity_by_id(
    session: AsyncSession,
    notify_entity_id: int
) -> NotifyEntity | None:
    res = await session.execute(
        select(NotifyEntity)
            .where(NotifyEntity.id == notify_entity_id)
    )

    return res.scalars().first()


async def get_notify_entity_by_username(
    session: AsyncSession,
    twi_username: str
) -> NotifyEntity | None:
    res = await session.execute(
        select(NotifyEntity)
            .where(NotifyEntity.twi_username == twi_username)
    )

    return res.scalars().first()