from sqlalchemy import ForeignKey
from entitys.base import Base, BaseType
from sqlalchemy.orm import mapped_column,Mapped,relationship


class Item(Base):
    __tablename__ = "Item"
    id:Mapped[BaseType.int_primary_key]
    name:Mapped[BaseType.str_50]
    price:Mapped[float]
    brand:Mapped[BaseType.str_30]
    description:Mapped[BaseType.optional_str_100]
    create_time:Mapped[BaseType.update_time]
    last_login:Mapped[BaseType.update_time]

    user_id:Mapped[int] = mapped_column(ForeignKey("User.id", ondelete="cascade"))
    user:Mapped["User"] = relationship("User", back_populates="items")

    def __init__(self, name:str, price:float, brand:str, description:str, user_id:int) -> None:
        self.name = name
        self.price = price
        self.brand = brand
        self.description = description
        self.user_id = user_id

    def __repr__(self) -> str:
        return f"<Item(id={self.id}, name={self.name}, price={self.price}, brand={self.brand})>"