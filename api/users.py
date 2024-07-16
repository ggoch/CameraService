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

from schemas import users as UserSchema
from entitys.users import User
from manager.users import UserManager

from schemas.auth import oauth2_token_scheme

userManager = UserManager()

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
async def get_users(
    page_parms: dict = Depends(pagination_parms),
):
    users = await userManager.get_users(**page_parms)
    return users


@router.get(
    "/users/{user_id}",
    response_model=UserSchema.UserRead,
    status_code=201,
)
async def get_user_by_id(user_id: int, qry: str = None):

    user = await userManager.get_user_by_id(user_id)
    if user:
        return user

    raise HTTPException(status_code=404, detail="User not found")


@router.post(
    "/users",
    response_model=UserSchema.UserCreateResponse,
    status_code=status.HTTP_201_CREATED,
    response_description="Create new user",
)
async def create_users(newUser: UserSchema.UserCreate):
    user = await userManager.get_user_id_by_email(newUser.email)
    if user:
        raise HTTPException(status_code=409, detail=f"User already exists")

    user = await userManager.create_user(newUser)
    return vars(user)


@router.put("/users/{user_id}", response_model=UserSchema.UserUpdateResponse)
async def update_users(
    user_id: int,
    newUser: UserSchema.UserUpdate,
    current_user: UserSchema.CurrentUser = Depends(get_current_user),
):
    user = await userManager.get_user_by_id(user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    user = await userManager.update_user(user_id, newUser)

    return newUser


@router.put("/users/{user_id}/password", status_code=200)
async def update_user_password(
    user_id: int,
    newUser: UserSchema.UserUpdatePassword,
    current_user: UserSchema.CurrentUser = Depends(get_current_user),
):
    user = await userManager.get_user_by_id(user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    await userManager.update_user_password(user_id, newUser)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_users(
    user_id: int = Depends(check_user_id),
    current_user: UserSchema.CurrentUser = Depends(get_current_user),
):

    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    await userManager.delete_user(user_id)

    return
