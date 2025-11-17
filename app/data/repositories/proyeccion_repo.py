"""
Repositorio para proyecciones desde BD externa (READ-ONLY).
"""
from typing import List, Dict, Any, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session


class ProyeccionRepository:
    """
    Repositorio para consultas a la BD externa (RO).
    Usar para proyecciones, consultas históricas, etc.
    """
    
    def __init__(self, session: Session):
        self.session = session
    
    def ejecutar_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Ejecuta una query SELECT y retorna resultados como lista de diccionarios.
        
        Args:
            query: Query SQL (solo SELECT)
            params: Parámetros de la query
        
        Returns:
            Lista de diccionarios con los resultados
        """
        if not query.strip().upper().startswith("SELECT"):
            raise ValueError("Solo se permiten queries SELECT en la BD externa")
        
        result = self.session.execute(text(query), params or {})
        
        # Convertir resultado a lista de diccionarios
        columns = result.keys()
        return [dict(zip(columns, row)) for row in result.fetchall()]
    
    # ========================================================================
    # EJEMPLOS DE PROYECCIONES ESPECÍFICAS
    # ========================================================================
    
    def get_estadisticas_accidentes_por_mes(self, anio: int) -> List[Dict[str, Any]]:
        """
        Ejemplo: Obtiene estadísticas de accidentes por mes.
        Adaptar según estructura de BD externa.
        """
        query = """
        SELECT 
            MONTH(fecha_evento) as mes,
            COUNT(*) as total_accidentes,
            SUM(total_facturado) as total_facturado
        FROM accidentes_historico
        WHERE YEAR(fecha_evento) = :anio
        GROUP BY MONTH(fecha_evento)
        ORDER BY mes
        """
        
        return self.ejecutar_query(query, {"anio": anio})
    
    def get_top_naturalezas_evento(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Ejemplo: Obtiene las naturalezas de evento más frecuentes.
        """
        query = """
        SELECT 
            naturaleza_evento,
            COUNT(*) as total
        FROM accidentes_historico
        GROUP BY naturaleza_evento
        ORDER BY total DESC
        LIMIT :limit
        """
        
        return self.ejecutar_query(query, {"limit": limit})
