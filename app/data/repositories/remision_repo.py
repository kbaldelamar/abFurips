"""
Repositorio para AccidenteRemision.
"""
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload

from app.data.models.accidente_procesos import AccidenteRemision


class RemisionRepository:
    def __init__(self, session: Session):
        self.session = session
    
    def get_by_id(self, remision_id: int) -> Optional[AccidenteRemision]:
        """Obtiene una remisión por ID."""
        return (
            self.session.query(AccidenteRemision)
            .options(
                joinedload(AccidenteRemision.persona_remite),
                joinedload(AccidenteRemision.persona_recibe)
            )
            .filter(AccidenteRemision.id == remision_id)
            .first()
        )
    
    def get_by_accidente(self, accidente_id: int) -> List[AccidenteRemision]:
        """Obtiene todas las remisiones de un accidente activas."""
        return (
            self.session.query(AccidenteRemision)
            .options(
                joinedload(AccidenteRemision.persona_remite),
                joinedload(AccidenteRemision.persona_recibe)
            )
            .filter(
                AccidenteRemision.accidente_id == accidente_id,
                AccidenteRemision.estado == "activo"
            )
            .all()
        )
    
    def create(self, remision: AccidenteRemision) -> AccidenteRemision:
        """Crea una nueva remisión."""
        self.session.add(remision)
        self.session.flush()
        return remision
    
    def update(self, remision: AccidenteRemision) -> AccidenteRemision:
        """Actualiza una remisión existente."""
        self.session.flush()
        return remision
    
    def anular(self, remision_id: int) -> bool:
        """Anula una remisión (soft delete)."""
        remision = self.get_by_id(remision_id)
        if remision:
            remision.estado = "inactivo"
            self.session.flush()
            return True
        return False
    
    def delete_by_accidente(self, accidente_id: int) -> int:
        """Elimina todas las remisiones de un accidente."""
        count = (
            self.session.query(AccidenteRemision)
            .filter(AccidenteRemision.accidente_id == accidente_id)
            .delete()
        )
        self.session.flush()
        return count
