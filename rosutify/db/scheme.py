from __future__ import annotations

from sqlalchemy import (
	Column, String, Table, Text, Enum as SqlEnum, ForeignKey, Boolean, Integer
)
from sqlalchemy.orm import (
	Mapped, mapped_column, relationship, DeclarativeBase
)

from . import enums


class Base(DeclarativeBase):
	pass


communities_in_notify_entity = Table(
    "communities_in_notify_entity",
    Base.metadata,
    Column("community_id", ForeignKey("community.id"), primary_key=True),
    Column("notify_entity_id", ForeignKey("notify_entity.id"), primary_key=True)
)


class Community(Base):
	__tablename__ = "community"

	id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
	name: Mapped[str] = mapped_column(Text, unique=False, nullable=False)
	connected_channel: Mapped[int] = mapped_column(Integer, nullable=False)
	personal_only: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

	notify_entity: Mapped[list[NotifyEntity]] = relationship(
		back_populates="community",
		secondary=communities_in_notify_entity
	)
	user_in_community: Mapped[list[UserInCommunity]] = relationship(
		back_populates="community",
		cascade="all, delete-orphan"
	)
	fetched_entity: Mapped[list[FetchedEntity]] = relationship(
		back_populates="community"
	)


class NotifyEntity(Base):
	__tablename__ = "notify_entity"

	id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
	twi_id: Mapped[int] = mapped_column(nullable=False)
	twi_username: Mapped[str] = mapped_column(String(16), nullable=False)
	twi_name: Mapped[str] = mapped_column(String(51), nullable=False)

	community: Mapped[list[Community]] = relationship(
        back_populates="notify_entity",
        secondary=communities_in_notify_entity
    )
	fetched_entity: Mapped[list[FetchedEntity]] = relationship(
		back_populates="notify_entity"
	)


class UserInCommunity(Base):
	__tablename__ = "user_in_community"

	id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
	role: Mapped[enums.Role] = mapped_column(SqlEnum(enums.Role), nullable=False, default=enums.Role.fetcher)
	personal_notification: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

	community_id: Mapped[int] = mapped_column(ForeignKey("community.id"), nullable=False)
	user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)

	community: Mapped[Community] = relationship(
		back_populates="user_in_community"
	)
	user: Mapped[User] = relationship(
		back_populates="user_in_community"
	)

class User(Base):
	__tablename__ = "user"

	id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
	dm_initialized: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
	promotion_allowed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
	is_superuser: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

	user_in_community: Mapped[list[UserInCommunity]] = relationship(
		back_populates="user",
		cascade="all, delete-orphan"
	)
	fetched_entity: Mapped[list[FetchedEntity]] = relationship(
		back_populates="user"
	)


class FetchedEntity(Base):
	__tablename__ = "fetched_entity"

	id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
	twi_id: Mapped[int] = mapped_column(nullable=False)
	text: Mapped[str] = mapped_column(Text, nullable=False)
	picked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

	community_id: Mapped[int] = mapped_column(ForeignKey("community.id"), nullable=False)
	picked_by_user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=True, default=None)
	notify_entity_id: Mapped[int] = mapped_column(ForeignKey("notify_entity.id"), nullable=False)

	community: Mapped[Community] = relationship(
		back_populates="fetched_entity"
	)
	user: Mapped[User] = relationship(
		back_populates="fetched_entity"
	)
	notify_entity: Mapped[NotifyEntity] = relationship(
		back_populates="fetched_entity"
	)
