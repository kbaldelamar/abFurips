"""
Modelo de Prestador de Salud (IPS).
"""
from sqlalchemy import Column, BigInteger, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.data.models.base import Base


class PrestadorSalud(Base):
    __tablename__ = "prestador_salud"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="PK prestador IPS")
    codigo_habilitacion = Column(String(12), unique=True, nullable=False, comment="Código de habilitación IPS")
    razon_social = Column(String(120), nullable=False, comment="Razón social IPS")
    nit = Column(String(15), nullable=True, comment="NIT de la IPS")
    telefono = Column(String(15), nullable=True, comment="Contacto telefónico")
    municipio_id = Column(Integer, ForeignKey("municipio.id"), nullable=True, comment="FK municipio de la IPS")
    direccion = Column(String(200), nullable=True, comment="Dirección de la IPS")
    
    # Relaciones
    municipio = relationship("Municipio", back_populates="prestadores")
    accidentes = relationship("Accidente", back_populates="prestador")
    
    def __repr__(self) -> str:
        return f"<PrestadorSalud(id={self.id}, codigo='{self.codigo_habilitacion}', razon_social='{self.razon_social}')>"
