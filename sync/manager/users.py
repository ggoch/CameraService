from contextlib import contextmanager
from sqlalchemy.orm import Session 
from sqlalchemy import select , update , delete
import hashlib


from database.generic import get_db
from entitys.users import User as UserModel 
from schemas import users as UserSchema

@contextmanager
def get_db_session():
    db_session = next(get_db())
    try:
        yield db_session
    finally:
        db_session.close()

def get_user_id_by_email(email: str):
    with get_db_session() as db_session:
        stmt = select(UserModel.id).where(UserModel.email == email)
        user = db_session.execute(stmt).first()
        if user:
            return user

        return None

def create_user(newUser: UserSchema.UserCreate ):
    with get_db_session() as db_session:

        user = UserModel(
            name=newUser.name,
            password=newUser.password,
            age=newUser.age,
            birthday=newUser.birthday,
            email=newUser.email,
            avatar=newUser.avatar
        )

        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        return user
    
def get_users(keyword:str=None,last:int=0,limit:int=50):
    with get_db_session() as db_session:
        stmt = select(UserModel.name,UserModel.id,UserModel.email,UserModel.avatar)
        if keyword:
            stmt = stmt.where(UserModel.name.like(f"%{keyword}%"))
        stmt = stmt.offset(last).limit(limit)
        users =  db_session.execute(stmt).all()
    
        return users