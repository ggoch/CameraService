from fastapi import FastAPI
from contextlib import asynccontextmanager

from setting.config import get_settings

settings = get_settings()

if settings.run_mode == "ASYNC":
    from api.infor import router as infor_router
    from api.users import router as user_router
    from api.items import router as item_router
    from api.auth import router as auth_router
    from database.generic import init_db, close_db
    from sqlalchemy.schema import CreateTable
    import entitys

    async def init_test_db():
        from setting.config import get_settings
        from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

        settings = get_settings()
        engine = create_async_engine(
            settings.database_url,
            echo=True,
            pool_pre_ping=True,
            connect_args={"check_same_thread": False},
        )
        SessionLocal = async_sessionmaker(
            autocommit=False, autoflush=False, bind=engine
        )
        async with SessionLocal() as db:
            async with db.begin():
                await db.execute(
                    CreateTable(entitys.User.__table__, if_not_exists=True)
                )
                await db.execute(
                    CreateTable(entitys.Item.__table__, if_not_exists=True)
                )

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Startup event
        print("Application startup")
        # await init_db()
        await init_test_db()
        yield
        # Shutdown event
        print("Application shutdown")
        # await close_db()

    app = FastAPI(lifespan=lifespan)

    app.include_router(infor_router)
    app.include_router(user_router)
    app.include_router(item_router)
    app.include_router(auth_router)
else:
    from sync.api.infor import router as infor_router
    from sync.api.users import router as user_router
    from sync.api.items import router as item_router
    from sync.database.generic import init_db

    @asynccontextmanager
    def lifespan(app: FastAPI):
        # Startup event
        print("Application startup")
        init_db()
        yield
        # Shutdown event
        print("Application shutdown")

    app = FastAPI(lifespan=lifespan)

    app.include_router(infor_router)
    app.include_router(user_router)
    app.include_router(item_router)
