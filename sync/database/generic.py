from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from entitys.item import Item
from entitys.users import User
from setting.config import get_settings


settings = get_settings()


engine = create_engine(
    settings.database_url ,
    echo=True,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

@contextmanager
def get_db_session():
    db_session = next(get_db())
    try:
        yield db_session
    finally:
        db_session.close()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine, tables=[User.__table__, Item.__table__])

def db_session_decorator(func):
    # print("in db_context_decorator")
    def wrapper(*args, **kwargs):
        with get_db_session() as db_session:
            kwargs["db_session"] = db_session
            result = func(*args, **kwargs)
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