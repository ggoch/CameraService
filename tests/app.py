from fastapi import FastAPI
from contextlib import asynccontextmanager

from setting.config import get_settings

settings = get_settings()

if settings.run_mode == "ASYNC":
    from api.infor import router as infor_router
    from api.users import router as user_router
    from api.items import router as item_router
    from api.auth import router as auth_router
    from database.generic import init_db , close_db

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Startup event
        print("Application startup")
        await init_db()
        yield
        # Shutdown event
        print("Application shutdown")
        await close_db()

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