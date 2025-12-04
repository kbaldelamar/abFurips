"""
Repositorio para gestión de Personas.
"""
from typing import List, Optional

from sqlalchemy.orm import Session, joinedload

from app.data.models import Persona


class PersonaRepository:
    """Repositorio para operaciones con Persona."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_by_id(self, persona_id: int) -> Optional[Persona]:
        """Obtiene una persona por ID."""
        return (
            self.session.query(Persona)
            .options(
                joinedload(Persona.tipo_identificacion),
                joinedload(Persona.sexo),
                joinedload(Persona.municipio_residencia),
            )
            .filter(Persona.id == persona_id)
            .first()
        )
    
    def get_by_documento(self, tipo_id: int, numero: str) -> Optional[Persona]:
        """Busca una persona por tipo y número de documento."""
        return (
            self.session.query(Persona)
            .options(
                joinedload(Persona.tipo_identificacion),
                joinedload(Persona.sexo),
                joinedload(Persona.municipio_residencia),
            )
            .filter(
                Persona.tipo_identificacion_id == tipo_id,
                Persona.numero_identificacion == numero,
            )
            .first()
        )
    
    def get_all_activas(self, limit: int = 1000) -> List[Persona]:
        """Obtiene todas las personas activas."""
        return (
            self.session.query(Persona)
            .options(
                joinedload(Persona.tipo_identificacion),
                joinedload(Persona.sexo),
            )
            .order_by(Persona.primer_nombre, Persona.primer_apellido)
            .limit(limit)
            .all()
        )
    
    def search(self, texto: str, limit: int = 50) -> List[Persona]:
        """Busca personas por nombre, apellido o documento."""
        filtro = f"%{texto}%"
        return (
            self.session.query(Persona)
            .options(
                joinedload(Persona.tipo_identificacion),
                joinedload(Persona.sexo),
            )
            .filter(
                (Persona.primer_nombre.ilike(filtro))
                | (Persona.segundo_nombre.ilike(filtro))
                | (Persona.primer_apellido.ilike(filtro))
                | (Persona.segundo_apellido.ilike(filtro))
                | (Persona.numero_identificacion.ilike(filtro))
            )
            .limit(limit)
            .all()
        )
    
    def create(self, persona: Persona) -> Persona:
        """Crea una nueva persona."""
        self.session.add(persona)
        self.session.flush()
        self.session.refresh(persona)
        return persona
    
    def update(self, persona: Persona) -> Persona:
        """Actualiza una persona existente."""
        self.session.add(persona)
        self.session.flush()
        self.session.refresh(persona)
        return persona
    
    def delete(self, persona_id: int) -> bool:
        """Elimina una persona por ID."""
        persona = self.get_by_id(persona_id)
        if persona:
            self.session.delete(persona)
            self.session.flush()
            return True
        return False
    
    def obtener_o_crear(self, tipo_id: int, numero: str, datos_persona: dict) -> Persona:
        """
        Obtiene una persona existente por documento o crea una nueva.
        Retorna la persona (existente o nueva).
        """
        # Buscar si ya existe
        persona = self.get_by_documento(tipo_id, numero)
        
        if persona:
            # Si existe, actualizar datos
            for key, value in datos_persona.items():
                if hasattr(persona, key):
                    setattr(persona, key, value)
            self.session.flush()
            self.session.refresh(persona)
            return persona
        else:
            # Si no existe, crear nueva
            persona = Persona(**datos_persona)
            return self.create(persona)
