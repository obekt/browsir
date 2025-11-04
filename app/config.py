from pydantic_settings import BaseSettings
from pydantic import field_validator
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # OpenAI Configuration
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"
    
    @field_validator('openai_api_key')
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        """Ensure API key is not empty"""
        if not v or not v.strip():
            raise ValueError(
                "OPENAI_API_KEY is required and cannot be empty. "
                "Get your API key from: https://platform.openai.com/api-keys"
            )
        return v.strip()
    
    # Selenium Configuration
    selenium_timeout: int = 30
    max_popup_retries: int = 3
    chrome_headless: bool = True
    
    # Application Configuration
    log_level: str = "INFO"
    port: int = 8000
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


