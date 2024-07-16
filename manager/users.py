from contextlib import asynccontextmanager, contextmanager
from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete
import hashlib
from sqlalchemy.ext.asyncio import AsyncSession


from auth.passwd import get_password_hash
from database.generic import get_db, manager_class_decorator
from database.redis_cache import generic_cache_get, generic_cache_update, generic_pagenation_cache_get, user_cache_delete
from entitys.users import User as UserModel
from schemas import users as UserSchema


@manager_class_decorator
class UserManager:

    @generic_pagenation_cache_get(prefix="user",cls=UserSchema.UserRead)
    async def get_users(
        self,
        db_session: AsyncSession,
        keyword: str = None,
        skip_count: int = 0,
        max_count: int = 50,
    ):
        stmt = select(UserModel.name, UserModel.id, UserModel.email, UserModel.avatar)
        if keyword:
            stmt = stmt.where(UserModel.name.like(f"%{keyword}%"))
        stmt = stmt.offset(skip_count).limit(max_count)
        result = await db_session.execute(stmt)
        users = result.all()

        return users

    async def get_user_id_by_email(self, email: str, db_session: AsyncSession):
        stmt = select(UserModel.id).where(UserModel.email == email)
        user = (await db_session.execute(stmt)).first()
        if user:
            return user

        return None

    @generic_cache_get(prefix="user",key="user_id",cls=UserSchema.UserRead)
    async def get_user_by_id(self, user_id: int, db_session: AsyncSession):
        stmt = select(
            UserModel.name, UserModel.id, UserModel.email, UserModel.avatar
        ).where(UserModel.id == user_id)
        user = (await db_session.execute(stmt)).first()
        if user:
            return user

        return None

    async def create_user(
        self,
        newUser: UserSchema.UserCreate,
        db_session: AsyncSession,
    ):
        password = get_password_hash(newUser.password)

        user = UserModel(
            name=newUser.name,
            password=password,
            age=newUser.age,
            birthday=newUser.birthday,
            email=newUser.email,
            avatar=newUser.avatar,
        )

        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        return user

    @generic_cache_update(prefix="user",key="user_id")
    async def update_user(
        self,
        user_id: int,
        newUser: UserSchema.UserUpdate,
        db_session: AsyncSession,
    ):
        stmt = (
            update(UserModel)
            .where(UserModel.id == user_id)
            .values(
                name=newUser.name,
                age=newUser.age,
                birthday=newUser.birthday,
                avatar=newUser.avatar,
            )
        )

        await db_session.execute(stmt)
        await db_session.commit()

        return newUser

    @generic_cache_update(prefix="user",key="user_id")
    async def update_user_password(
        self,
        user_id: int,
        newUser: UserSchema.UserUpdatePassword,
        db_session: AsyncSession,
    ):
        password = get_password_hash(newUser.password)

        stmt = (
            update(UserModel)
            .where(UserModel.id == user_id)
            .values(
                password=password,
            )
        )
        await db_session.execute(stmt)
        await db_session.commit()

    @generic_cache_get(prefix="user",key="email",cls=UserSchema.UserInDB)
    async def get_user_in_db(
        self, email: str, db_session: AsyncSession = None
    ) -> UserSchema.UserInDB:
        stmt = select(UserModel.id, UserModel.name, UserModel.password).where(
            UserModel.email == email
        )
        result = await db_session.execute(stmt)
        user = result.first()
        if user:
            return user

        return None

    @user_cache_delete(prefix="user",key="user_id")
    async def delete_user(self, user_id: int, db_session: AsyncSession):
        stmt = delete(UserModel).where(UserModel.id == user_id)
        await db_session.execute(stmt)
        await db_session.commit()
        return None
