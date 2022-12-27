from pydantic import BaseSettings

import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    DB_URL: str = os.environ["DB_URL"]

    ACCESS_TOKEN_EXPIRES_IN: int = os.environ["ACCESS_TOKEN_EXPIRES_IN"]
    REFRESH_TOKEN_EXPIRES_IN: int = os.environ["REFRESH_TOKEN_EXPIRES_IN"]

    JWT_SECRET_KEY: str = os.environ["JWT_SECRET_KEY"]


settings = Settings()