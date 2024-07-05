from sqlalchemy.orm import mapped_column,Mapped,relationship
from entitys.base import Base, BaseType
from datetime import datetime

class CarNoPredictLog(Base):
    __tablename__ = "CarNoPredictLog"
    id:Mapped[BaseType.uuid_primary_key]
    occur_time:Mapped[datetime]
    car_no:Mapped[str]
    position:Mapped[BaseType.str_30]
    lane_id:Mapped[BaseType.str_30]
    create_time:Mapped[BaseType.update_time]

    def __init__(self, occur_time:str,car_no:str,position:str,lane_id:str) -> None:
        self.occur_time = occur_time
        self.car_no = car_no
        self.position = position
        self.lane_id = lane_id

    def __repr__(self) -> str:
        return f"<CarNoPredictLog(id={self.id},occur_time={self.occur_time}, car_no={self.car_no},position={self.position},lane_id={self.lane_id})>"