from fastapi import APIRouter, HTTPException
from auth.jwt import create_token_pair, verify_refresh_token
from auth.passwd import verify_password
from manager.users import UserManager
from schemas.auth import Token, oauth2_token_scheme, RefreshRequest, login_form_schema
from schemas.users import UserInDB

userManager = UserManager()

router = APIRouter(
    tags=["auth"],
    prefix="/api/auth",
)


@router.post("/login", response_model=Token)
async def login(form_data: login_form_schema):
    """
    Login with the following information:

    - **username**
    - **password**

    """

    user_in_db: UserInDB = await userManager.get_user_in_db(form_data.username)

    if user_in_db is None:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(form_data.password, user_in_db.password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return await create_token_pair(
        {"username": user_in_db.name, "id": user_in_db.id},
        {"username": user_in_db.name, "id": user_in_db.id},
    )


@router.post("/refresh", response_model=Token)
async def refresh(refersh_data: RefreshRequest):
    """
    Refresh token with the following information:

    - **token** in `Authorization` header

    """
    payload: dict = await verify_refresh_token(refersh_data.refresh_token)
    u_id:int = payload.get("id")

    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    username: str = payload.get("user")
    if username is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid token ( No `username` in payload )",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return await create_token_pair(
        {"user": username, "id": u_id}, {"user": username, "id": u_id}
    )
