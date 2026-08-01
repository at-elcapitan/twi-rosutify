from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .scheme import NotifyEntity, UserInCommunity, Community, TelegramNotifyEntity, TelegramNotifyMessage


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


async def get_telegram_notify_entities(
    session: AsyncSession
) -> list[TelegramNotifyEntity]:
    res = await session.execute(
        select(TelegramNotifyEntity)
    )

    return res.scalars().all()


async def create_tg_message(
    session: AsyncSession,
    tg_message_id: int,
    text: str,
    community_id: int,
    tg_notify_entity_id: int
) -> TelegramNotifyMessage:
    tg_message = TelegramNotifyMessage(
        tg_message_id=tg_message_id,
        text=text,
        community_id=community_id,
        tg_notify_entity_id=tg_notify_entity_id
    )

    session.add(tg_message)
    await session.commit()
    await session.refresh(tg_message)

    return tg_message


async def set_tg_message_picked(
    session: AsyncSession,
    tg_message_id: int,
    picked_by_user_id: int
) -> None:
    res = await session.execute(
        select(TelegramNotifyMessage)
            .where(TelegramNotifyMessage.tg_message_id == tg_message_id)
    )

    tg_message = res.scalars().first()

    if tg_message is None:
        return

    tg_message.picked = True
    tg_message.picked_by_user_id = picked_by_user_id

    session.add(tg_message)
    await session.commit()