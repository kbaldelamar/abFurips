"""
Presenter principal de la aplicación (patrón MVP).
"""
from PySide6.QtCore import QObject

from app.ui.views import MainWindow, AccidenteForm
from app.ui.views.buscar_imprimir_dialog import BuscarImprimirDialog
from PySide6.QtWidgets import QMessageBox
from app.ui.presenters.accidente_presenter import AccidentePresenter
from app.domain.services.print_service import PrintService


class MainPresenter(QObject):
    """Presenter principal que orquesta la aplicación."""
    
    def __init__(self, main_window: MainWindow):
        super().__init__()
        self.view = main_window
        
        # Presenters hijos
        self.accidente_presenter = None
        
        # Conectar señales
        self._connect_signals()
    
    def _connect_signals(self):
        """Conecta las señales de la vista."""
        self.view.accion_diligenciar_furips.connect(self.mostrar_diligenciar_furips)
        self.view.accion_exportar_magneticos.connect(self.mostrar_exportar_magneticos)
        self.view.accion_imprimir_pdf.connect(self.mostrar_imprimir_pdf)
        self.view.accion_configuracion.connect(self.mostrar_configuracion)
        self.view.accion_salir.connect(self.salir_aplicacion)
    
    def mostrar_diligenciar_furips(self):
        """Muestra el formulario para diligenciar FURIPS."""
        if self.accidente_presenter is None:
            # Crear vista y presenter
            accidente_form = AccidenteForm()
            self.accidente_presenter = AccidentePresenter(accidente_form)
        
        self.view.set_content(self.accidente_presenter.view)
        self.view.mostrar_estado("Diligenciando FURIPS")
    
    def mostrar_exportar_magneticos(self):
        """Muestra el diálogo para exportar archivos magnéticos."""
        # TODO: Implementar
        self.view.mostrar_mensaje(
            "Exportar Magnéticos",
            "Funcionalidad en desarrollo",
            "info"
        )
    
    def mostrar_imprimir_pdf(self):
        """Muestra el diálogo para imprimir PDFs."""
        # Mostrar el panel de búsqueda/imprimir embebido en la ventana principal
        self.imprimir_panel = BuscarImprimirDialog(self.view)
        self.imprimir_panel.imprimir_accidente.connect(self._on_imprimir_accidente)
        self.view.set_content(self.imprimir_panel)

    def _on_imprimir_accidente(self, accidente_id: int):
        # Invocar el servicio de generación de PDF (sin bloquear UI por mucho tiempo)
        try:
            self.view.mostrar_estado(f"Generando PDF para accidente {accidente_id}...")
            svc = PrintService()
            # Generar PDF usando la consulta CTE (rellena DTO desde una sola consulta)
            output = svc.generar_pdf_accidente(accidente_id, tipo="furips_cte")
            self.view.mostrar_estado(f"PDF generado: {output}")
            QMessageBox.information(self.view, "Imprimir", f"PDF generado: {output}")
        except Exception as e:
            QMessageBox.critical(self.view, "Error impresión", f"No se pudo generar el PDF: {e}")
    
    def mostrar_configuracion(self):
        """Muestra el diálogo de configuración."""
        # TODO: Implementar
        self.view.mostrar_mensaje(
            "Configuración",
            "Funcionalidad en desarrollo",
            "info"
        )
    
    def salir_aplicacion(self):
        """Cierra la aplicación."""
        self.view.close()
