from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from database.generic import manager_class_decorator
from entitys.thing_predict_log import ThingPredictLog

from schemas.thing_predict_log import ThingPredictLogCreateResponse, ThingPredictLogRead

import sys

@manager_class_decorator
class ThingPredictLogManager:

    async def get_list(
        self,
        keyword: str = None,
        max_occur_time: str = None,
        min_occur_time: str = None,
        skip_count: int = 0,
        max_count: int = sys.maxsize,
        db_session: AsyncSession = None,
    ) -> list[ThingPredictLogRead]:
        stmt = select(ThingPredictLog).order_by(ThingPredictLog.create_time.desc())
        if keyword:
            stmt = stmt.where(ThingPredictLog.thing_data.like(f"%{keyword}%"))

        if max_occur_time:
            stmt = stmt.where(ThingPredictLog.occur_time <= max_occur_time)

        if min_occur_time:
            stmt = stmt.where(ThingPredictLog.occur_time >= min_occur_time)

        stmt = stmt.offset(skip_count).limit(max_count)
        result = await db_session.execute(stmt)
        thing_predict_logs = result.scalars().all()

        return thing_predict_logs
    
    async def get_by_id(self, db_session: AsyncSession, id: str) -> ThingPredictLogRead:
        stmt = select(ThingPredictLog).where(ThingPredictLog.id == id)
        result = await db_session.execute(stmt)
        thing_predict_log = result.scalars().first()

        return thing_predict_log
    
    async def create(
        self,
        occur_time: str,
        thing_data: str,
        position: str,
        lane_name: str,
        camera_name: str,
        no: str,
        db_session: AsyncSession,
    ) -> ThingPredictLogCreateResponse:
        thing_predict_log = ThingPredictLog(
            occur_time=occur_time,
            thing_data=thing_data,
            position=position,
            lane_name=lane_name if lane_name is not None else "",
            camera_name=camera_name,
            no=no
        )
        db_session.add(thing_predict_log)
        await db_session.commit()
        await db_session.refresh(thing_predict_log)

        return thing_predict_log
    
    async def delete(self, id: str,db_session: AsyncSession) -> None:
        stmt = delete(ThingPredictLog).where(ThingPredictLog.id == id)
        await db_session.execute(stmt)
        await db_session.commit()

        return None