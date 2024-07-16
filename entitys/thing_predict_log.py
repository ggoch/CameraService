from sqlalchemy.orm import mapped_column,Mapped,relationship
from entitys.base import Base, BaseType
from datetime import datetime


class ThingPredictLog(Base):
    __tablename__ = "ThingPredictLog"
    id:Mapped[BaseType.uuid_primary_key]
    occur_time:Mapped[datetime]
    thing_data:Mapped[str]
    position:Mapped[BaseType.str_30]
    lane_name:Mapped[BaseType.str_60]
    camera_name:Mapped[BaseType.str_60]
    no:Mapped[BaseType.str_60]
    create_time:Mapped[BaseType.update_time]

    def __init__(self, occur_time:str,thing_data:str,position:str,lane_name:str,camera_name:str,no:str) -> None:
        self.occur_time = occur_time
        self.thing_data = thing_data
        self.position = position
        self.lane_name = lane_name
        self.camera_name = camera_name
        self.no = no

    def __repr__(self) -> str:
        return f"<ThingPredictLog(id={self.id},occur_time={self.occur_time}, thing_data={self.thing_data},position={self.position},lane_name={self.lane_name},camera_name={self.camera_name},no={self.no})>"