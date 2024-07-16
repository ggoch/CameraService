from sqlalchemy import select, update, delete
from sqlalchemy.orm import Session 

from sync.database.generic import manager_class_decorator
from entitys.car_no_predict_log import CarNoPredictLog

import sys

@manager_class_decorator
class CarNoPredictLogManager:
    def get_list(
        self,
        keyword: str = None,
        max_occur_time: str = None,
        min_occur_time: str = None,
        skip_count: int = 0,
        max_count: int = sys.maxsize,
        db_session: Session = None,
    ):
        stmt = select(CarNoPredictLog).order_by(CarNoPredictLog.create_time.desc())
        if keyword:
            stmt = stmt.where(CarNoPredictLog.car_no.like(f"%{keyword}%"))

        if max_occur_time:
            stmt = stmt.where(CarNoPredictLog.occur_time <= max_occur_time)

        if min_occur_time:
            stmt = stmt.where(CarNoPredictLog.occur_time >= min_occur_time)

        stmt = stmt.offset(skip_count).limit(max_count)
        result = db_session.execute(stmt)
        car_no_predict_logs = result.scalars().all()

        return car_no_predict_logs
    
    def get_by_id(self, id: str,db_session: Session,):
        stmt = select(CarNoPredictLog).where(CarNoPredictLog.id == id)
        result = db_session.execute(stmt)
        car_no_predict_log = result.scalars().first()

        return car_no_predict_log
    
    def create(
        self,
        occur_time: str,
        car_no: str,
        position: str,
        lane_name: str,
        camera_name: str,
        no: str,
        db_session: Session,
    ):
        car_no_predict_log = CarNoPredictLog(
            occur_time=occur_time,
            car_no=car_no,
            position=position,
            lane_name=lane_name if lane_name is not None else "",
            camera_name=camera_name,
            no=no
        )
        db_session.add(car_no_predict_log)
        db_session.commit()
        db_session.refresh(car_no_predict_log)

        return car_no_predict_log
    
    def delete(self, id: str,db_session: Session,):
        stmt = delete(CarNoPredictLog).where(CarNoPredictLog.id == id)
        db_session.execute(stmt)
        db_session.commit()

        return None