import logging
import sys
from pathlib import Path

from app.config.settings import settings


_logging_initialized = False


def setup_logging(force: bool = False) -> None:
    """Configure application logging.
    
    Args:
        force: If True, reinitialize logging even if already initialized.
               If False, skip initialization if already done.
    """
    global _logging_initialized
    
    # Guard against duplicate initialization
    if _logging_initialized and not force:
        return
    
    # Create logs directory if it doesn't exist
    log_dir = Path(settings.log_directory)
    log_dir.mkdir(exist_ok=True)
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format=settings.log_format,
        handlers=[
            # Console handler
            logging.StreamHandler(sys.stdout),
            # File handler
            logging.FileHandler(log_dir / "investigation.log"),
        ],
        force=force,  # Force reconfiguration if force=True
    )
    
    _logging_initialized = True


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the given name.
    
    Args:
        name: The logger name, typically __name__ of the calling module.
        
    Returns:
        A logger instance configured with the root logger settings.
    """
    return logging.getLogger(name)
