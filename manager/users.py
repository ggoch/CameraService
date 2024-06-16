from contextlib import asynccontextmanager, contextmanager
from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete
import hashlib
from sqlalchemy.ext.asyncio import AsyncSession


from auth.passwd import get_password_hash
from database.generic import get_db, manager_class_decorator
from entitys.users import User as UserModel
from schemas import users as UserSchema


@manager_class_decorator
class UserManager:

    async def get_users(
        self,
        db_session: AsyncSession,
        keyword: str = None,
        last: int = 0,
        limit: int = 50,
    ):
        stmt = select(UserModel.name, UserModel.id, UserModel.email, UserModel.avatar)
        if keyword:
            stmt = stmt.where(UserModel.name.like(f"%{keyword}%"))
        stmt = stmt.offset(last).limit(limit)
        result = await db_session.execute(stmt)
        users = result.all()

        return users

    async def get_user_id_by_email(self, email: str, db_session: AsyncSession):
        stmt = select(UserModel.id).where(UserModel.email == email)
        user = (await db_session.execute(stmt)).first()
        if user:
            return user

        return None

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

    async def delete_user(self, user_id: int, db_session: AsyncSession):
        stmt = delete(UserModel).where(UserModel.id == user_id)
        await db_session.execute(stmt)
        await db_session.commit()
        return None
