"""
Servicio para proyecciones desde BD externa.
"""
from typing import List, Dict, Any, Optional

from sqlalchemy.orm import Session

from app.data.repositories import ProyeccionRepository


class ProyeccionService:
    """Servicio para consultas y proyecciones desde BD externa (READ-ONLY)."""
    
    def __init__(self, session_ext: Session):
        """
        Args:
            session_ext: Sesión de BD externa (READ-ONLY)
        """
        self.proyeccion_repo = ProyeccionRepository(session_ext)
    
    def obtener_estadisticas_mensuales(self, anio: int) -> List[Dict[str, Any]]:
        """Obtiene estadísticas de accidentes por mes."""
        return self.proyeccion_repo.get_estadisticas_accidentes_por_mes(anio)
    
    def obtener_top_naturalezas(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Obtiene las naturalezas de evento más frecuentes."""
        return self.proyeccion_repo.get_top_naturalezas_evento(limit)
    
    def ejecutar_consulta_personalizada(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Ejecuta una consulta SQL personalizada en la BD externa.
        SOLO permite SELECT.
        """
        return self.proyeccion_repo.ejecutar_query(query, params)
