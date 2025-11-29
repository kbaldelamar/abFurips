"""
Modelo de Persona.
"""
from datetime import date, datetime

from sqlalchemy import Column, BigInteger, Integer, String, Date, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship

from app.data.models.base import Base


class Persona(Base):
    __tablename__ = "persona"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="PK persona")
    tipo_identificacion_id = Column(Integer, ForeignKey("tipo_identificacion.id"), nullable=False, comment="FK tipo_identificacion")
    numero_identificacion = Column(String(20), nullable=False, comment="Número de documento")
    primer_nombre = Column(String(30), nullable=False, comment="Primer nombre")
    segundo_nombre = Column(String(30), nullable=True, comment="Segundo nombre")
    primer_apellido = Column(String(30), nullable=False, comment="Primer apellido")
    segundo_apellido = Column(String(30), nullable=True, comment="Segundo apellido")
    sexo_id = Column(Integer, ForeignKey("sexo.id"), nullable=False, comment="FK sexo")
    fecha_nacimiento = Column(Date, nullable=False, comment="Fecha de nacimiento")
    fecha_fallecimiento = Column(Date, nullable=True, comment="Fecha de fallecimiento (si aplica)")
    direccion = Column(String(200), nullable=False, comment="Dirección de residencia")
    telefono = Column(String(15), nullable=False, comment="Teléfono de contacto")
    municipio_residencia_id = Column(Integer, ForeignKey("municipio.id"), nullable=False, comment="FK municipio de residencia")
    fecha_registro = Column(DateTime, nullable=False, default=datetime.now, comment="Fecha de creación del registro")
    estado = Column(Integer, nullable=False, default=1, comment="1 activo, 0 inactivo")
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "(fecha_fallecimiento IS NULL) OR (fecha_fallecimiento >= fecha_nacimiento)",
            name="chk_persona_fallecimiento"
        ),
    )
    
    # Relaciones
    tipo_identificacion = relationship("TipoIdentificacion", back_populates="personas")
    sexo = relationship("Sexo", back_populates="personas")
    municipio_residencia = relationship("Municipio", back_populates="personas", foreign_keys=[municipio_residencia_id])
    
    # Roles en accidentes
    como_victima = relationship("AccidenteVictima", back_populates="persona")
    como_conductor = relationship("AccidenteConductor", back_populates="persona")
    como_propietario = relationship("AccidentePropietario", back_populates="persona")
    vehiculos_propietario = relationship("Vehiculo", back_populates="propietario")
    
    # Configuración adicional
    config = relationship("PersonaConfig", back_populates="persona", uselist=False)
    
    @property
    def nombre_completo(self) -> str:
        """Retorna el nombre completo de la persona."""
        partes = [
            self.primer_nombre,
            self.segundo_nombre,
            self.primer_apellido,
            self.segundo_apellido
        ]
        return " ".join([p for p in partes if p])
    
    def __repr__(self) -> str:
        return f"<Persona(id={self.id}, nombre='{self.nombre_completo}', doc='{self.numero_identificacion}')>"
