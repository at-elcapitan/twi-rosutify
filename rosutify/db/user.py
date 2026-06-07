from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .scheme import User, UserInCommunity, Community


async def get_user_by_id(
    session: AsyncSession,
    user_id: int
) -> User | None:
    res = await session.execute(
        select(User)
            .where(User.id == user_id)
            .options(selectinload(User.user_in_community).selectinload(UserInCommunity.community))
    )
    return res.scalars().first()


async def create_user(
    session: AsyncSession,
    user_id: int,
    dm_initialized: bool = False,
    promotion_allowed: bool = False,
    is_superuser: bool = False
) -> User:
    user = User(
        id=user_id,
        dm_initialized=dm_initialized,
        promotion_allowed=promotion_allowed,
        is_superuser=is_superuser
    )

    session.add(user)
    await session.commit()

    return user


async def get_users_in_community(
    session: AsyncSession,
    community_id: int
) -> list[User]:
    res = await session.execute(
        select(User)
        .join(UserInCommunity)
        .where(UserInCommunity.community_id == community_id)
    )

    return res.scalars().all()


async def get_users_in_community_dm(
    session: AsyncSession,
    community_id: int
) -> list[User]:
    res = await session.execute(
        select(User)
            .join(UserInCommunity, UserInCommunity.user_id == User.id)
            .where(UserInCommunity.community_id == community_id)
            .where(UserInCommunity.personal_notification.is_(True))
            .where(User.dm_initialized.is_(True))
    )

    return res.scalars().all()


async def get_user_communities(
    session: AsyncSession,
    user_id: int
) -> list[Community]:
    res = await session.execute(
        select(Community)
            .join(UserInCommunity)
            .where(UserInCommunity.user_id == user_id)
    )

    return res.scalars().all()


async def check_admin_inited(
    session: AsyncSession
) -> bool:
    res = await session.execute(
        select(exists().where(User.is_superuser.is_(True)))
    )

    return res.scalar()


async def is_user_in_database(
    session: AsyncSession,
    user_id: int
) -> bool:
    res = await session.execute(
        select(exists().where(User.id == user_id))
    )

    return res.scalar()