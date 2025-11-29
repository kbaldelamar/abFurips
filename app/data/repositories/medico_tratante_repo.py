"""
Repositorio para AccidenteMedicoTratante.
"""
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload

from app.data.models.accidente_procesos import AccidenteMedicoTratante


class MedicoTratanteRepository:
    def __init__(self, session: Session):
        self.session = session
    
    def get_by_id(self, medico_id: int) -> Optional[AccidenteMedicoTratante]:
        """Obtiene un médico tratante por ID."""
        return (
            self.session.query(AccidenteMedicoTratante)
            .options(joinedload(AccidenteMedicoTratante.medico))
            .filter(AccidenteMedicoTratante.id == medico_id)
            .first()
        )
    
    def get_by_accidente(self, accidente_id: int) -> List[AccidenteMedicoTratante]:
        """Obtiene todos los médicos tratantes de un accidente activos."""
        return (
            self.session.query(AccidenteMedicoTratante)
            .options(
                joinedload(AccidenteMedicoTratante.medico),
                joinedload(AccidenteMedicoTratante.victima)
            )
            .filter(
                AccidenteMedicoTratante.accidente_id == accidente_id,
                AccidenteMedicoTratante.estado == "activo"
            )
            .all()
        )
    
    def get_by_victima(self, victima_id: int) -> Optional[AccidenteMedicoTratante]:
        """Obtiene el médico tratante de una víctima específica."""
        return (
            self.session.query(AccidenteMedicoTratante)
            .options(joinedload(AccidenteMedicoTratante.medico))
            .filter(
                AccidenteMedicoTratante.accidente_victima_id == victima_id,
                AccidenteMedicoTratante.estado == "activo"
            )
            .first()
        )
    
    def create(self, medico_tratante: AccidenteMedicoTratante) -> AccidenteMedicoTratante:
        """Crea un nuevo médico tratante."""
        self.session.add(medico_tratante)
        self.session.flush()
        return medico_tratante
    
    def update(self, medico_tratante: AccidenteMedicoTratante) -> AccidenteMedicoTratante:
        """Actualiza un médico tratante existente."""
        self.session.flush()
        return medico_tratante
    
    def anular(self, medico_id: int) -> bool:
        """Anula un médico tratante (soft delete)."""
        medico = self.get_by_id(medico_id)
        if medico:
            medico.estado = "inactivo"
            self.session.flush()
            return True
        return False
