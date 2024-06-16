from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from requests import Session
from sqlalchemy import select, update, delete
from api.depends import (
    check_user_id,
    pagination_parms,
    paginationParms,
    test_verify_token,
)
from database.generic import get_db
from mock_datas.fackdb import fake_db

from schemas import users as UserSchema
from entitys.users import User
from manager import users as UserCrud

router = APIRouter(
    tags=["users"],
    prefix="/api",
    # dependencies=[Depends(test_verify_token)]
)


@router.get(
    "/users",
    response_model=list[UserSchema.UserRead],
    response_description="Get list of user",
)
def get_users(
    page_parms: Annotated[paginationParms, Depends(pagination_parms)],
):
    """
    users = UserCrud.get_users(
        page_parms["keyword"],
        page_parms["last"],
        page_parms["limit"]
    )
    """
    users = UserCrud.get_users(**page_parms)
    return users


@router.get(
    "/users/{user_id}",
    response_model=UserSchema.UserRead,
    status_code=201,
)
def get_user_by_id(
    user_id: int, qry: str = None, db_session: Session = Depends(get_db)
):

    stmt = select(User.name, User.id, User.email, User.avatar).where(User.id == user_id)
    user = db_session.execute(stmt).first()
    if user:
        return user

    raise HTTPException(status_code=404, detail="User not found")


@router.post(
    "/users",
    response_model=UserSchema.UserCreateResponse,
    status_code=status.HTTP_201_CREATED,
    response_description="Create new user",
)
def create_users(newUser: UserSchema.UserCreate, db_session: Session = Depends(get_db)):
    user = UserCrud.get_user_id_by_email(newUser.email)
    if user:
        raise HTTPException(status_code=409, detail=f"User already exists")

    user = UserCrud.create_user(newUser)
    return vars(user)


@router.put("/users/{user_id}", response_model=UserSchema.UserUpdateResponse)
def update_users(
    user_id: int, newUser: UserSchema.UserUpdate, db_session: Session = Depends(get_db)
):

    stmt = select(User.id).where(User.id == user_id)
    user = db_session.execute(stmt).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    stmt = (
        update(User)
        .where(User.id == user_id)
        .values(
            name=newUser.name,
            age=newUser.age,
            birthday=newUser.birthday,
            avatar=newUser.avatar,
        )
    )

    db_session.execute(stmt)
    db_session.commit()

    return newUser


@router.put("/users/{user_id}/password", status_code=200)
def update_user_password(
    user_id: int,
    newUser: UserSchema.UserUpdatePassword,
    db_session: Session = Depends(get_db),
):
    # ...
    stmt = (
        update(User)
        .where(User.id == user_id)
        .values(
            password=newUser.password,
        )
    )
    db_session.execute(stmt)
    db_session.commit()

    return newUser


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_users(
    user_id: int = Depends(check_user_id),
    db_session: Session = Depends(get_db),
):

    stmt = delete(User).where(User.id == user_id)
    db_session.execute(stmt)
    db_session.commit()

    return
