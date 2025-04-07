"""
Configuration settings for the Simplified Attribute Enrichment service
"""
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API settings
    HOST: str = "127.0.0.1"
    PORT: int = 8080
    
    # Google API settings
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    GOOGLE_CSE_ID: str = os.getenv("GOOGLE_CSE_ID", "")
    
    # Gemini API settings
    GEMINI_PROJECT_ID: str = "data-lighthouse-bds-gen-ai"
    GEMINI_LOCATION: str = "us-central1"
    GEMINI_MODEL: str = "gemini-2.0-flash"
    
    # Processing settings
    MAX_BATCH_SIZE: int = 50
    MAX_ROWS_TO_PROCESS: int = 2000
    
    # Token cost settings
    USD_TO_INR: float = 86.0  # 1 USD = 86 INR
    INPUT_TOKEN_COST_PER_MILLION: float = 0.10  # $0.10 per 1M tokens
    OUTPUT_TOKEN_COST_PER_MILLION: float = 0.40  # $0.40 per 1M tokens
    
    # File paths - use relative paths or environment variables for better portability
    TAXONOMY_PATH: str = os.getenv("TAXONOMY_PATH", "./data/taxonomy.xlsx")
    OUTPUT_DIR: str = os.getenv("OUTPUT_DIR", "./output")
    
    # Global token tracking
    ENABLE_TOKEN_TRACKING: bool = True
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Create settings instance
settings = Settings()