from pathlib import Path
from typing import Literal, Optional

from pydantic import HttpUrl, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    database_path: str = "core_banking.db"

    # LLM Configuration
    default_llm_provider: str = "gemini"
    gemini_api_key: Optional[str] = None
    gemini_model: str = "gemini-2.5-flash"
    gemini_temperature: float = 0.0
    
    # MCP Configuration
    mcp_server_host: str = "localhost"
    mcp_server_port: int = 8000
    mcp_transport: Literal["in-process", "gateway"] = "in-process"
    mcp_gateway_url: HttpUrl | None = None
    mcp_gateway_username: str = "investigation"
    mcp_gateway_password: SecretStr | None = None

    @model_validator(mode="after")
    def validate_mcp_transport(self):
        if self.mcp_transport == "gateway" and self.mcp_gateway_url is None:
            raise ValueError("MCP_GATEWAY_URL is required in gateway mode")
        if self.mcp_transport == "gateway" and (
            not self.mcp_gateway_username
            or self.mcp_gateway_password is None
            or not self.mcp_gateway_password.get_secret_value()
        ):
            raise ValueError("MCP gateway credentials are required in gateway mode")
        return self

    mcp_read_timeout_seconds: float = 30.0
    mcp_max_retries: int = 2
    mcp_retry_delay_seconds: float = 0.5
    
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
