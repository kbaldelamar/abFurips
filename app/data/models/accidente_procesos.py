"""
Modelos de AccidenteMedicoTratante y AccidenteRemision.
"""
from datetime import date, time, datetime

from sqlalchemy import Column, BigInteger, Integer, String, Date, Time, DateTime, ForeignKey, Enum, TIMESTAMP, SmallInteger, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.data.models.base import Base


class AccidenteMedicoTratante(Base):
    __tablename__ = "accidente_medico_tratante"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="PK vínculo médico tratante")
    accidente_id = Column(BigInteger, ForeignKey("accidente.id"), nullable=False, comment="FK accidente")
    accidente_victima_id = Column(BigInteger, ForeignKey("accidente_victima.id"), nullable=False, unique=True, comment="FK víctima atendida")
    persona_id = Column(BigInteger, ForeignKey("persona.id"), nullable=False, comment="FK persona del médico tratante")
    fecha_ingreso = Column(Date, nullable=True, comment="80: fecha de ingreso a IPS")
    hora_ingreso = Column(Time, nullable=True, comment="81: hora de ingreso a IPS")
    fecha_egreso = Column(Date, nullable=True, comment="82: fecha de egreso de IPS")
    hora_egreso = Column(Time, nullable=True, comment="83: hora de egreso de IPS")
    diagnostico_ingreso = Column(String(4), nullable=True, comment="84: CIE10 principal ingreso")
    diagnostico_ingreso_sec1 = Column(String(4), nullable=True, comment="85: CIE10 ingreso asociado 1")
    diagnostico_ingreso_sec2 = Column(String(4), nullable=True, comment="86: CIE10 ingreso asociado 2")
    diagnostico_egreso = Column(String(4), nullable=True, comment="87: CIE10 principal egreso")
    diagnostico_egreso_sec1 = Column(String(4), nullable=True, comment="88: CIE10 egreso asociado 1")
    diagnostico_egreso_sec2 = Column(String(4), nullable=True, comment="89: CIE10 egreso asociado 2")
    servicio_uci = Column(Boolean, nullable=True, comment="Uso de UCI: 0=no, 1=sí")
    dias_uci = Column(SmallInteger, nullable=True, comment="Días en UCI reclamados")
    estado = Column(Enum("activo", "inactivo", name="estado_medico_tratante"), nullable=False, default="activo", comment="Estatus lógico del vínculo")
    creado_en = Column(TIMESTAMP, server_default=func.current_timestamp(), comment="Fecha de creación")
    actualizado_en = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp(), comment="Fecha de última actualización")
    
    # Relaciones
    accidente = relationship("Accidente", back_populates="medicos_tratantes")
    victima = relationship("AccidenteVictima", back_populates="medico_tratante")
    medico = relationship("Persona", foreign_keys=[persona_id])
    
    def __repr__(self) -> str:
        return f"<AccidenteMedicoTratante(id={self.id}, accidente_id={self.accidente_id}, victima_id={self.accidente_victima_id})>"


class AccidenteRemision(Base):
    __tablename__ = "accidente_remision"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    accidente_id = Column(BigInteger, ForeignKey("accidente.id"), nullable=False, comment="FK accidente (padre)")
    tipo_referencia = Column(Integer, nullable=False, comment="1 = Remite paciente, 2 = Orden de servicio, 3 = Recibe paciente")
    fecha_remision = Column(Date, nullable=True)
    hora_salida = Column(Time, nullable=True)
    codigo_hab_remitente = Column(String(12), nullable=True)
    profesional_remite = Column(String(60), nullable=True)
    cargo_remite = Column(String(30), nullable=True)
    fecha_aceptacion = Column(Date, nullable=True)
    hora_aceptacion = Column(Time, nullable=True)
    codigo_hab_recibe = Column(String(12), nullable=True)
    profesional_recibe = Column(String(60), nullable=True)
    placa_ambulancia = Column(String(12), nullable=True)
    estado = Column(Enum("activo", "inactivo", name="estado_remision"), nullable=False, default="activo")
    persona_remite_id = Column(BigInteger, ForeignKey("persona.id"), nullable=True)
    persona_recibe_id = Column(BigInteger, ForeignKey("persona.id"), nullable=True)
    creado_en = Column(TIMESTAMP, server_default=func.current_timestamp())
    actualizado_en = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    # Relaciones
    accidente = relationship("Accidente", back_populates="remisiones")
    persona_remite = relationship("Persona", foreign_keys=[persona_remite_id])
    persona_recibe = relationship("Persona", foreign_keys=[persona_recibe_id])
    
    def __repr__(self) -> str:
        return f"<AccidenteRemision(id={self.id}, accidente_id={self.accidente_id}, tipo={self.tipo_referencia})>"
