import datetime
from typing import Annotated, Optional

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import mapped_column,DeclarativeBase


class Base(DeclarativeBase):
    pass

class BaseType:
    int_primary_key = Annotated[int, mapped_column(Integer, primary_key=True, unique=True, autoincrement=True)]
    str_30 = Annotated[str, mapped_column(String(30))]
    str_50 = Annotated[str, mapped_column(String(50))]
    str_60 = Annotated[str, mapped_column(String(60))]
    optional_str_50 = Annotated[Optional[str], mapped_column(String(50), nullable=True)]
    optional_str_100 = Annotated[Optional[str], mapped_column(String(100), nullable=True)]
    update_time = Annotated[datetime.datetime, mapped_column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)]