import pytest
import asyncio
import os
import pytest_asyncio
import json
from dotenv import load_dotenv

from httpx import AsyncClient
import pytest_asyncio
from sqlalchemy.schema import CreateTable
import entitys


def pytest_addoption(parser):
    parser.addoption(
        "--prod", action="store_true", help="Run the server in production mode."
    )
    parser.addoption("--test", action="store_true", help="Run the server in test mode.")
    parser.addoption(
        "--dev", action="store_true", help="Run the server in development mode."
    )
    parser.addoption("--sync", action="store_true", help="Run the server in Sync mode.")
    parser.addoption(
        "--db",
        help="Run the server in database type.",
        choices=["mysql", "postgresql", "sqlite"],
        default="sqlite",
    )


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def dependencies(request):
    args = request.config

    if args.getoption("prod"):
        load_dotenv("./setting/.env.prod")
    elif args.getoption("dev"):
        load_dotenv("./setting/.env.dev")
    else:
        load_dotenv("./setting/.env.test")

    if args.getoption("sync"):
        os.environ["RUN_MODE"] = "SYNC"
    else:
        os.environ["RUN_MODE"] = "ASYNC"

    os.environ["DB_TYPE"] = args.getoption("db")
    print("DB_TYPE", os.getenv("DB_TYPE"))


@pytest_asyncio.fixture(scope="module")
async def async_client(dependencies) -> AsyncClient:
    from .app import app

    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture(scope="module")
async def get_user_data():
    with open("data/user_data.json") as f:
        data = json.load(f)
    return data


@pytest.fixture(scope="function")
async def async_session(init_test_db):
    from setting.config import get_settings
    from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker

    settings = get_settings()
    engine = create_async_engine(settings.database_url, echo=True, pool_pre_ping=True)
    async_session_factory = async_sessionmaker(
        autocommit=False, autoflush=False, bind=engine
    )
    async with async_session_factory() as session:
        yield session
        await session.rollback()
