from sqlalchemy.orm import mapped_column,Mapped,relationship
from entitys.base import Base, BaseType
from datetime import datetime


class ThingPredictLog(Base):
    id:Mapped[BaseType.uuid_primary_key]
    __tablename__ = "ThingPredictLog"
    occur_time:Mapped[datetime]
    thing_data:Mapped[str]
    position:Mapped[BaseType.str_30]
    lane_id:Mapped[BaseType.str_30]
    create_time:Mapped[BaseType.update_time]

    def __init__(self, occur_time:str,thing_data:str,position:str,lane_id:str) -> None:
        self.occur_time = occur_time
        self.thing_data = thing_data
        self.position = position
        self.lane_id = lane_id

    def __repr__(self) -> str:
        return f"<ThingPredictLog(id={self.id},occur_time={self.occur_time}, thing_data={self.thing_data},position={self.position},lane_id={self.lane_id})>"