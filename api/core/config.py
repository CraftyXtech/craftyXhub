import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

# class Settings:
#     # PostgreSQL configuration
#     database_username: str = os.getenv("DB_USER", "postgres")
#     database_password: str = os.getenv("DB_PASSWORD", "root")
#     database_host: str = os.getenv("DB_HOST", "localhost")
#     database_port: str = os.getenv("DB_PORT", "5432")
#     database_name: str = os.getenv("DB_NAME", "xhub")

#     DATABASE_URL = f'postgresql+asyncpg://{database_username}:{database_password}@{database_host}:{database_port}/{database_name}'
    
#     # for migrations since alembic does not support async db connections
#     SYNC_DATABASE_URL = f'postgresql://{database_username}:{database_password}@{database_host}:{database_port}/{database_name}'

#     GOOGLE_CLIENT_ID = os.getenv("CLIENT_ID", "")
#     GOOGLE_CLIENT_SECRET = os.getenv("CLIENT_SECRET", "")
    
#     ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 15)
#     SECRET_KEY = os.getenv("SECRET_KEY", "")
#     ALGORITHM = os.getenv("ALGORITHM", "HS256")


class Settings:
    sqlite_db_path = Path(__file__).resolve().parent.parent / "database" / "dev.sqlite3"

    DATABASE_URL = f"sqlite+aiosqlite:///{sqlite_db_path}"
    SYNC_DATABASE_URL = f"sqlite:///{sqlite_db_path}"
    
    GOOGLE_CLIENT_ID = os.getenv("CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET = os.getenv("CLIENT_SECRET", "")
    
    ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 15)
    SECRET_KEY = os.getenv("SECRET_KEY", "")
    ALGORITHM = os.getenv("ALGORITHM", "HS256")

settings = Settings()