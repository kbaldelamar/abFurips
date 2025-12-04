"""
Repositorios de acceso a datos.
"""
from app.data.repositories.catalogo_repo import CatalogoRepository
from app.data.repositories.persona_repo import PersonaRepository
from app.data.repositories.prestador_repo import PrestadorRepository
from app.data.repositories.accidente_repo import AccidenteRepository
from app.data.repositories.detalle_repo import DetalleRepository
from app.data.repositories.totales_repo import TotalesRepository
from app.data.repositories.proyeccion_repo import ProyeccionRepository
from app.data.repositories.persona_config_repo import PersonaConfigRepository
from app.data.repositories.medico_tratante_repo import MedicoTratanteRepository
from app.data.repositories.remision_repo import RemisionRepository

__all__ = [
    "CatalogoRepository",
    "PersonaRepository",
    "PrestadorRepository",
    "AccidenteRepository",
    "DetalleRepository",
    "TotalesRepository",
    "ProyeccionRepository",
    "PersonaConfigRepository",
    "MedicoTratanteRepository",
    "RemisionRepository",
]
