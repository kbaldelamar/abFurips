"""
Repositorio para la entidad AccidenteVictima.
"""
from typing import Optional, List
from sqlalchemy.orm import Session, joinedload

from app.data.models import AccidenteVictima


class VictimaRepository:
    """Repositorio para gestionar víctimas."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, victima: AccidenteVictima) -> AccidenteVictima:
        """Crea una nueva víctima."""
        self.session.add(victima)
        self.session.flush()
        return victima
    
    def delete(self, victima_id: int):
        """Elimina una víctima (soft delete - cambia estado a 0)."""
        victima = self.get_by_id(victima_id)
        if victima:
            victima.estado = 0
            self.session.flush()
    
    def anular(self, victima_id: int) -> bool:
        """Anula una víctima (soft delete - cambia estado a 0)."""
        victima = self.get_by_id(victima_id)
        if victima:
            victima.estado = 0
            self.session.flush()
            return True
        return False
    
    def reactivar(self, victima_id: int) -> bool:
        """Reactiva una víctima anulada (cambia estado a 1)."""
        victima = self.get_by_id(victima_id)
        if victima:
            victima.estado = 1
            self.session.flush()
            return True
        return False
    
    def get_by_id(self, victima_id: int) -> Optional[AccidenteVictima]:
        """Obtiene una víctima por ID con relaciones cargadas."""
        from app.data.models import Persona, TipoIdentificacion, Sexo
        return (
            self.session.query(AccidenteVictima)
            .options(
                joinedload(AccidenteVictima.persona).joinedload(Persona.tipo_identificacion),
                joinedload(AccidenteVictima.persona).joinedload(Persona.sexo),
                joinedload(AccidenteVictima.accidente)
            )
            .filter(AccidenteVictima.id == victima_id)
            .first()
        )
    
    def get_by_accidente(self, accidente_id: int) -> List[AccidenteVictima]:
        """Obtiene todas las víctimas activas de un accidente (estado=1)."""
        from app.data.models import Persona, TipoIdentificacion, Sexo
        return (
            self.session.query(AccidenteVictima)
            .options(
                joinedload(AccidenteVictima.persona).joinedload(Persona.tipo_identificacion),
                joinedload(AccidenteVictima.persona).joinedload(Persona.sexo)
            )
            .filter(
                AccidenteVictima.accidente_id == accidente_id,
                AccidenteVictima.estado == 1
            )
            .all()
        )
    
    def get_by_persona_accidente(
        self, 
        persona_id: int, 
        accidente_id: int
    ) -> Optional[AccidenteVictima]:
        """Verifica si existe una víctima activa con esa persona en ese accidente (estado=1)."""
        return (
            self.session.query(AccidenteVictima)
            .filter(
                AccidenteVictima.persona_id == persona_id,
                AccidenteVictima.accidente_id == accidente_id,
                AccidenteVictima.estado == 1
            )
            .first()
        )
