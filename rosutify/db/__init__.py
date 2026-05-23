from urllib.parse import quote_plus

import sqlite3
from sqlalchemy import event
from typing import Callable
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from .scheme import Base
from ..configuration import configuration

DB_URL = f"sqlite+aiosqlite:///{configuration["DB_PATH"]}"

engine = create_async_engine(DB_URL, connect_args={"check_same_thread" : False})

session_local = async_sessionmaker(
	bind=engine,
	class_=AsyncSession,
	expire_on_commit=False
)

@event.listens_for(engine.sync_engine, "connect")
def enforce_fk(conn, _):
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def get_session(handler: Callable):
    async def dec(*args, **kwargs):
        async with session_local() as session:
            kwargs["session"] = session

            try:
                return await handler(*args, **kwargs)
            except Exception as e:
                await session.rollback()
                raise e
            finally:
                await session.close()
        
    return dec

__all__ = ["init_db", "get_session"]