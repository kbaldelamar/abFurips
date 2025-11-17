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
        """Elimina un conductor."""
        conductor = self.get_by_id(conductor_id)
        if conductor:
            self.session.delete(conductor)
    
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
        """Obtiene todos los conductores de un accidente."""
        return (
            self.session.query(AccidenteConductor)
            .options(joinedload(AccidenteConductor.persona))
            .filter(AccidenteConductor.accidente_id == accidente_id)
            .all()
        )
    
    def get_by_persona_accidente(
        self, 
        persona_id: int, 
        accidente_id: int
    ) -> Optional[AccidenteConductor]:
        """Verifica si existe un conductor con esa persona en ese accidente."""
        return (
            self.session.query(AccidenteConductor)
            .filter(
                AccidenteConductor.persona_id == persona_id,
                AccidenteConductor.accidente_id == accidente_id
            )
            .first()
        )
