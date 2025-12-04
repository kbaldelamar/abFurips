"""
Configuración de logging para la aplicación.
"""
import logging
import logging.handlers
from pathlib import Path

from app.config import get_settings


def setup_logging():
    """Configura el sistema de logging."""
    settings = get_settings()
    
    # Crear directorio de logs si no existe
    log_file = Path(settings.LOG_FILE)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Configurar formato
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    
    # Handler para archivo con rotación
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    
    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    
    # Configurar root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Silenciar logs verbosos de SQLAlchemy
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    
    logging.info("=" * 60)
    logging.info(f"{settings.APP_NAME} v{settings.APP_VERSION} iniciado")
    logging.info("=" * 60)


def get_logger(name: str) -> logging.Logger:
    """Retorna un logger con el nombre especificado."""
    return logging.getLogger(name)
