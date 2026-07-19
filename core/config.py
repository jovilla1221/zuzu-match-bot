import os
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env file."""
    
    # Telegram Bot
    BOT_TOKEN: str = Field(description="Telegram Bot API Token")
    ADMIN_CHAT_ID: int = Field(default=0, description="Telegram Chat ID for Admin alerts")
    
    # Server & Web App
    API_HOST: str = Field(default="127.0.0.1", description="API listen host")
    API_PORT: int = Field(default=8008, description="API listen port")
    WEBAPP_URL: str = Field(description="Telegram Web App base URL")
    SECRET_KEY: str = Field(description="App secret key for token signing")
    
    # Database & Cache
    DATABASE_URL: str = Field(
        description="Async Database Connection String"
    )
    REDIS_URL: str = Field(default="redis://127.0.0.1:6379/0", description="Redis Connection String")

    # Gemini AI Settings
    GEMINI_API_KEY: str = Field(
        description="Google Gemini API Key"
    )
    GEMINI_MODEL: str = Field(default="gemini-3.1-flash-lite", description="Gemini AI Model identifier")
    
    # Debug Mode
    DEBUG: bool = Field(default=False, description="Enable debug mode")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
