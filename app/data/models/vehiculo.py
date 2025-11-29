"""
Modelos de Vehículo y Procedimiento.
"""
from sqlalchemy import Column, BigInteger, Integer, String, Date, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship

from app.data.models.base import Base


# ============================================================================
# VEHÍCULO
# ============================================================================
class Vehiculo(Base):
    __tablename__ = "vehiculo"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="PK vehículo")
    placa = Column(String(10), unique=True, nullable=True, comment="Placa del vehículo")
    marca = Column(String(30), nullable=True, comment="Marca del vehículo")
    tipo_vehiculo_id = Column(Integer, ForeignKey("tipo_vehiculo.id"), nullable=True, comment="FK tipo de vehículo")
    aseguradora_codigo = Column(String(6), nullable=True, comment="Código de aseguradora (AT)")
    numero_poliza = Column(String(20), nullable=True, comment="Número de póliza SOAT")
    vigencia_inicio = Column(Date, nullable=True, comment="Inicio vigencia póliza")
    vigencia_fin = Column(Date, nullable=True, comment="Fin vigencia póliza")
    estado_aseguramiento_id = Column(Integer, ForeignKey("estado_aseguramiento.id"), nullable=False, comment="FK estado de aseguramiento")
    propietario_id = Column(BigInteger, ForeignKey("persona.id"), nullable=True, comment="FK propietario (persona)")
    estado = Column(Integer, nullable=False, default=1, comment="1 activo, 0 inactivo")
    
    # Relaciones
    tipo_vehiculo = relationship("TipoVehiculo", back_populates="vehiculos")
    estado_aseguramiento = relationship("EstadoAseguramiento", back_populates="vehiculos")
    propietario = relationship("Persona", back_populates="vehiculos_propietario")
    accidentes = relationship("Accidente", back_populates="vehiculo")
    
    def __repr__(self) -> str:
        return f"<Vehiculo(id={self.id}, placa='{self.placa}', marca='{self.marca}')>"


# ============================================================================
# PROCEDIMIENTO
# ============================================================================
class Procedimiento(Base):
    __tablename__ = "procedimiento"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="PK procedimiento/catálogo")
    codigo = Column(String(15), unique=True, nullable=False, comment="Código interno del procedimiento")
    descripcion = Column(String(200), nullable=True, comment="Descripción del procedimiento")
    codigo_soat = Column(String(10), nullable=True, comment="Código SOAT (si aplica)")
    valor = Column(BigInteger, nullable=False, comment="Valor base del procedimiento")
    estado = Column(Enum("ACTIVO", "INACTIVO", name="estado_procedimiento"), nullable=False, default="ACTIVO", comment="Estado del procedimiento")
    es_traslado_primario = Column(Boolean, nullable=False, default=False, comment="Marca si es traslado primario")
    
    # Relaciones
    detalles = relationship("AccidenteDetalle", back_populates="procedimiento")
    
    def __repr__(self) -> str:
        return f"<Procedimiento(id={self.id}, codigo='{self.codigo}', descripcion='{self.descripcion}')>"
