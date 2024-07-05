from contextlib import asynccontextmanager
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker,DeclarativeBase

from sqlalchemy.schema import CreateTable
from setting.config import get_settings

import entitys


settings = get_settings()


engine = create_async_engine(settings.database_url, echo=True, pool_pre_ping=True)

SessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)


@asynccontextmanager
async def get_db():
    async with SessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()


async def init_db():
    async with SessionLocal() as db:
        async with db.begin():
            await db.execute(CreateTable(entitys.User.__table__,if_not_exists=True))
            await db.execute(CreateTable(entitys.Item.__table__,if_not_exists=True))
            await db.execute(CreateTable(entitys.ThingPredictLog.__table__,if_not_exists=True))
            await db.execute(CreateTable(entitys.CarNoPredictLog.__table__,if_not_exists=True))



async def close_db():
    await engine.dispose()


def db_session_decorator(func):
    # print("in db_context_decorator")
    async def wrapper(*args, **kwargs):
        async with get_db() as db_session:
            kwargs["db_session"] = db_session
            result = await func(*args, **kwargs)
            return result
    # print("out db_context_decorator")
    return wrapper

def manager_class_decorator(cls):
    # print("in db_class_decorator")
    for name, method in cls.__dict__.items():
        if callable(method):
            setattr(cls, name, db_session_decorator(method))
    # print("out db_class_decorator")
    return cls