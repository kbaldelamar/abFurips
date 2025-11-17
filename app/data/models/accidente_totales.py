"""
Modelo de AccidenteTotales (campos 97-102 FURIPS1).
"""
from sqlalchemy import Column, BigInteger, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.data.models.base import Base


class AccidenteTotales(Base):
    __tablename__ = "accidente_totales"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="PK totales FURIPS1")
    accidente_id = Column(BigInteger, ForeignKey("accidente.id"), nullable=False, unique=True, comment="FK accidente")
    total_facturado_gmq = Column(BigInteger, nullable=False, comment="Campo 97: total facturado gastos médico-quirúrgicos")
    total_reclamado_gmq = Column(BigInteger, nullable=False, comment="Campo 98: total reclamado gastos médico-quirúrgicos")
    total_facturado_transporte = Column(BigInteger, nullable=False, comment="Campo 99: total facturado transporte primario")
    total_reclamado_transporte = Column(BigInteger, nullable=False, comment="Campo 100: total reclamado transporte primario")
    manifestacion_servicios = Column(Boolean, nullable=False, comment="Campo 101: 0/1 servicios habilitados")
    descripcion_evento = Column(String(1000), nullable=False, comment="Campo 102: descripción breve del evento")
    
    # Relaciones
    accidente = relationship("Accidente", back_populates="totales")
    
    def __repr__(self) -> str:
        return f"<AccidenteTotales(id={self.id}, accidente_id={self.accidente_id})>"
