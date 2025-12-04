"""
Modelos de datos de la aplicación.
"""
from app.data.models.base import Base
from app.data.models.catalogos import (
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
from app.data.models.persona import Persona
from app.data.models.prestador import PrestadorSalud
from app.data.models.vehiculo import Vehiculo, Procedimiento
from app.data.models.accidente import (
    Accidente,
    AccidenteVictima,
    AccidenteConductor,
    AccidentePropietario,
)
from app.data.models.accidente_detalle import AccidenteDetalle
from app.data.models.accidente_totales import AccidenteTotales
from app.data.models.persona_config import PersonaConfig
from app.data.models.accidente_procesos import (
    AccidenteMedicoTratante,
    AccidenteRemision,
)

__all__ = [
    "Base",
    # Catálogos
    "Pais",
    "Departamento",
    "Municipio",
    "TipoIdentificacion",
    "Sexo",
    "NaturalezaEvento",
    "EstadoAseguramiento",
    "TipoVehiculo",
    "TipoServicio",
    # Entidades principales
    "Persona",
    "PrestadorSalud",
    "Vehiculo",
    "Procedimiento",
    # Accidente
    "Accidente",
    "AccidenteVictima",
    "AccidenteConductor",
    "AccidentePropietario",
    "AccidenteDetalle",
    "AccidenteTotales",
    "PersonaConfig",
    "AccidenteMedicoTratante",
    "AccidenteRemision",
]
