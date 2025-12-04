"""
Modelo de AccidenteDetalle (FURIPS2).
"""
from sqlalchemy import Column, BigInteger, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.data.models.base import Base


class AccidenteDetalle(Base):
    __tablename__ = "accidente_detalle"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="PK detalle FURIPS2")
    accidente_id = Column(BigInteger, ForeignKey("accidente.id"), nullable=False, comment="FK accidente")
    tipo_servicio_id = Column(Integer, ForeignKey("tipo_servicio.id"), nullable=False, comment="FK tipo de servicio (1..8)")
    procedimiento_id = Column(BigInteger, ForeignKey("procedimiento.id"), nullable=True, comment="FK procedimiento/catálogo")
    codigo_servicio = Column(String(15), nullable=True, comment="Código del servicio (CUM, SOAT, etc.)")
    descripcion = Column(String(200), nullable=True, comment="Descripción del ítem facturado")
    cantidad = Column(BigInteger, nullable=False, default=0, comment="Cantidad del servicio")
    valor_unitario = Column(BigInteger, nullable=False, default=0, comment="Valor unitario facturado")
    valor_facturado = Column(BigInteger, nullable=False, default=0, comment="Valor total facturado")
    valor_reclamado = Column(BigInteger, nullable=False, default=0, comment="Valor total reclamado")
    estado = Column(Integer, nullable=False, default=1, comment="1 activo, 0 inactivo")
    
    # Relaciones
    accidente = relationship("Accidente", back_populates="detalles")
    tipo_servicio = relationship("TipoServicio", back_populates="detalles")
    procedimiento = relationship("Procedimiento", back_populates="detalles")
    
    def __repr__(self) -> str:
        return f"<AccidenteDetalle(id={self.id}, accidente_id={self.accidente_id}, tipo_servicio_id={self.tipo_servicio_id})>"
