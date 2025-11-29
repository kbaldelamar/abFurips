"""
Repositorio para la entidad Vehiculo.
"""
from typing import Optional, List
from sqlalchemy.orm import Session, joinedload

from app.data.models.vehiculo import Vehiculo


class VehiculoRepository:
    """Repositorio para gestionar vehículos."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, vehiculo: Vehiculo) -> Vehiculo:
        """Crea un nuevo vehículo."""
        self.session.add(vehiculo)
        self.session.flush()
        return vehiculo
    
    def delete(self, vehiculo_id: int):
        """Elimina un vehículo (soft delete - cambia estado a 0)."""
        vehiculo = self.get_by_id(vehiculo_id)
        if vehiculo:
            vehiculo.estado = 0
            self.session.flush()
    
    def anular(self, vehiculo_id: int) -> bool:
        """Anula un vehículo (soft delete - cambia estado a 0)."""
        vehiculo = self.get_by_id(vehiculo_id)
        if vehiculo:
            vehiculo.estado = 0
            self.session.flush()
            return True
        return False
    
    def reactivar(self, vehiculo_id: int) -> bool:
        """Reactiva un vehículo anulado (cambia estado a 1)."""
        vehiculo = self.get_by_id(vehiculo_id)
        if vehiculo:
            vehiculo.estado = 1
            self.session.flush()
            return True
        return False
    
    def get_by_id(self, vehiculo_id: int) -> Optional[Vehiculo]:
        """Obtiene un vehículo por ID con relaciones cargadas."""
        return (
            self.session.query(Vehiculo)
            .options(
                joinedload(Vehiculo.tipo_vehiculo),
                joinedload(Vehiculo.estado_aseguramiento),
                joinedload(Vehiculo.propietario)
            )
            .filter(Vehiculo.id == vehiculo_id)
            .first()
        )
    
    def get_by_placa(self, placa: str) -> Optional[Vehiculo]:
        """Obtiene un vehículo por placa."""
        return (
            self.session.query(Vehiculo)
            .options(
                joinedload(Vehiculo.tipo_vehiculo),
                joinedload(Vehiculo.estado_aseguramiento),
                joinedload(Vehiculo.propietario)
            )
            .filter(Vehiculo.placa == placa.upper())
            .first()
        )
    
    def get_by_accidente(self, accidente_id: int) -> Optional[Vehiculo]:
        """Obtiene el vehículo activo asociado a un accidente (estado=1)."""
        from app.data.models import Accidente
        print(f"🔍 VehiculoRepo.get_by_accidente: Buscando para accidente_id={accidente_id}")
        
        accidente = (
            self.session.query(Accidente)
            .options(
                joinedload(Accidente.vehiculo).joinedload(Vehiculo.tipo_vehiculo),
                joinedload(Accidente.vehiculo).joinedload(Vehiculo.estado_aseguramiento),
                joinedload(Accidente.vehiculo).joinedload(Vehiculo.propietario)
            )
            .filter(Accidente.id == accidente_id)
            .first()
        )
        
        if accidente:
            print(f"  ✓ Accidente encontrado, vehiculo_id={accidente.vehiculo_id}")
            if accidente.vehiculo:
                print(f"  ✓ Vehículo cargado: ID={accidente.vehiculo.id}, Placa={accidente.vehiculo.placa}, Estado={accidente.vehiculo.estado}")
                if accidente.vehiculo.estado == 1:
                    return accidente.vehiculo
                else:
                    print(f"  ⚠️ Vehículo con estado={accidente.vehiculo.estado} (inactivo)")
            else:
                print(f"  ℹ️ vehiculo_id={accidente.vehiculo_id} pero no se cargó la relación")
        else:
            print(f"  ❌ Accidente no encontrado")
        
        return None
    
    def get_all_activos(self, limit: int = 100) -> List[Vehiculo]:
        """Obtiene todos los vehículos activos (estado=1)."""
        return (
            self.session.query(Vehiculo)
            .options(
                joinedload(Vehiculo.tipo_vehiculo),
                joinedload(Vehiculo.estado_aseguramiento)
            )
            .filter(Vehiculo.estado == 1)
            .order_by(Vehiculo.placa)
            .limit(limit)
            .all()
        )
    
    def get_by_propietario(self, propietario_id: int) -> List[Vehiculo]:
        """Obtiene todos los vehículos activos (estado=1) de un propietario."""
        return (
            self.session.query(Vehiculo)
            .options(
                joinedload(Vehiculo.tipo_vehiculo),
                joinedload(Vehiculo.estado_aseguramiento)
            )
            .filter(
                Vehiculo.propietario_id == propietario_id,
                Vehiculo.estado == 1
            )
            .order_by(Vehiculo.placa)
            .all()
        )
