from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from requests import Session
from sqlalchemy import select, update, delete
from api.depends import (
    check_user_id,
    pagination_parms,
    paginationParms,
    test_verify_token,
)
from manager.car_no_predict_log import CarNoPredictLogManager

from schemas import car_no_predict_log as CarNoPredictLogSchema

carNoPredictLogManager = CarNoPredictLogManager()

router = APIRouter(
    tags=["carNoPredictLogs"],
    prefix="/api",
    # dependencies=[Depends(test_verify_token)]
)


@router.get(
    "/carNoPredictLogs",
    response_model=list[CarNoPredictLogSchema.CarNoPredictLogRead],
    response_description="Get list of predict car no logs",
)
async def get_logs(
    page_parms: dict = Depends(pagination_parms),
):
    logs = await carNoPredictLogManager.get_list(**page_parms)
    return logs


