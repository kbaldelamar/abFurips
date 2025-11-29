"""
Modelo de Accidente (encabezado FURIPS1).
"""
from datetime import date, time

from sqlalchemy import Column, BigInteger, Integer, String, Date, Time, ForeignKey, Enum
from sqlalchemy.orm import relationship

from app.data.models.base import Base


class Accidente(Base):
    __tablename__ = "accidente"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="PK accidente/evento")
    prestador_id = Column(BigInteger, ForeignKey("prestador_salud.id"), nullable=False, comment="FK prestador que radica")
    numero_consecutivo = Column(String(12), nullable=False, comment="Consecutivo único por prestador")
    numero_factura = Column(String(20), nullable=False, comment="Número de factura")
    numero_rad_siras = Column(String(20), nullable=False, comment="Radicado SIRAS")
    naturaleza_evento_id = Column(Integer, ForeignKey("naturaleza_evento.id"), nullable=False, comment="FK naturaleza del evento")
    descripcion_otro_evento = Column(String(25), nullable=True, comment="Descripción si la naturaleza es 'otro'")
    fecha_evento = Column(Date, nullable=False, comment="Fecha del evento")
    hora_evento = Column(Time, nullable=False, comment="Hora del evento")
    municipio_evento_id = Column(Integer, ForeignKey("municipio.id"), nullable=False, comment="FK municipio del evento")
    direccion_evento = Column(String(200), nullable=False, comment="Dirección de ocurrencia")
    descripcion = Column(String, nullable=True, comment="Descripción del evento")
    zona = Column(Enum("U", "R", name="zona_evento"), nullable=True, comment="Zona urbana/rural")
    vehiculo_id = Column(BigInteger, ForeignKey("vehiculo.id"), nullable=True, comment="FK vehículo involucrado")
    estado_aseguramiento_id = Column(Integer, ForeignKey("estado_aseguramiento.id"), nullable=False, comment="FK estado del aseguramiento")
    estado = Column(Integer, nullable=False, default=1, comment="1 activo, 0 inactivo")
    
    # Relaciones
    prestador = relationship("PrestadorSalud", back_populates="accidentes")
    naturaleza_evento = relationship("NaturalezaEvento", back_populates="accidentes")
    municipio_evento = relationship("Municipio", back_populates="accidentes")
    vehiculo = relationship("Vehiculo", back_populates="accidentes")
    estado_aseguramiento = relationship("EstadoAseguramiento", back_populates="accidentes")
    
    # Vínculos con personas
    victimas = relationship("AccidenteVictima", back_populates="accidente", cascade="all, delete-orphan")
    conductores = relationship("AccidenteConductor", back_populates="accidente", cascade="all, delete-orphan")
    propietarios = relationship("AccidentePropietario", back_populates="accidente", cascade="all, delete-orphan")
    
    # Detalle FURIPS2
    detalles = relationship("AccidenteDetalle", back_populates="accidente", cascade="all, delete-orphan")
    
    # Totales FURIPS1
    totales = relationship("AccidenteTotales", back_populates="accidente", uselist=False, cascade="all, delete-orphan")
    
    # Médicos tratantes y remisiones
    medicos_tratantes = relationship("AccidenteMedicoTratante", back_populates="accidente", cascade="all, delete-orphan")
    remisiones = relationship("AccidenteRemision", back_populates="accidente", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Accidente(id={self.id}, consecutivo='{self.numero_consecutivo}', fecha='{self.fecha_evento}')>"


# ============================================================================
# VÍCTIMA
# ============================================================================
class AccidenteVictima(Base):
    __tablename__ = "accidente_victima"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="PK víctima del accidente")
    accidente_id = Column(BigInteger, ForeignKey("accidente.id"), nullable=False, comment="FK accidente")
    persona_id = Column(BigInteger, ForeignKey("persona.id"), nullable=False, comment="FK persona víctima")
    condicion_codigo = Column(String(1), nullable=True, comment="1 conductor, 2 peatón, 3 ocupante, 4 ciclista")
    estado = Column(Integer, nullable=False, default=1, comment="1 activo, 0 inactivo")
    
    # Relaciones
    accidente = relationship("Accidente", back_populates="victimas")
    persona = relationship("Persona", back_populates="como_victima")
    medico_tratante = relationship("AccidenteMedicoTratante", back_populates="victima", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<AccidenteVictima(id={self.id}, accidente_id={self.accidente_id}, persona_id={self.persona_id})>"


# ============================================================================
# CONDUCTOR
# ============================================================================
class AccidenteConductor(Base):
    __tablename__ = "accidente_conductor"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="PK conductor vinculado")
    accidente_id = Column(BigInteger, ForeignKey("accidente.id"), nullable=False, comment="FK accidente")
    persona_id = Column(BigInteger, ForeignKey("persona.id"), nullable=False, comment="FK persona conductor")
    estado = Column(Integer, nullable=False, default=1, comment="1 activo, 0 inactivo")
    
    # Relaciones
    accidente = relationship("Accidente", back_populates="conductores")
    persona = relationship("Persona", back_populates="como_conductor")
    
    def __repr__(self) -> str:
        return f"<AccidenteConductor(id={self.id}, accidente_id={self.accidente_id}, persona_id={self.persona_id})>"


# ============================================================================
# PROPIETARIO
# ============================================================================
class AccidentePropietario(Base):
    __tablename__ = "accidente_propietario"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="PK propietario vinculado")
    accidente_id = Column(BigInteger, ForeignKey("accidente.id"), nullable=False, comment="FK accidente")
    persona_id = Column(BigInteger, ForeignKey("persona.id"), nullable=False, comment="FK persona propietaria")
    estado = Column(Integer, nullable=False, default=1, comment="1 activo, 0 inactivo")
    
    # Relaciones
    accidente = relationship("Accidente", back_populates="propietarios")
    persona = relationship("Persona", back_populates="como_propietario")
    
    def __repr__(self) -> str:
        return f"<AccidentePropietario(id={self.id}, accidente_id={self.accidente_id}, persona_id={self.persona_id})>"
