import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

class Settings:
    database_username: str = os.getenv("DB_USER", "postgres")
    database_password: str = os.getenv("DB_PASSWORD", "root")
    database_host: str = os.getenv("DB_HOST", "localhost")
    database_port: int = os.getenv("DB_PORT", 5432)
    database_name: str = os.getenv("DB_NAME", "xhub")

    DATABASE_URL = f'postgresql+asyncpg://{database_username}:{database_password}@{database_host}:{database_port}/{database_name}'

    # for migrations since alembic does not support asyc db connections - ngori
    SYNC_DATABASE_URL = f'postgresql://{database_username}:{database_password}@{database_host}:{database_port}/{database_name}'


settings = Settings()