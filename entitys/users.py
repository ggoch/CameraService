from datetime import date
import hashlib
from typing import Optional
from sqlalchemy import Date
from sqlalchemy.orm import mapped_column,Mapped,relationship

from auth.passwd import get_password_hash
from entitys.base import Base, BaseType

class User(Base):
    __tablename__ = "User"
    id:Mapped[BaseType.int_primary_key]
    password:Mapped[BaseType.str_60]
    name:Mapped[BaseType.str_30]
    age:Mapped[int]
    avatar:Mapped[BaseType.optional_str_100]
    birthday:Mapped[date] = mapped_column(Date)
    email:Mapped[BaseType.str_50]
    create_time:Mapped[BaseType.update_time]

    items:Mapped[list["Item"]] \
        = relationship("Item", 
            back_populates="user", 
            cascade="all, delete-orphan", 
            lazy="select", 
            order_by="Item.name"
        )
    
    def __init__(self, password:str, name:str, age:int, avatar:Optional[str], birthday:date, email:str) -> None:
        # password should be hashed before store in database , here is just for demo
        # self.password = hashlib.md5(password.encode()+b'secret').hexdigest()
        self.password = password
        self.name = name
        self.age = age
        self.avatar = avatar
        self.birthday = birthday
        self.email = email

    def __repr__(self) -> str:
        return f"<User(id={self.id}, name={self.name}, age={self.age}, email={self.email})>"