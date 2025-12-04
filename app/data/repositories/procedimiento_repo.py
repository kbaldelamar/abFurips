"""
Repositorio para Procedimiento.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.data.models.vehiculo import Procedimiento


class ProcedimientoRepository:
    def __init__(self, session: Session):
        self.session = session
    
    def get_by_id(self, procedimiento_id: int) -> Optional[Procedimiento]:
        """Obtiene un procedimiento por ID."""
        return (
            self.session.query(Procedimiento)
            .filter(Procedimiento.id == procedimiento_id)
            .first()
        )
    
    def get_by_codigo(self, codigo: str) -> Optional[Procedimiento]:
        """Obtiene un procedimiento por código."""
        return (
            self.session.query(Procedimiento)
            .filter(
                Procedimiento.codigo == codigo,
                Procedimiento.estado == "ACTIVO"
            )
            .first()
        )
    
    def buscar(self, termino: str) -> List[Procedimiento]:
        """
        Busca procedimientos por código o descripción.
        Retorna máximo 50 resultados.
        """
        termino_like = f"%{termino}%"
        return (
            self.session.query(Procedimiento)
            .filter(
                Procedimiento.estado == "ACTIVO",
                or_(
                    Procedimiento.codigo.ilike(termino_like),
                    Procedimiento.descripcion.ilike(termino_like),
                    Procedimiento.codigo_soat.ilike(termino_like)
                )
            )
            .order_by(Procedimiento.codigo)
            .limit(50)
            .all()
        )
    
    def get_todos_activos(self) -> List[Procedimiento]:
        """Obtiene todos los procedimientos activos."""
        return (
            self.session.query(Procedimiento)
            .filter(Procedimiento.estado == "ACTIVO")
            .order_by(Procedimiento.codigo)
            .all()
        )
    
    def get_traslados_primarios(self) -> List[Procedimiento]:
        """Obtiene todos los procedimientos de traslado primario."""
        return (
            self.session.query(Procedimiento)
            .filter(
                Procedimiento.estado == "ACTIVO",
                Procedimiento.es_traslado_primario == True
            )
            .order_by(Procedimiento.codigo)
            .all()
        )
    
    def create(self, procedimiento: Procedimiento) -> Procedimiento:
        """Crea un nuevo procedimiento."""
        self.session.add(procedimiento)
        self.session.flush()
        return procedimiento
    
    def update(self, procedimiento: Procedimiento) -> Procedimiento:
        """Actualiza un procedimiento existente."""
        self.session.flush()
        return procedimiento
    
    def desactivar(self, procedimiento_id: int) -> bool:
        """Desactiva un procedimiento."""
        procedimiento = self.get_by_id(procedimiento_id)
        if procedimiento:
            procedimiento.estado = "INACTIVO"
            self.session.flush()
            return True
        return False
