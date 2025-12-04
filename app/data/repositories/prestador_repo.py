"""
Repositorio para gestión de Prestadores de Salud.
"""
from typing import List, Optional

from sqlalchemy.orm import Session, joinedload

from app.data.models import PrestadorSalud


class PrestadorRepository:
    """Repositorio para operaciones con PrestadorSalud."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_by_id(self, prestador_id: int) -> Optional[PrestadorSalud]:
        """Obtiene un prestador por ID."""
        return (
            self.session.query(PrestadorSalud)
            .options(joinedload(PrestadorSalud.municipio))
            .filter(PrestadorSalud.id == prestador_id)
            .first()
        )
    
    def get_by_codigo(self, codigo_habilitacion: str) -> Optional[PrestadorSalud]:
        """Obtiene un prestador por código de habilitación."""
        return (
            self.session.query(PrestadorSalud)
            .options(joinedload(PrestadorSalud.municipio))
            .filter(PrestadorSalud.codigo_habilitacion == codigo_habilitacion)
            .first()
        )
    
    def search(self, texto: str, limit: int = 50) -> List[PrestadorSalud]:
        """Busca prestadores por razón social, NIT o código."""
        filtro = f"%{texto}%"
        return (
            self.session.query(PrestadorSalud)
            .options(joinedload(PrestadorSalud.municipio))
            .filter(
                (PrestadorSalud.razon_social.ilike(filtro))
                | (PrestadorSalud.nit.ilike(filtro))
                | (PrestadorSalud.codigo_habilitacion.ilike(filtro))
            )
            .limit(limit)
            .all()
        )
    
    def get_all(self, limit: int = 100) -> List[PrestadorSalud]:
        """Obtiene todos los prestadores."""
        return (
            self.session.query(PrestadorSalud)
            .options(joinedload(PrestadorSalud.municipio))
            .order_by(PrestadorSalud.razon_social)
            .limit(limit)
            .all()
        )
    
    def create(self, prestador: PrestadorSalud) -> PrestadorSalud:
        """Crea un nuevo prestador."""
        self.session.add(prestador)
        self.session.flush()
        self.session.refresh(prestador)
        return prestador
    
    def update(self, prestador: PrestadorSalud) -> PrestadorSalud:
        """Actualiza un prestador existente."""
        self.session.add(prestador)
        self.session.flush()
        self.session.refresh(prestador)
        return prestador
