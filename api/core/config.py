import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()


class Settings:
    database_username: str = os.getenv("DB_USER", "") 
    database_password: str = os.getenv("DB_PASSWORD", "")
    database_host: str = os.getenv("DB_HOST", "localhost")
    database_port: str = os.getenv("DB_PORT", "5432")
    database_name: str = os.getenv("DB_NAME", "") 

    _encoded_password = quote_plus(database_password) if database_password else ""

    DATABASE_URL = f'postgresql+asyncpg://{database_username}:{_encoded_password}@{database_host}:{database_port}/{database_name}'
    SYNC_DATABASE_URL = f'postgresql://{database_username}:{_encoded_password}@{database_host}:{database_port}/{database_name}'

    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

    FACEBOOK_CLIENT_ID = os.getenv("FACEBOOK_CLIENT_ID")
    FACEBOOK_CLIENT_SECRET = os.getenv("FACEBOOK_CLIENT_SECRET")

    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM", "HS256")

    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
    API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GROK_API_KEY: str = os.getenv("GROK_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    FREE_CHATGPT_TOKEN: str = os.getenv("FREE_CHATGPT_TOKEN", "")
    FREE_DEEPSEEK_TOKEN: str = os.getenv("FREE_DEEPSEEK_TOKEN", "")

    _origins = os.getenv(
        "ALLOWED_ORIGINS",
        ",".join(
            [
                "http://localhost:3000",
                "http://127.0.0.1:3000",
                "http://localhost:5173",
                "http://127.0.0.1:5173",
                "https://craftyxhub.com",
                "https://www.craftyxhub.com",
                "https://admin.craftyxhub.com",
            ]
        ),
    )
    ALLOWED_ORIGINS = (
        [o.strip() for o in _origins.split(",")] if _origins else [
            "http://localhost:3000"
        ]
    )

    ALLOW_ORIGIN_REGEX: str | None = os.getenv("ALLOW_ORIGIN_REGEX") or None
    ALLOW_CREDENTIALS: bool = (
        os.getenv("ALLOW_CREDENTIALS", "true").lower() == "true"
    )
    ALLOW_METHODS: list[str] = (
        [m.strip() for m in os.getenv("ALLOW_METHODS", "*").split(",")]
        if os.getenv("ALLOW_METHODS") != "*"
        else ["*"]
    )
    ALLOW_HEADERS: list[str] = (
        [h.strip() for h in os.getenv("ALLOW_HEADERS", "*").split(",")]
        if os.getenv("ALLOW_HEADERS") != "*"
        else ["*"]
    )
    EXPOSE_HEADERS: list[str] = (
        [h.strip() for h in os.getenv("EXPOSE_HEADERS", "").split(",")]
        if os.getenv("EXPOSE_HEADERS")
        else []
    )
    CORS_MAX_AGE: int = int(os.getenv("CORS_MAX_AGE", "600"))

    def __post_init__(self):
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
