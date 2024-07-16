from contextlib import contextmanager
from sqlalchemy.orm import Session 
from sqlalchemy import select , update , delete
import hashlib


from entitys.thing_predict_log import ThingPredictLog
from sync.database.generic import manager_class_decorator

@manager_class_decorator
class ThingPredictLogManager:
    def get_list(
        self,
        keyword: str = None,
        max_occur_time: str = None,
        min_occur_time: str = None,
        skip_count: int = 0,
        max_count: int = 50,
        db_session: Session = None,
    ):
        stmt = select(ThingPredictLog).order_by(ThingPredictLog.create_time.desc())
        if keyword:
            stmt = stmt.where(ThingPredictLog.thing_data.like(f"%{keyword}%"))

        if max_occur_time:
            stmt = stmt.where(ThingPredictLog.occur_time <= max_occur_time)

        if min_occur_time:
            stmt = stmt.where(ThingPredictLog.occur_time >= min_occur_time)

        stmt = stmt.offset(skip_count).limit(max_count)
        result = db_session.execute(stmt)
        thing_predict_logs = result.all()

        return thing_predict_logs
    
    def get_by_id(self, db_session: Session, id: str):
        stmt = select(ThingPredictLog).where(ThingPredictLog.id == id)
        result = db_session.execute(stmt)
        thing_predict_log = result.first()

        return thing_predict_log
    
    def create(
        self,
        occur_time: str,
        thing_data: str,
        position: str,
        lane_name: str,
        camera_name: str,
        no: str,
        db_session: Session,
    ):
        thing_predict_log = ThingPredictLog(
            occur_time=occur_time,
            thing_data=thing_data,
            position=position,
            lane_name=lane_name if lane_name is not None else "",
            camera_name=camera_name,
            no=no
        )
        db_session.add(thing_predict_log)
        db_session.commit()
        db_session.refresh(thing_predict_log)

        return thing_predict_log
    
    def delete(self, id: str,db_session: Session,):
        stmt = delete(ThingPredictLog).where(ThingPredictLog.id == id)
        db_session.execute(stmt)
        db_session.commit()

        return None