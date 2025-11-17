"""
Modelos de tablas de catálogo/maestros.
"""
from sqlalchemy import Column, Integer, String, SmallInteger, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship

from app.data.models.base import Base


# ============================================================================
# GEOGRAFÍA
# ============================================================================
class Pais(Base):
    __tablename__ = "pais"
    
    id = Column(SmallInteger, primary_key=True, autoincrement=True, comment="PK país")
    codigo = Column(String(3), unique=True, nullable=False, comment="Código ISO u homólogo")
    nombre = Column(String(60), nullable=False, comment="Nombre del país")
    estado = Column(Boolean, nullable=False, default=True, comment="1 activo, 0 inactivo")
    
    # Relaciones
    departamentos = relationship("Departamento", back_populates="pais")


class Departamento(Base):
    __tablename__ = "departamento"
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="PK departamento")
    pais_id = Column(SmallInteger, ForeignKey("pais.id"), nullable=False, comment="FK a pais.id")
    codigo = Column(String(3), nullable=False, comment="Código interno/DANE depto")
    nombre = Column(String(60), nullable=False, comment="Nombre del departamento")
    estado = Column(Boolean, nullable=False, default=True, comment="1 activo, 0 inactivo")
    
    # Relaciones
    pais = relationship("Pais", back_populates="departamentos")
    municipios = relationship("Municipio", back_populates="departamento")


class Municipio(Base):
    __tablename__ = "municipio"
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="PK municipio")
    departamento_id = Column(Integer, ForeignKey("departamento.id"), nullable=False, comment="FK a departamento.id")
    codigo_dane = Column(String(5), nullable=False, comment="Código DANE municipio")
    codigo_postal = Column(String(6), nullable=True, comment="Código postal")
    nombre = Column(String(80), nullable=False, comment="Nombre del municipio")
    estado = Column(Boolean, nullable=False, default=True, comment="1 activo, 0 inactivo")
    
    # Relaciones
    departamento = relationship("Departamento", back_populates="municipios")
    personas = relationship("Persona", back_populates="municipio_residencia", foreign_keys="Persona.municipio_residencia_id")
    prestadores = relationship("PrestadorSalud", back_populates="municipio")
    accidentes = relationship("Accidente", back_populates="municipio_evento")


# ============================================================================
# PERSONA / IDENTIFICACIÓN
# ============================================================================
class TipoIdentificacion(Base):
    __tablename__ = "tipo_identificacion"
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="PK tipo de identificación")
    codigo = Column(String(2), unique=True, nullable=False, comment="Código (CC, CE, etc.)")
    descripcion = Column(String(50), nullable=False, comment="Descripción del tipo de documento")
    
    # Relaciones
    personas = relationship("Persona", back_populates="tipo_identificacion")


class Sexo(Base):
    __tablename__ = "sexo"
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="PK sexo")
    codigo = Column(String(1), unique=True, nullable=False, comment="F, M, O")
    descripcion = Column(String(15), nullable=False, comment="Descripción del sexo")
    
    # Relaciones
    personas = relationship("Persona", back_populates="sexo")


# ============================================================================
# EVENTO / ACCIDENTE
# ============================================================================
class NaturalezaEvento(Base):
    __tablename__ = "naturaleza_evento"
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="PK naturaleza del evento")
    codigo = Column(String(2), unique=True, nullable=False, comment="01..27 según circular")
    descripcion = Column(String(60), nullable=False, comment="Descripción de la naturaleza")
    
    # Relaciones
    accidentes = relationship("Accidente", back_populates="naturaleza_evento")


class EstadoAseguramiento(Base):
    __tablename__ = "estado_aseguramiento"
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="PK estado de aseguramiento")
    codigo = Column(String(1), unique=True, nullable=False, comment="1,2,3,4,6,7,8 según circular")
    descripcion = Column(String(60), nullable=False, comment="Descripción del estado de aseguramiento")
    
    # Relaciones
    accidentes = relationship("Accidente", back_populates="estado_aseguramiento")
    vehiculos = relationship("Vehiculo", back_populates="estado_aseguramiento")


# ============================================================================
# VEHÍCULO
# ============================================================================
class TipoVehiculo(Base):
    __tablename__ = "tipo_vehiculo"
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="PK tipo de vehículo")
    codigo = Column(String(2), unique=True, nullable=False, comment="Código de tipo de vehículo")
    descripcion = Column(String(40), nullable=False, comment="Descripción del tipo de vehículo")
    
    # Relaciones
    vehiculos = relationship("Vehiculo", back_populates="tipo_vehiculo")


# ============================================================================
# SERVICIOS
# ============================================================================
class TipoServicio(Base):
    __tablename__ = "tipo_servicio"
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="PK tipo de servicio FURIPS2")
    codigo = Column(String(1), unique=True, nullable=False, comment="1..8 tipos de servicio")
    descripcion = Column(String(40), nullable=False, comment="Descripción del tipo de servicio")
    
    # Relaciones
    detalles = relationship("AccidenteDetalle", back_populates="tipo_servicio")
