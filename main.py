"""
Punto de entrada de la aplicación FURIPS Desktop.
"""
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from app.config import check_db_connection, get_settings
from app.infra.logging_conf import setup_logging, get_logger
from app.ui.views import MainWindow
from app.ui.presenters import MainPresenter


def main():
    """Función principal de la aplicación.   """
    # Configurar logging
    setup_logging()
    logger = get_logger(__name__)
    
    logger.info("Iniciando aplicación FURIPS Desktop")
    
    # Verificar configuración
    settings = get_settings()
    logger.info(f"Versión: {settings.APP_VERSION}")
    
    # Verificar conexión a BD
    if not check_db_connection():
        logger.error("No se pudo conectar a la base de datos principal")
        print("ERROR: No se pudo conectar a la base de datos.")
        print("Verifique la configuración en el archivo .env")
        return 1
    
    logger.info("Conexión a base de datos establecida")
    
    # Crear aplicación Qt
    app = QApplication(sys.argv)
    app.setApplicationName(settings.APP_NAME)
    app.setApplicationVersion(settings.APP_VERSION)
    
    # Crear ventana principal y presenter
    main_window = MainWindow()
    main_presenter = MainPresenter(main_window)
    
    # Mostrar ventana
    main_window.show()
    
    logger.info("Interfaz gráfica iniciada")
    
    # Ejecutar aplicación
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
