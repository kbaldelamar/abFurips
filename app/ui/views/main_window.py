"""
Ventana principal de la aplicación.
"""
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QMenuBar,
    QMenu,
    QStatusBar,
    QMessageBox,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction


class MainWindow(QMainWindow):
    """Ventana principal de la aplicación FURIPS."""
    
    # Señales
    accion_diligenciar_furips = Signal()
    accion_exportar_magneticos = Signal()
    accion_imprimir_pdf = Signal()
    accion_configuracion = Signal()
    accion_salir = Signal()
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FURIPS Desktop - Sistema de Gestión de Accidentes de Tránsito")
        
        self._setup_ui()
        self._setup_menubar()
        self._setup_statusbar()
        
    def showEvent(self, event):
        """Se ejecuta cuando la ventana se muestra por primera vez."""
        super().showEvent(event)
        # Maximizar la ventana en el primer show
        if not event.spontaneous():
            self.showMaximized()
            # Después de maximizar, fijar el tamaño para evitar redimensionamiento
            from PySide6.QtCore import QTimer
            QTimer.singleShot(100, self._fix_window_size)
    
    def _fix_window_size(self):
        """Fija el tamaño de la ventana después de maximizar."""
        self.setFixedSize(self.size())
    
    def _setup_ui(self):
        """Configura el widget central."""
        # Widget central placeholder
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        
        # Aquí se cargará el formulario de accidente desde el presenter
        self.content_area = QVBoxLayout()
        layout.addLayout(self.content_area)
        
        # Widget de bienvenida inicial
        self._create_welcome_widget()
        
        self.setCentralWidget(central_widget)
    
    def _create_welcome_widget(self):
        """Crea el widget de bienvenida."""
        from PySide6.QtWidgets import QLabel
        
        welcome = QWidget()
        welcome_layout = QVBoxLayout(welcome)
        welcome_layout.setAlignment(Qt.AlignCenter)
        
        label = QLabel("Bienvenido a FURIPS Desktop\n\nSeleccione una opción del menú para comenzar")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 16pt; color: #666;")
        
        welcome_layout.addWidget(label)
        self.content_area.addWidget(welcome)
    
    def _setup_menubar(self):
        """Configura el menú principal."""
        menubar = self.menuBar()
        
        # Menú Archivo
        menu_archivo = menubar.addMenu("&Archivo")
        
        action_diligenciar = QAction("&Diligenciar FURIPS", self)
        action_diligenciar.setShortcut("Ctrl+N")
        action_diligenciar.triggered.connect(self.accion_diligenciar_furips.emit)
        menu_archivo.addAction(action_diligenciar)
        
        menu_archivo.addSeparator()
        
        action_salir = QAction("&Salir", self)
        action_salir.setShortcut("Ctrl+Q")
        action_salir.triggered.connect(self.accion_salir.emit)
        menu_archivo.addAction(action_salir)
        
        # Menú Exportar
        menu_exportar = menubar.addMenu("&Exportar")
        
        action_magneticos = QAction("FURIPS &Magnéticos", self)
        action_magneticos.triggered.connect(self.accion_exportar_magneticos.emit)
        menu_exportar.addAction(action_magneticos)
        
        action_pdf = QAction("&Imprimir FURIPS (PDF)", self)
        action_pdf.setShortcut("Ctrl+P")
        action_pdf.triggered.connect(self.accion_imprimir_pdf.emit)
        menu_exportar.addAction(action_pdf)
        
        # Menú Herramientas
        menu_herramientas = menubar.addMenu("&Herramientas")
        
        action_config = QAction("&Configuración", self)
        action_config.triggered.connect(self.accion_configuracion.emit)
        menu_herramientas.addAction(action_config)
    
    def _setup_statusbar(self):
        """Configura la barra de estado."""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage("Listo")
    
    def set_content(self, widget: QWidget):
        """Establece el contenido principal."""
        # Verificar si el widget ya está en el layout
        for i in range(self.content_area.count()):
            existing_widget = self.content_area.itemAt(i).widget()
            if existing_widget is widget:
                # El widget ya está mostrado, no hacer nada
                return
        
        # Limpiar contenido anterior (ocultar, no eliminar)
        while self.content_area.count():
            item = self.content_area.takeAt(0)
            if item.widget():
                item.widget().hide()
        
        # Agregar nuevo contenido
        self.content_area.addWidget(widget)
        widget.show()
    
    def mostrar_mensaje(self, titulo: str, mensaje: str, tipo: str = "info"):
        """Muestra un mensaje al usuario."""
        if tipo == "info":
            QMessageBox.information(self, titulo, mensaje)
        elif tipo == "warning":
            QMessageBox.warning(self, titulo, mensaje)
        elif tipo == "error":
            QMessageBox.critical(self, titulo, mensaje)
        elif tipo == "question":
            return QMessageBox.question(self, titulo, mensaje)
    
    def mostrar_estado(self, mensaje: str):
        """Muestra un mensaje en la barra de estado."""
        self.statusbar.showMessage(mensaje)
    
    def confirmar_salir(self) -> bool:
        """Confirma si el usuario desea salir."""
        respuesta = QMessageBox.question(
            self,
            "Confirmar salida",
            "¿Está seguro de que desea salir?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        return respuesta == QMessageBox.Yes
    
    def closeEvent(self, event):
        """Maneja el evento de cierre de ventana."""
        if self.confirmar_salir():
            self.accion_salir.emit()
            event.accept()
        else:
            event.ignore()
