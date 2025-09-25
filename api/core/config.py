import os
from dotenv import load_dotenv
from pathlib import Path
from urllib.parse import quote_plus

load_dotenv()

class Settings:
    # PostgreSQL configuration - ALL from environment variables only
    database_username: str = os.getenv("DB_USER") or ""
    database_password: str = os.getenv("DB_PASSWORD") or ""
    database_host: str = os.getenv("DB_HOST", "localhost")
    database_port: str = os.getenv("DB_PORT", "5432")
    database_name: str = os.getenv("DB_NAME") or ""

    # URL-encode password to handle special characters
    _encoded_password = quote_plus(database_password) if database_password else ""
    
    DATABASE_URL = f'postgresql+asyncpg://{database_username}:{_encoded_password}@{database_host}:{database_port}/{database_name}'

    # for migrations since alembic does not support async db connections
    SYNC_DATABASE_URL = f'postgresql://{database_username}:{_encoded_password}@{database_host}:{database_port}/{database_name}'

    # OAuth configuration - NO defaults for secrets
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
    
    FACEBOOK_CLIENT_ID = os.getenv("FACEBOOK_CLIENT_ID")
    FACEBOOK_CLIENT_SECRET = os.getenv("FACEBOOK_CLIENT_SECRET")

    # Security configuration - NO defaults for sensitive values
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM", "HS256")
    
    # Application URLs - non-sensitive defaults OK
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
    API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

    # CORS configuration
    # Include common local dev and production domains by default.
    # Can be overridden via ALLOWED_ORIGINS env.
    _origins = os.getenv(
        "ALLOWED_ORIGINS",
        ",".join(
            [
                # Local development
                "http://localhost:3000",
                "http://127.0.0.1:3000",
                # Production sites
                "https://craftyxhub.com",
                "https://www.craftyxhub.com",
                # If you host an admin app on a subdomain,
                # add it here or via env
                "https://admin.craftyxhub.com",
            ]
        ),
    )
    ALLOWED_ORIGINS = (
        [o.strip() for o in _origins.split(",")] if _origins else [
            "http://localhost:3000"
        ]
    )

    # Optional CORS regex. If set, will be passed to CORSMiddleware
    # e.g., r"https://([a-z0-9-]+\.)?craftyxhub\.com"
    ALLOW_ORIGIN_REGEX: str | None = os.getenv("ALLOW_ORIGIN_REGEX") or None

    def __post_init__(self):
        """Validate that all required environment variables are set"""
        required_vars = {
            "DB_USER": self.database_username,
            "DB_PASSWORD": self.database_password,
            "DB_NAME": self.database_name,
            "SECRET_KEY": self.SECRET_KEY,
        }
        
        missing_vars = [
            var for var, value in required_vars.items() if not value
        ]
        if missing_vars:
            raise ValueError(
                "Required environment variables missing: "
                f"{', '.join(missing_vars)}"
            )


settings = Settings()
