from sqlalchemy import exists, select, insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .scheme import UserInCommunity, Community, communities_in_notify_entity


async def create_community(
    session: AsyncSession,
    name: str,
    connected_channel: int,
    personal_only: bool = False
) -> Community:
    community = Community(
        name=name,
        connected_channel=connected_channel,
        personal_only=personal_only
    )

    session.add(community)

    await session.commit()
    await session.refresh(community)

    return community


async def get_community_by_id(
    session: AsyncSession,
    community_id: int
) -> Community | None:
    res = await session.execute(
        select(Community)
            .where(Community.id == community_id)
            .options(
                selectinload(Community.notify_entity),
                selectinload(Community.user_in_community).selectinload(UserInCommunity.user)
            )
    )
    return res.scalars().first()


async def get_community_by_channel_id(
    session: AsyncSession,
    channel_id: int
) -> Community | None:
    res = await session.execute(
        select(Community)
            .where(Community.connected_channel == channel_id)
            .options(
                selectinload(Community.notify_entity),
                selectinload(Community.user_in_community).selectinload(UserInCommunity.user)
            )
    )
    return res.scalars().first()


async def add_notify_entity(
    session: AsyncSession,
    community_id: int,
    notify_entity_id: int
) -> None:
    await session.execute(
        insert(communities_in_notify_entity).values(
            community_id=community_id,
            notify_entity_id=notify_entity_id
        )
    )

    await session.commit()


async def get_all_community_channel_ids(
    session: AsyncSession
) -> list[int]:
    res = await session.execute(
        select(Community.connected_channel)
    )

    return res.scalars().all()