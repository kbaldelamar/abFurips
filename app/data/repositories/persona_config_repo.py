"""
Repositorio para PersonaConfig.
"""
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload

from app.data.models.persona_config import PersonaConfig


class PersonaConfigRepository:
    def __init__(self, session: Session):
        self.session = session
    
    def get_by_id(self, config_id: int) -> Optional[PersonaConfig]:
        """Obtiene una configuración por ID."""
        return (
            self.session.query(PersonaConfig)
            .options(joinedload(PersonaConfig.persona))
            .filter(PersonaConfig.id == config_id)
            .first()
        )
    
    def get_by_persona(self, persona_id: int) -> Optional[PersonaConfig]:
        """Obtiene la configuración de una persona."""
        return (
            self.session.query(PersonaConfig)
            .filter(PersonaConfig.persona_id == persona_id)
            .first()
        )
    
    def get_medicos_activos(self) -> List[PersonaConfig]:
        """Obtiene todas las personas configuradas como médicos activos."""
        return (
            self.session.query(PersonaConfig)
            .options(joinedload(PersonaConfig.persona))
            .filter(
                PersonaConfig.es_medico == True,
                PersonaConfig.estado == 1
            )
            .order_by(PersonaConfig.persona.has())
            .all()
        )
    
    def create(self, config: PersonaConfig) -> PersonaConfig:
        """Crea una nueva configuración."""
        self.session.add(config)
        self.session.flush()
        return config
    
    def update(self, config: PersonaConfig) -> PersonaConfig:
        """Actualiza una configuración existente."""
        self.session.flush()
        return config
