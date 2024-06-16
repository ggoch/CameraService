from contextlib import contextmanager
from typing import Optional
from fastapi import HTTPException, Header

from sqlalchemy.orm import Session
from sqlalchemy import select 

from entitys.users import User as UserModel
from database.generic import get_db

@contextmanager
def get_db_session():
    db_session = next(get_db())
    try:
        yield db_session
    finally:
        db_session.close()
        
def check_user_id(user_id:int):
    with get_db_session() as db_session:
        stmt = select(UserModel.id).where(UserModel.id == user_id)
        user = db_session.execute(stmt).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user.id
    
class paginationParms:
    def __init__(self,keyword:Optional[str]=None,last:int=0,limit:int=50):
        self.keyword = keyword
        self.last = last
        self.limit = limit

def pagination_parms(keyword:Optional[str]=None,last:int=0,limit:int=50):
    return {
        "keyword":keyword,
        "last":last,
        "limit":limit
    }

def test_verify_token(verify_header: str = Header()):
    if verify_header != "secret-token":
        raise HTTPException(status_code=403, detail="Forbidden")
    return verify_header