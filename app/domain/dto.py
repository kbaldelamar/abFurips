"""
DTOs (Data Transfer Objects) para transferencia de datos entre capas.
"""
from datetime import date, time, datetime
from typing import Optional, List

from pydantic import BaseModel, Field, field_validator


# ============================================================================
# CATÁLOGOS
# ============================================================================
class CatalogoDTO(BaseModel):
    """DTO base para catálogos."""
    id: int
    codigo: str
    descripcion: str
    
    class Config:
        from_attributes = True


# ============================================================================
# PERSONA
# ============================================================================
class PersonaDTO(BaseModel):
    """DTO para Persona."""
    id: Optional[int] = None
    tipo_identificacion_id: int
    numero_identificacion: str = Field(max_length=20)
    primer_nombre: str = Field(max_length=30)
    segundo_nombre: Optional[str] = Field(None, max_length=30)
    primer_apellido: str = Field(max_length=30)
    segundo_apellido: Optional[str] = Field(None, max_length=30)
    sexo_id: int
    fecha_nacimiento: date
    fecha_fallecimiento: Optional[date] = None
    direccion: str = Field(max_length=200)
    telefono: str = Field(max_length=15)
    municipio_residencia_id: int
    
    @field_validator('fecha_fallecimiento')
    @classmethod
    def validar_fallecimiento(cls, v, info):
        if v and 'fecha_nacimiento' in info.data:
            if v < info.data['fecha_nacimiento']:
                raise ValueError('Fecha de fallecimiento no puede ser anterior a nacimiento')
        return v
    
    class Config:
        from_attributes = True


# ============================================================================
# PRESTADOR
# ============================================================================
class PrestadorDTO(BaseModel):
    """DTO para PrestadorSalud."""
    id: Optional[int] = None
    codigo_habilitacion: str = Field(max_length=12)
    razon_social: str = Field(max_length=120)
    nit: Optional[str] = Field(None, max_length=15)
    telefono: Optional[str] = Field(None, max_length=15)
    municipio_id: Optional[int] = None
    direccion: Optional[str] = Field(None, max_length=200)
    
    class Config:
        from_attributes = True


# ============================================================================
# VEHÍCULO
# ============================================================================
class VehiculoDTO(BaseModel):
    """DTO para Vehículo."""
    id: Optional[int] = None
    placa: Optional[str] = Field(None, max_length=10)
    marca: Optional[str] = Field(None, max_length=30)
    tipo_vehiculo_id: Optional[int] = None
    aseguradora_codigo: Optional[str] = Field(None, max_length=6)
    numero_poliza: Optional[str] = Field(None, max_length=20)
    vigencia_inicio: Optional[date] = None
    vigencia_fin: Optional[date] = None
    estado_aseguramiento_id: int
    propietario_id: Optional[int] = None
    
    class Config:
        from_attributes = True


# ============================================================================
# ACCIDENTE
# ============================================================================
class AccidenteDTO(BaseModel):
    """DTO para Accidente."""
    id: Optional[int] = None
    prestador_id: int
    numero_consecutivo: str = Field(max_length=12)
    numero_factura: str = Field(max_length=20)
    numero_rad_siras: str = Field(max_length=20)
    naturaleza_evento_id: int
    descripcion_otro_evento: Optional[str] = Field(None, max_length=25)
    fecha_evento: date
    hora_evento: time
    municipio_evento_id: int
    direccion_evento: str = Field(max_length=200)
    zona: Optional[str] = Field(None, pattern="^[UR]$")  # U o R
    vehiculo_id: Optional[int] = None
    estado_aseguramiento_id: int
    
    class Config:
        from_attributes = True


# ============================================================================
# VÍCTIMA
# ============================================================================
class VictimaDTO(BaseModel):
    """DTO para AccidenteVictima."""
    id: Optional[int] = None
    accidente_id: Optional[int] = None
    persona_id: int
    condicion_codigo: Optional[str] = Field(None, pattern="^[1-4]$")  # 1-4
    fecha_ingreso: Optional[datetime] = None
    fecha_egreso: Optional[datetime] = None
    diagnostico_ingreso: Optional[str] = Field(None, max_length=4)
    diagnostico_ingreso_sec1: Optional[str] = Field(None, max_length=4)
    diagnostico_ingreso_sec2: Optional[str] = Field(None, max_length=4)
    diagnostico_egreso: Optional[str] = Field(None, max_length=4)
    diagnostico_egreso_sec1: Optional[str] = Field(None, max_length=4)
    diagnostico_egreso_sec2: Optional[str] = Field(None, max_length=4)
    servicio_uci: Optional[int] = Field(None, ge=0, le=1)  # 0 o 1
    dias_uci: Optional[int] = Field(None, ge=0)
    
    class Config:
        from_attributes = True


# ============================================================================
# DETALLE (FURIPS2)
# ============================================================================
class DetalleDTO(BaseModel):
    """DTO para AccidenteDetalle."""
    id: Optional[int] = None
    accidente_id: Optional[int] = None
    tipo_servicio_id: int
    procedimiento_id: Optional[int] = None
    codigo_servicio: Optional[str] = Field(None, max_length=15)
    descripcion: Optional[str] = Field(None, max_length=200)
    cantidad: int = Field(ge=0)
    valor_unitario: int = Field(ge=0)
    valor_facturado: int = Field(ge=0)
    valor_reclamado: int = Field(ge=0)
    
    class Config:
        from_attributes = True


# ============================================================================
# TOTALES (FURIPS1 - campos 97-102)
# ============================================================================
class TotalesDTO(BaseModel):
    """DTO para AccidenteTotales."""
    id: Optional[int] = None
    accidente_id: int
    total_facturado_gmq: int = Field(ge=0)
    total_reclamado_gmq: int = Field(ge=0)
    total_facturado_transporte: int = Field(ge=0)
    total_reclamado_transporte: int = Field(ge=0)
    manifestacion_servicios: bool
    descripcion_evento: str = Field(max_length=1000)
    
    class Config:
        from_attributes = True


# ============================================================================
# DTOs COMPUESTOS
# ============================================================================
class AccidenteCompletoDTO(BaseModel):
    """DTO completo con todos los datos del accidente."""
    accidente: AccidenteDTO
    victimas: List[VictimaDTO] = []
    conductores: List[int] = []  # IDs de personas
    propietarios: List[int] = []  # IDs de personas
    detalles: List[DetalleDTO] = []
    totales: Optional[TotalesDTO] = None
    
    class Config:
        from_attributes = True


# ============================================================================
# DTOs PARA EXPORTACIÓN
# ============================================================================
class FURIPS1ExportDTO(BaseModel):
    """DTO para exportar archivo plano FURIPS1."""
    accidente: AccidenteDTO
    victima: VictimaDTO
    totales: TotalesDTO
    prestador: PrestadorDTO
    
    class Config:
        from_attributes = True


class FURIPS2ExportDTO(BaseModel):
    """DTO para exportar archivo plano FURIPS2."""
    accidente: AccidenteDTO
    detalles: List[DetalleDTO]
    
    class Config:
        from_attributes = True
