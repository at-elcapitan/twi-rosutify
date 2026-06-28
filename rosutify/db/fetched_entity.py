from sqlalchemy import exists, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .scheme import FetchedEntity


async def create_fetched_entity(
    session: AsyncSession,
    text: str,
    community_id: int,
    notify_entity_id: int,
    twi_id: int
) -> FetchedEntity:
    fetched_entity = FetchedEntity(
        text=text,
        community_id=community_id,
        notify_entity_id=notify_entity_id,
        twi_id=twi_id
    )

    session.add(fetched_entity)
    await session.commit()
    await session.refresh(fetched_entity)

    return fetched_entity


async def set_fetched_entity_picked(
    session: AsyncSession,
    fetched_entity_id: int,
    picked_by_user_id: int
) -> None:
    await session.execute(
        update(FetchedEntity)
        .where(FetchedEntity.id == fetched_entity_id)
        .values(
            picked_by_user_id=picked_by_user_id,
            picked=True
        )
    )
    await session.commit()


async def is_fetched_entity_picked(
    session: AsyncSession,
    fetched_entity_id: int
) -> bool:
    res = await session.execute(
        select(exists().where(
            FetchedEntity.id == fetched_entity_id,
            FetchedEntity.picked.is_(True)
        ))
    )

    return res.scalar()


async def get_fetched_entities_ids_unique(
    session: AsyncSession,
    notify_entity_id: int,
    limit: int = 20
) -> list[int]:
    res = await session.execute(
        select(FetchedEntity.twi_id)
        .where(
            FetchedEntity.notify_entity_id == notify_entity_id
        )
        .group_by(FetchedEntity.twi_id)
        .order_by(func.max(FetchedEntity.id).desc())
        .limit(limit)
    )

    return res.scalars().all()