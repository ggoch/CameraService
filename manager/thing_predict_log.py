from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from database.generic import manager_class_decorator
from entitys.thing_predict_log import ThingPredictLog

@manager_class_decorator
class ThingPredictLogManager:
    async def get_list(
        self,
        keyword: str = None,
        max_occur_time: str = None,
        min_occur_time: str = None,
        skip_count: int = 0,
        max_count: int = 50,
        db_session: AsyncSession = None,
    ):
        stmt = select(ThingPredictLog).order_by(ThingPredictLog.create_time.desc())
        if keyword:
            stmt = stmt.where(ThingPredictLog.thing_data.like(f"%{keyword}%"))

        if max_occur_time:
            stmt = stmt.where(ThingPredictLog.occur_time <= max_occur_time)

        if min_occur_time:
            stmt = stmt.where(ThingPredictLog.occur_time >= min_occur_time)

        stmt = stmt.offset(skip_count).limit(max_count)
        result = await db_session.execute(stmt)
        thing_predict_logs = result.all()

        return thing_predict_logs
    
    async def get_by_id(self, db_session: AsyncSession, id: str):
        stmt = select(ThingPredictLog).where(ThingPredictLog.id == id)
        result = await db_session.execute(stmt)
        thing_predict_log = result.first()

        return thing_predict_log
    
    async def create(
        self,
        occur_time: str,
        thing_data: str,
        position: str,
        lane_id: str,
        db_session: AsyncSession,
    ):
        thing_predict_log = ThingPredictLog(
            occur_time=occur_time,
            thing_data=thing_data,
            position=position,
            lane_id=lane_id,
        )
        db_session.add(thing_predict_log)
        await db_session.commit()
        await db_session.refresh(thing_predict_log)

        return thing_predict_log
    
    async def delete(self, id: str,db_session: AsyncSession,):
        stmt = delete(ThingPredictLog).where(ThingPredictLog.id == id)
        await db_session.execute(stmt)
        await db_session.commit()

        return None