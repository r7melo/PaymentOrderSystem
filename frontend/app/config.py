import os


class Settings:
    API_GATEWAY_URL: str = os.getenv("API_GATEWAY_URL", "http://gateway:8000")
    PUBLIC_API_URL: str = os.getenv("PUBLIC_API_URL", "http://localhost:30000")
    APP_NAME: str = "PaymentOrderSystem - Frontend"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-change-me")
    SESSION_COOKIE_NAME: str = "pos_session"


settings = Settings()