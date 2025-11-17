"""
Configuración de la aplicación.
Carga variables de entorno desde .env usando pydantic.
"""
from functools import lru_cache
from pathlib import Path
from typing import Optional
import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# Cargar .env explícitamente ANTES de crear Settings (con override=True)
_env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(_env_path, override=True)


class Settings(BaseSettings):
    """Configuración global de la aplicación."""
    
    # Base de datos principal (furips) - RW
    DB_URL: str
    DB_POOL_SIZE: int = 5
    DB_POOL_RECYCLE: int = 3600
    DB_ECHO: bool = False
    
    # Base de datos externa - RO
    DB_EXT_URL: Optional[str] = None
    DB_EXT_POOL_SIZE: int = 3
    DB_EXT_POOL_RECYCLE: int = 3600
    DB_EXT_ECHO: bool = False
    
    # Rutas de plantillas PDF
    PDF_TEMPLATE_FURIPS1: str = "app/infra/pdf/templates/furips1_base.pdf"
    PDF_TEMPLATE_FURIPS2: str = "app/infra/pdf/templates/furips2_base.pdf"
    PDF_OUTPUT_DIR: str = "output"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/furips.log"
    
    # Aplicación
    APP_NAME: str = "FURIPS Desktop"
    APP_VERSION: str = "1.0.0"
    
    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).parent.parent.parent / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
        env_file_override=True  # El archivo .env tiene prioridad sobre las variables del sistema
    )
    
    def get_pdf_template_path(self, template_type: str) -> Path:
        """Retorna el path absoluto de la plantilla PDF."""
        if template_type == "furips1":
            return Path(self.PDF_TEMPLATE_FURIPS1)
        elif template_type == "furips2":
            return Path(self.PDF_TEMPLATE_FURIPS2)
        else:
            raise ValueError(f"Tipo de plantilla desconocido: {template_type}")
    
    def get_output_dir(self) -> Path:
        """Retorna el path del directorio de salida."""
        output_path = Path(self.PDF_OUTPUT_DIR)
        output_path.mkdir(parents=True, exist_ok=True)
        return output_path


@lru_cache()
def get_settings() -> Settings:
    """
    Retorna una instancia cacheada de Settings.
    Usar esta función para obtener la configuración en toda la app.
    """
    return Settings()
