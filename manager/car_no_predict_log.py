from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from database.generic import manager_class_decorator
from entitys.car_no_predict_log import CarNoPredictLog

@manager_class_decorator
class CarNoPredictLogManager:
    async def get_list(
        self,
        keyword: str = None,
        max_occur_time: str = None,
        min_occur_time: str = None,
        skip_count: int = 0,
        max_count: int = 50,
        db_session: AsyncSession = None,
    ):
        stmt = select(CarNoPredictLog).order_by(CarNoPredictLog.create_time.desc())
        if keyword:
            stmt = stmt.where(CarNoPredictLog.car_no.like(f"%{keyword}%"))

        if max_occur_time:
            stmt = stmt.where(CarNoPredictLog.occur_time <= max_occur_time)

        if min_occur_time:
            stmt = stmt.where(CarNoPredictLog.occur_time >= min_occur_time)

        stmt = stmt.offset(skip_count).limit(max_count)
        result = await db_session.execute(stmt)
        car_no_predict_logs = result.all()

        return car_no_predict_logs
    
    async def get_by_id(self, id: str,db_session: AsyncSession,):
        stmt = select(CarNoPredictLog).where(CarNoPredictLog.id == id)
        result = await db_session.execute(stmt)
        car_no_predict_log = result.first()

        return car_no_predict_log
    
    async def create(
        self,
        occur_time: str,
        car_no: str,
        position: str,
        lane_id: str,
        db_session: AsyncSession,
    ):
        car_no_predict_log = CarNoPredictLog(
            occur_time=occur_time,
            car_no=car_no,
            position=position,
            lane_id=lane_id,
        )
        db_session.add(car_no_predict_log)
        await db_session.commit()
        await db_session.refresh(car_no_predict_log)

        return car_no_predict_log
    
    async def delete(self, id: str,db_session: AsyncSession,):
        stmt = delete(CarNoPredictLog).where(CarNoPredictLog.id == id)
        await db_session.execute(stmt)
        await db_session.commit()

        return None