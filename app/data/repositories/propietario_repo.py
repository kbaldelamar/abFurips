"""
Repositorio para la entidad AccidentePropietario.
"""
from typing import Optional, List
from sqlalchemy.orm import Session, joinedload

from app.data.models import AccidentePropietario


class PropietarioRepository:
    """Repositorio para gestionar propietarios."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, propietario: AccidentePropietario) -> AccidentePropietario:
        """Crea un nuevo propietario."""
        self.session.add(propietario)
        self.session.flush()
        return propietario
    
    def delete(self, propietario_id: int):
        """Elimina un propietario (soft delete - cambia estado a 0)."""
        propietario = self.get_by_id(propietario_id)
        if propietario:
            propietario.estado = 0
            self.session.flush()
    
    def anular(self, propietario_id: int) -> bool:
        """Anula un propietario (soft delete - cambia estado a 0)."""
        propietario = self.get_by_id(propietario_id)
        if propietario:
            propietario.estado = 0
            self.session.flush()
            return True
        return False
    
    def reactivar(self, propietario_id: int) -> bool:
        """Reactiva un propietario anulado (cambia estado a 1)."""
        propietario = self.get_by_id(propietario_id)
        if propietario:
            propietario.estado = 1
            self.session.flush()
            return True
        return False
    
    def get_by_id(self, propietario_id: int) -> Optional[AccidentePropietario]:
        """Obtiene un propietario por ID con relaciones cargadas."""
        return (
            self.session.query(AccidentePropietario)
            .options(
                joinedload(AccidentePropietario.persona),
                joinedload(AccidentePropietario.accidente)
            )
            .filter(AccidentePropietario.id == propietario_id)
            .first()
        )
    
    def get_by_accidente(self, accidente_id: int) -> List[AccidentePropietario]:
        """Obtiene todos los propietarios activos de un accidente (estado=1)."""
        return (
            self.session.query(AccidentePropietario)
            .options(joinedload(AccidentePropietario.persona))
            .filter(
                AccidentePropietario.accidente_id == accidente_id,
                AccidentePropietario.estado == 1
            )
            .all()
        )
    
    def get_by_persona_accidente(
        self, 
        persona_id: int, 
        accidente_id: int
    ) -> Optional[AccidentePropietario]:
        """Verifica si existe un propietario activo con esa persona en ese accidente (estado=1)."""
        return (
            self.session.query(AccidentePropietario)
            .filter(
                AccidentePropietario.persona_id == persona_id,
                AccidentePropietario.accidente_id == accidente_id,
                AccidentePropietario.estado == 1
            )
            .first()
        )
