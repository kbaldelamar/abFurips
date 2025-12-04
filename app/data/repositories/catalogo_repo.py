"""
Repositorio para gestión de catálogos.
"""
from typing import List, Optional

from sqlalchemy.orm import Session

from app.data.models import (
    Pais,
    Departamento,
    Municipio,
    TipoIdentificacion,
    Sexo,
    NaturalezaEvento,
    EstadoAseguramiento,
    TipoVehiculo,
    TipoServicio,
)


class CatalogoRepository:
    """Repositorio para operaciones de catálogos/maestros."""
    
    def __init__(self, session: Session):
        self.session = session
    
    # ========================================================================
    # GEOGRAFÍA
    # ========================================================================
    def get_paises(self, activos_solo: bool = True) -> List[Pais]:
        """Obtiene todos los países."""
        query = self.session.query(Pais)
        if activos_solo:
            query = query.filter(Pais.estado == True)
        return query.order_by(Pais.nombre).all()
    
    def get_departamentos_por_pais(self, pais_id: int, activos_solo: bool = True) -> List[Departamento]:
        """Obtiene departamentos de un país."""
        query = self.session.query(Departamento).filter(Departamento.pais_id == pais_id)
        if activos_solo:
            query = query.filter(Departamento.estado == True)
        return query.order_by(Departamento.nombre).all()
    
    def get_municipios_por_departamento(self, departamento_id: int, activos_solo: bool = True) -> List[Municipio]:
        """Obtiene municipios de un departamento."""
        query = self.session.query(Municipio).filter(Municipio.departamento_id == departamento_id)
        if activos_solo:
            query = query.filter(Municipio.estado == True)
        return query.order_by(Municipio.nombre).all()
    
    def get_municipio_by_id(self, municipio_id: int) -> Optional[Municipio]:
        """Obtiene un municipio por ID."""
        return self.session.query(Municipio).filter(Municipio.id == municipio_id).first()
    
    def get_todos_municipios(self, activos_solo: bool = True) -> List[Municipio]:
        """Obtiene todos los municipios sin filtrar por departamento."""
        query = self.session.query(Municipio)
        if activos_solo:
            query = query.filter(Municipio.estado == True)
        return query.order_by(Municipio.nombre).all()
    
    # ========================================================================
    # IDENTIFICACIÓN Y PERSONA
    # ========================================================================
    def get_tipos_identificacion(self) -> List[TipoIdentificacion]:
        """Obtiene todos los tipos de identificación."""
        return self.session.query(TipoIdentificacion).order_by(TipoIdentificacion.descripcion).all()
    
    def get_sexos(self) -> List[Sexo]:
        """Obtiene todos los sexos."""
        return self.session.query(Sexo).order_by(Sexo.id).all()
    
    # ========================================================================
    # EVENTO
    # ========================================================================
    def get_naturalezas_evento(self) -> List[NaturalezaEvento]:
        """Obtiene todas las naturalezas de evento."""
        return self.session.query(NaturalezaEvento).order_by(NaturalezaEvento.codigo).all()
    
    def get_naturaleza_evento_by_id(self, naturaleza_id: int) -> Optional[NaturalezaEvento]:
        """Obtiene una naturaleza de evento por ID."""
        return self.session.query(NaturalezaEvento).filter(NaturalezaEvento.id == naturaleza_id).first()
    
    def get_estados_aseguramiento(self) -> List[EstadoAseguramiento]:
        """Obtiene todos los estados de aseguramiento."""
        return self.session.query(EstadoAseguramiento).order_by(EstadoAseguramiento.codigo).all()
    
    # ========================================================================
    # VEHÍCULO
    # ========================================================================
    def get_tipos_vehiculo(self) -> List[TipoVehiculo]:
        """Obtiene todos los tipos de vehículo."""
        return self.session.query(TipoVehiculo).order_by(TipoVehiculo.codigo).all()
    
    # ========================================================================
    # SERVICIOS
    # ========================================================================
    def get_tipos_servicio(self) -> List[TipoServicio]:
        """Obtiene todos los tipos de servicio."""
        return self.session.query(TipoServicio).order_by(TipoServicio.codigo).all()
