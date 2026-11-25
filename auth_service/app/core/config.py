from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    RABBITMQ_URL: str = "amqp://guest:guest@rabbitmq:5672/"
    DATABASE_URL: str = "postgresql+asyncpg://auth_user:auth_pass@auth-db:5432/auth_db"
    JWT_SECRET: str = "super-secret-jwt-key-payment-system"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    AUTH_QUEUE: str = "rpc.auth.requests"


settings = Settings()