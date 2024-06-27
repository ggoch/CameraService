import asyncio
from fastapi import FastAPI
from contextlib import asynccontextmanager

# import redis
import redis.asyncio as redis

from handlers.handler_camera_event import sub_camera_event
from setting.config import get_settings

settings = get_settings()

if settings.run_mode == "ASYNC":
    from api.infor import router as infor_router
    from api.users import router as user_router
    from api.items import router as item_router
    from api.auth import router as auth_router
    from api.camera import router as camera_router
    from api.camera import live_router as camera_live_router
    from database.generic import init_db , close_db
    from services.camera_service import init_camera_service
    from database.redis_cache import not_decode_redis_pool

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Startup event
        print("Application startup")
        rc = redis.Redis(connection_pool=not_decode_redis_pool)

        # await init_db()
        # await init_camera_service(rc)
        # await sub_camera_event(rc)
        task = asyncio.create_task(sub_camera_event(rc))
        yield
        # Shutdown event
        print("Application shutdown")
        task.cancel()
        await close_db()

    app = FastAPI(lifespan=lifespan)

    app.include_router(infor_router)
    app.include_router(user_router)
    app.include_router(item_router)
    app.include_router(auth_router)
    app.include_router(camera_router)
    app.include_router(camera_live_router)
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


@app.get("/")
def hello_world():
    return "Hello World"


