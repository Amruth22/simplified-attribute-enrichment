"""
Configuration settings for the Simplified Attribute Enrichment service
"""
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API settings
    HOST: str = "127.0.0.1"
    PORT: int = 8080
    
    # Debug settings
    DEBUG_MODE: bool = os.getenv("DEBUG_MODE", "False").lower() in ("true", "1", "t")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Google API settings
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    GOOGLE_CSE_ID: str = os.getenv("GOOGLE_CSE_ID", "")
    
    # Gemini API settings
    GEMINI_PROJECT_ID: str = os.getenv("GEMINI_PROJECT_ID", "data-lighthouse-bds-gen-ai")
    GEMINI_LOCATION: str = os.getenv("GEMINI_LOCATION", "us-central1")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    
    # Processing settings
    MAX_BATCH_SIZE: int = int(os.getenv("MAX_BATCH_SIZE", "50"))
    MAX_ROWS_TO_PROCESS: int = int(os.getenv("MAX_ROWS_TO_PROCESS", "2000"))
    
    # Token cost settings
    USD_TO_INR: float = float(os.getenv("USD_TO_INR", "86.0"))  # 1 USD = 86 INR
    INPUT_TOKEN_COST_PER_MILLION: float = float(os.getenv("INPUT_TOKEN_COST_PER_MILLION", "0.10"))  # $0.10 per 1M tokens
    OUTPUT_TOKEN_COST_PER_MILLION: float = float(os.getenv("OUTPUT_TOKEN_COST_PER_MILLION", "0.40"))  # $0.40 per 1M tokens
    
    # File paths - use relative paths or environment variables for better portability
    TAXONOMY_PATH: str = os.getenv("TAXONOMY_PATH", "./data/taxonomy.xlsx")
    OUTPUT_DIR: str = os.getenv("OUTPUT_DIR", "./output")
    
    # Global token tracking
    ENABLE_TOKEN_TRACKING: bool = os.getenv("ENABLE_TOKEN_TRACKING", "True").lower() in ("true", "1", "t")
    
    # Mock mode for testing without API calls
    MOCK_GEMINI_API: bool = os.getenv("MOCK_GEMINI_API", "False").lower() in ("true", "1", "t")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Create settings instance
settings = Settings()