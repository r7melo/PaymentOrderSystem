from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    RABBITMQ_URL: str = "amqp://guest:guest@rabbitmq:5672/"
    JWT_SECRET: str = "super-secret-jwt-key-payment-system"
    JWT_ALGORITHM: str = "HS256"
    RPC_TIMEOUT: float = 5.0


settings = Settings()