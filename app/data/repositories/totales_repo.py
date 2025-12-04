"""
Repositorio para gestión de AccidenteTotales.
"""
from typing import Optional

from sqlalchemy.orm import Session

from app.data.models import AccidenteTotales


class TotalesRepository:
    """Repositorio para operaciones con AccidenteTotales."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_by_accidente(self, accidente_id: int) -> Optional[AccidenteTotales]:
        """Obtiene los totales de un accidente."""
        return (
            self.session.query(AccidenteTotales)
            .filter(AccidenteTotales.accidente_id == accidente_id)
            .first()
        )
    
    def create(self, totales: AccidenteTotales) -> AccidenteTotales:
        """Crea un nuevo registro de totales."""
        self.session.add(totales)
        self.session.flush()
        self.session.refresh(totales)
        return totales
    
    def update(self, totales: AccidenteTotales) -> AccidenteTotales:
        """Actualiza un registro de totales existente."""
        self.session.add(totales)
        self.session.flush()
        self.session.refresh(totales)
        return totales
    
    def delete(self, accidente_id: int) -> bool:
        """Elimina los totales de un accidente."""
        totales = self.get_by_accidente(accidente_id)
        if totales:
            self.session.delete(totales)
            self.session.flush()
            return True
        return False
    
    def create_or_update(self, totales: AccidenteTotales) -> AccidenteTotales:
        """Crea o actualiza totales según si existen o no."""
        existente = self.get_by_accidente(totales.accidente_id)
        
        if existente:
            # Actualizar existente
            existente.total_facturado_gmq = totales.total_facturado_gmq
            existente.total_reclamado_gmq = totales.total_reclamado_gmq
            existente.total_facturado_transporte = totales.total_facturado_transporte
            existente.total_reclamado_transporte = totales.total_reclamado_transporte
            existente.manifestacion_servicios = totales.manifestacion_servicios
            existente.descripcion_evento = totales.descripcion_evento
            return self.update(existente)
        else:
            # Crear nuevo
            return self.create(totales)
