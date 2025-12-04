"""
Repositorio para gestión de AccidenteDetalle.
"""
from typing import List

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.data.models import AccidenteDetalle


class DetalleRepository:
    """Repositorio para operaciones con AccidenteDetalle."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_by_accidente(self, accidente_id: int) -> List[AccidenteDetalle]:
        """Obtiene todos los detalles de un accidente."""
        print(f"📊 DetalleRepository.get_by_accidente() - Filtrando por accidente_id={accidente_id}")
        query = (
            self.session.query(AccidenteDetalle)
            .options(
                joinedload(AccidenteDetalle.tipo_servicio),
                joinedload(AccidenteDetalle.procedimiento),
            )
            .filter(AccidenteDetalle.accidente_id == accidente_id)
            .order_by(AccidenteDetalle.id)
        )
        
        # Log del SQL generado
        print(f"🔍 SQL Query: {query}")
        
        result = query.all()
        print(f"📦 Resultado: {len(result)} registros encontrados")
        
        return result
    
    def create(self, detalle: AccidenteDetalle) -> AccidenteDetalle:
        """Crea un nuevo detalle."""
        self.session.add(detalle)
        self.session.flush()
        self.session.refresh(detalle)
        return detalle
    
    def create_bulk(self, detalles: List[AccidenteDetalle]) -> List[AccidenteDetalle]:
        """Crea múltiples detalles en lote."""
        self.session.add_all(detalles)
        self.session.flush()
        for detalle in detalles:
            self.session.refresh(detalle)
        return detalles
    
    def update(self, detalle: AccidenteDetalle) -> AccidenteDetalle:
        """Actualiza un detalle existente."""
        self.session.add(detalle)
        self.session.flush()
        self.session.refresh(detalle)
        return detalle
    
    def delete(self, detalle_id: int) -> bool:
        """Elimina un detalle por ID."""
        detalle = self.session.query(AccidenteDetalle).filter(AccidenteDetalle.id == detalle_id).first()
        if detalle:
            self.session.delete(detalle)
            self.session.flush()
            return True
        return False
    
    def delete_by_accidente(self, accidente_id: int) -> int:
        """Elimina todos los detalles de un accidente. Retorna cantidad eliminada."""
        count = (
            self.session.query(AccidenteDetalle)
            .filter(AccidenteDetalle.accidente_id == accidente_id)
            .delete()
        )
        self.session.flush()
        return count
    
    def calcular_totales_gmq(self, accidente_id: int) -> dict:
        """
        Calcula totales de gastos médico-quirúrgicos (tipos 1, 2, 5, 6, 7, 8).
        Retorna dict con total_facturado y total_reclamado.
        """
        result = (
            self.session.query(
                func.sum(AccidenteDetalle.valor_facturado).label("total_facturado"),
                func.sum(AccidenteDetalle.valor_reclamado).label("total_reclamado"),
            )
            .filter(
                AccidenteDetalle.accidente_id == accidente_id,
                AccidenteDetalle.tipo_servicio_id.in_([1, 2, 5, 6, 7, 8]),
            )
            .first()
        )
        
        return {
            "total_facturado": result.total_facturado or 0,
            "total_reclamado": result.total_reclamado or 0,
        }
    
    def calcular_totales_transporte(self, accidente_id: int) -> dict:
        """
        Calcula totales de transporte primario (tipo 3).
        Retorna dict con total_facturado y total_reclamado.
        """
        result = (
            self.session.query(
                func.sum(AccidenteDetalle.valor_facturado).label("total_facturado"),
                func.sum(AccidenteDetalle.valor_reclamado).label("total_reclamado"),
            )
            .filter(
                AccidenteDetalle.accidente_id == accidente_id,
                AccidenteDetalle.tipo_servicio_id == 3,
            )
            .first()
        )
        
        return {
            "total_facturado": result.total_facturado or 0,
            "total_reclamado": result.total_reclamado or 0,
        }
