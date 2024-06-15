import os
from functools import lru_cache

from dotenv import load_dotenv

class Settings():
    app_mode: str = os.getenv("APP_MODE")
    port:int = int(os.getenv("PORT"))
    reload:bool = bool(os.getenv("RELOAD"))
    database_url:str = os.getenv("DATABASE_URL")

@lru_cache()
def get_settings():
    load_dotenv( f".env.{os.getenv('APP_MODE')}")
    return Settings()
