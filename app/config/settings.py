from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    database_path: str = "core_banking.db"
    
    # LLM Configuration
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    default_llm_provider: str = "openai"  # openai, anthropic, google
    default_model: str = "gpt-4o-mini"
    
    # MCP Configuration
    mcp_server_host: str = "localhost"
    mcp_server_port: int = 8000
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8001
    debug: bool = False
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_directory: str = "logs"
    
    # Investigation Configuration
    max_investigation_steps: int = 10
    investigation_timeout_seconds: int = 300
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


# Global settings instance
settings = Settings()
