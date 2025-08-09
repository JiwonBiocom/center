from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # App
    APP_NAME: str = "AIBIO Center Management"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: Optional[str] = None
    
    # Supabase
    SUPABASE_URL: Optional[str] = None
    SUPABASE_ANON_KEY: Optional[str] = None
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = None
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # Business Info
    BUSINESS_PHONE: str = "02-2039-2783"
    BUSINESS_ADDRESS: str = "서울시 강남구 테헤란로 123"
    
    # Kakao API
    KAKAO_REST_API_KEY: str = ""
    KAKAO_ADMIN_KEY: str = ""
    KAKAO_SENDER_KEY: str = ""
    
    # Aligo SMS API
    ALIGO_API_KEY: str = ""
    ALIGO_USER_ID: str = ""
    ALIGO_SENDER: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"

settings = Settings()