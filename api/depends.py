from contextlib import contextmanager
from typing import Optional
from fastapi import HTTPException, Header

from sqlalchemy.orm import Session
from sqlalchemy import select

from entitys.users import User as UserModel
from database.generic import get_db


async def check_user_id(user_id: int):
    async with get_db() as db_session:
        stmt = select(UserModel.id).where(UserModel.id == user_id)
        user = (await db_session.execute(stmt)).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user.id


class paginationParms:
    def __init__(self, keyword: Optional[str] = None, skip_count: int = 0, max_count: int = 10):
        self.keyword = keyword
        self.skip_count = skip_count
        self.max_count = max_count


def pagination_parms(keyword: Optional[str] = None, skip_count: int = 0, max_count: int = 10):
    return {"keyword": keyword, "skip_count": skip_count, "max_count": max_count}


def test_verify_token(verify_header: str = Header()):
    if verify_header != "secret-token":
        raise HTTPException(status_code=403, detail="Forbidden")
    return verify_header
