from functools import wraps
import inspect

from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from .scheme import Base
from ..configuration import configuration
from . import user, community as community_db, notify_entity as notify_entity_db

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

def get_session(handler):
    sig = inspect.signature(handler)

    @wraps(handler)
    async def wrapper(*args, **kwargs):
        async with session_local() as session:
            bound_args = sig.bind_partial(*args, **kwargs)
            bound_args.arguments['session'] = session
            
            try:
                return await handler(*bound_args.args, **bound_args.kwargs)
            except Exception:
                await session.rollback()
                raise

    return wrapper

__all__ = ["init_db", "get_session", "user"]