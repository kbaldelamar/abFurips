"""
Repositorio para la entidad AccidenteConductor.
"""
from typing import Optional, List
from sqlalchemy.orm import Session, joinedload

from app.data.models import AccidenteConductor


class ConductorRepository:
    """Repositorio para gestionar conductores."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, conductor: AccidenteConductor) -> AccidenteConductor:
        """Crea un nuevo conductor."""
        self.session.add(conductor)
        self.session.flush()
        return conductor
    
    def delete(self, conductor_id: int):
        """Elimina un conductor (soft delete - cambia estado a 0)."""
        conductor = self.get_by_id(conductor_id)
        if conductor:
            conductor.estado = 0
            self.session.flush()
    
    def anular(self, conductor_id: int) -> bool:
        """Anula un conductor (soft delete - cambia estado a 0)."""
        conductor = self.get_by_id(conductor_id)
        if conductor:
            conductor.estado = 0
            self.session.flush()
            return True
        return False
    
    def reactivar(self, conductor_id: int) -> bool:
        """Reactiva un conductor anulado (cambia estado a 1)."""
        conductor = self.get_by_id(conductor_id)
        if conductor:
            conductor.estado = 1
            self.session.flush()
            return True
        return False
    
    def get_by_id(self, conductor_id: int) -> Optional[AccidenteConductor]:
        """Obtiene un conductor por ID con relaciones cargadas."""
        return (
            self.session.query(AccidenteConductor)
            .options(
                joinedload(AccidenteConductor.persona),
                joinedload(AccidenteConductor.accidente)
            )
            .filter(AccidenteConductor.id == conductor_id)
            .first()
        )
    
    def get_by_accidente(self, accidente_id: int) -> List[AccidenteConductor]:
        """Obtiene todos los conductores activos de un accidente (estado=1)."""
        return (
            self.session.query(AccidenteConductor)
            .options(joinedload(AccidenteConductor.persona))
            .filter(
                AccidenteConductor.accidente_id == accidente_id,
                AccidenteConductor.estado == 1
            )
            .all()
        )
    
    def get_by_persona_accidente(
        self, 
        persona_id: int, 
        accidente_id: int
    ) -> Optional[AccidenteConductor]:
        """Verifica si existe un conductor activo con esa persona en ese accidente (estado=1)."""
        return (
            self.session.query(AccidenteConductor)
            .filter(
                AccidenteConductor.persona_id == persona_id,
                AccidenteConductor.accidente_id == accidente_id,
                AccidenteConductor.estado == 1
            )
            .first()
        )
