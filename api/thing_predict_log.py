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
from auth.jwt import verify_access_token
from auth.utils import get_current_user
from database.generic import get_db

from entitys.users import User
from manager.users import UserManager
from manager.thing_predict_log import ThingPredictLogManager

from schemas import thing_predict_log as ThingPredictLogSchema

thingPredictLogManager = ThingPredictLogManager()

router = APIRouter(
    tags=["thingPredictLogs"],
    prefix="/api",
    # dependencies=[Depends(test_verify_token)]
)


@router.get(
    "/thingPredictLogs",
    response_model=list[ThingPredictLogSchema.ThingPredictLogRead],
    response_description="Get list of predict thing logs",
)
async def get_logs(
    page_parms: dict = Depends(pagination_parms),
):
    logs = await thingPredictLogManager.get_list(**page_parms)
    return logs


