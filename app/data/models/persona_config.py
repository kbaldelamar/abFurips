"""
Modelo de PersonaConfig.
"""
from sqlalchemy import Column, BigInteger, Integer, String, Boolean, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.data.models.base import Base


class PersonaConfig(Base):
    __tablename__ = "persona_config"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    persona_id = Column(BigInteger, ForeignKey("persona.id"), nullable=False, unique=True)
    es_medico = Column(Boolean, nullable=False, default=False)
    registro_medico = Column(String(30), nullable=True, comment="Registro médico")
    especialidad = Column(String(80), nullable=True, comment="Especialidad médica")
    estado = Column(Integer, nullable=False, default=1, comment="1 activo, 0 inactivo")
    creado_en = Column(TIMESTAMP, server_default=func.current_timestamp())
    actualizado_en = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    # Relaciones
    persona = relationship("Persona", back_populates="config")
    
    def __repr__(self) -> str:
        return f"<PersonaConfig(id={self.id}, persona_id={self.persona_id}, es_medico={self.es_medico})>"
