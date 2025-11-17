"""
Presenter para el formulario de detalle (patrón MVP).
"""
from PySide6.QtCore import QObject

from app.ui.views import DetalleForm
from app.config import get_db_session
from app.data.repositories import DetalleRepository
from app.domain.services import AccidenteService
from app.domain.dto import DetalleDTO


class DetallePresenter(QObject):
    """Presenter para el formulario de detalle."""
    
    def __init__(self, view: DetalleForm, accidente_id: int):
        super().__init__()
        self.view = view
        self.accidente_id = accidente_id
        
        # Conectar señales
        self._connect_signals()
        
        # Cargar detalles existentes
        self._cargar_detalles()
    
    def _connect_signals(self):
        """Conecta las señales de la vista."""
        self.view.agregar_detalle_signal.connect(self.agregar_detalle)
        self.view.editar_detalle_signal.connect(self.editar_detalle)
        self.view.eliminar_detalle_signal.connect(self.eliminar_detalle)
    
    def _cargar_detalles(self):
        """Carga los detalles del accidente."""
        try:
            with get_db_session() as session:
                detalle_repo = DetalleRepository(session)
                detalles = detalle_repo.get_by_accidente(self.accidente_id)
                
                detalles_data = [
                    {
                        "tipo_servicio": d.tipo_servicio.descripcion,
                        "codigo_servicio": d.codigo_servicio or "",
                        "descripcion": d.descripcion or "",
                        "cantidad": d.cantidad,
                        "valor_unitario": d.valor_unitario,
                        "valor_facturado": d.valor_facturado,
                        "valor_reclamado": d.valor_reclamado,
                    }
                    for d in detalles
                ]
                
                self.view.cargar_detalles(detalles_data)
        
        except Exception as e:
            print(f"Error cargando detalles: {e}")
    
    def agregar_detalle(self):
        """Abre el diálogo para agregar un detalle."""
        # TODO: Implementar diálogo
        print("Agregar detalle")
    
    def editar_detalle(self, row: int):
        """Edita un detalle existente."""
        # TODO: Implementar
        print(f"Editar detalle en fila {row}")
    
    def eliminar_detalle(self, row: int):
        """Elimina un detalle."""
        # TODO: Implementar
        print(f"Eliminar detalle en fila {row}")
