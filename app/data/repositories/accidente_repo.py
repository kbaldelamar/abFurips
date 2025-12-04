"""
Repositorio para gestión de Accidentes.
"""
from datetime import date
from typing import List, Optional

from sqlalchemy.orm import Session, joinedload

from app.data.models import Accidente


class AccidenteRepository:
    """Repositorio para operaciones con Accidente."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_by_id(self, accidente_id: int) -> Optional[Accidente]:
        """Obtiene un accidente por ID con todas sus relaciones."""
        return (
            self.session.query(Accidente)
            .options(
                joinedload(Accidente.prestador),
                joinedload(Accidente.naturaleza_evento),
                joinedload(Accidente.municipio_evento),
                joinedload(Accidente.vehiculo),
                joinedload(Accidente.estado_aseguramiento),
                joinedload(Accidente.victimas),
                joinedload(Accidente.conductores),
                joinedload(Accidente.propietarios),
                joinedload(Accidente.detalles),
                joinedload(Accidente.totales),
            )
            .filter(Accidente.id == accidente_id)
            .first()
        )
    
    def get_by_consecutivo(self, prestador_id: int, consecutivo: str) -> Optional[Accidente]:
        """Busca un accidente por prestador y consecutivo."""
        return (
            self.session.query(Accidente)
            .filter(
                Accidente.prestador_id == prestador_id,
                Accidente.numero_consecutivo == consecutivo,
            )
            .first()
        )
    
    def search_by_filters(
        self,
        prestador_id: Optional[int] = None,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None,
        consecutivo: Optional[str] = None,
        factura: Optional[str] = None,
        limit: int = 50,
        solo_activos: bool = True,
    ) -> List[Accidente]:
        """Busca accidentes por múltiples criterios."""
        query = self.session.query(Accidente).options(
            joinedload(Accidente.prestador),
            joinedload(Accidente.naturaleza_evento),
        )
        
        # Por defecto solo mostrar activos
        if solo_activos:
            query = query.filter(Accidente.estado == 1)
        
        if prestador_id:
            query = query.filter(Accidente.prestador_id == prestador_id)
        
        if fecha_desde:
            query = query.filter(Accidente.fecha_evento >= fecha_desde)
        
        if fecha_hasta:
            query = query.filter(Accidente.fecha_evento <= fecha_hasta)
        
        if consecutivo:
            query = query.filter(Accidente.numero_consecutivo.ilike(f"%{consecutivo}%"))
        
        if factura:
            query = query.filter(Accidente.numero_factura.ilike(f"%{factura}%"))
        
        return query.order_by(Accidente.fecha_evento.desc()).limit(limit).all()
    
    def create(self, accidente: Accidente) -> Accidente:
        """Crea un nuevo accidente."""
        self.session.add(accidente)
        self.session.flush()
        self.session.refresh(accidente)
        return accidente
    
    def update(self, accidente: Accidente) -> Accidente:
        """Actualiza un accidente existente."""
        self.session.add(accidente)
        self.session.flush()
        self.session.refresh(accidente)
        return accidente
    
    def delete(self, accidente_id: int) -> bool:
        """Elimina un accidente por ID (eliminación física)."""
        accidente = self.get_by_id(accidente_id)
        if accidente:
            self.session.delete(accidente)
            self.session.flush()
            return True
        return False
    
    def anular(self, accidente_id: int) -> bool:
        """Anula un accidente (soft delete - cambia estado a 0)."""
        accidente = self.get_by_id(accidente_id)
        if accidente:
            accidente.estado = 0
            self.session.flush()
            return True
        return False
    
    def reactivar(self, accidente_id: int) -> bool:
        """Reactiva un accidente anulado (cambia estado a 1)."""
        accidente = self.get_by_id(accidente_id)
        if accidente:
            accidente.estado = 1
            self.session.flush()
            return True
        return False
    
    def get_activos(self, limit: int = 100) -> List[Accidente]:
        """Obtiene solo accidentes activos (estado=1)."""
        return (
            self.session.query(Accidente)
            .options(
                joinedload(Accidente.prestador),
                joinedload(Accidente.naturaleza_evento),
                joinedload(Accidente.municipio_evento),
            )
            .filter(Accidente.estado == 1)
            .order_by(Accidente.fecha_evento.desc())
            .limit(limit)
            .all()
        )
    
    def existe_consecutivo(self, prestador_id: int, consecutivo: str, excluir_id: Optional[int] = None) -> bool:
        """Verifica si existe un consecutivo para un prestador (útil para validación)."""
        query = self.session.query(Accidente).filter(
            Accidente.prestador_id == prestador_id,
            Accidente.numero_consecutivo == consecutivo,
        )
        
        if excluir_id:
            query = query.filter(Accidente.id != excluir_id)
        
        return query.count() > 0
    
    def get_ultimo_consecutivo(self, prestador_id: int, con_lock: bool = False) -> Optional[str]:
        """
        Obtiene el último (mayor) consecutivo usado por un prestador.
        
        Args:
            prestador_id: ID del prestador
            con_lock: Si True, usa SELECT FOR UPDATE para bloquear el registro
        """
        from sqlalchemy import func, cast, Integer
        
        # Obtener el consecutivo máximo numéricamente
        query = (
            self.session.query(func.max(cast(Accidente.numero_consecutivo, Integer)))
            .filter(Accidente.prestador_id == prestador_id)
        )
        
        if con_lock:
            # Bloquear para evitar concurrencia (FOR UPDATE)
            query = query.with_for_update()
        
        resultado = query.scalar()
        
        if resultado:
            return str(resultado).zfill(12)
        
        return None

    def get_totales_by_accidente(self, accidente_id: int) -> dict:
        """Calcula totales informativos a partir de accidente_detalle.

        Devuelve un dict con claves: 'gastosMovilizacion' y 'gastosQx'.
        """
        # Importar dentro del método para evitar dependencias circulares en tiempo de import
        from sqlalchemy import func, case
        from app.data.models import AccidenteDetalle

        # SUM CASE: tipo_servicio_id == 4 => movilizacion, else => quirurgicos
        # Aplicar filtro adicional: considerar sólo detalles activos (estado == 1)
        movilizacion_sum = self.session.query(
            func.coalesce(func.sum(
                case(
                    (AccidenteDetalle.tipo_servicio_id == 4, AccidenteDetalle.valor_unitario),
                    else_=0
                )
            ), 0)
        ).filter(
            AccidenteDetalle.accidente_id == accidente_id,
            AccidenteDetalle.estado == 1,
        ).scalar() or 0

        qx_sum = self.session.query(
            func.coalesce(func.sum(
                case(
                    (AccidenteDetalle.tipo_servicio_id != 4, AccidenteDetalle.valor_unitario),
                    else_=0
                )
            ), 0)
        ).filter(
            AccidenteDetalle.accidente_id == accidente_id,
            AccidenteDetalle.estado == 1,
        ).scalar() or 0

        return {
            "accidente_id": accidente_id,
            "gastosMovilizacion": float(movilizacion_sum),
            "gastosQx": float(qx_sum),
        }
    
    def generar_siguiente_consecutivo(self, prestador_id: int) -> str:
        """
        Genera el siguiente consecutivo para un prestador (último + 1).
        THREAD-SAFE: Usa lock a nivel de base de datos.
        """
        # Usar lock para evitar condiciones de carrera
        ultimo_consecutivo = self.get_ultimo_consecutivo(prestador_id, con_lock=True)
        
        if not ultimo_consecutivo:
            # Primer consecutivo para este prestador
            return "1".zfill(12)  # "000000000001"
        
        try:
            # Convertir a número y sumar 1
            numero = int(ultimo_consecutivo) + 1
            return str(numero).zfill(12)  # Rellenar con ceros a la izquierda
        except ValueError:
            # Si el consecutivo no es numérico, retornar "1"
            return "1".zfill(12)
    
    def buscar_accidentes_con_victima(self, filtros: dict) -> List:
        """
        Busca accidentes con información de la víctima según filtros.
        
        Filtros soportados:
        - id: ID del accidente
        - consecutivo: Número consecutivo
        - factura: Número de factura
        - documento: Número de documento de la víctima
        """
        from app.data.models import AccidenteVictima, Persona, TipoIdentificacion
        
        # Query base con JOIN
        query = (
            self.session.query(
                Accidente.id,
                Accidente.numero_consecutivo,
                Accidente.numero_factura,
                Accidente.fecha_evento,
                Accidente.hora_evento,
                TipoIdentificacion.descripcion.label('tipo_identificacion'),
                Persona.numero_identificacion,
                Persona.primer_nombre,
                Persona.segundo_nombre,
                Persona.primer_apellido,
                Persona.segundo_apellido,
            )
            .select_from(AccidenteVictima)
            .join(Accidente, AccidenteVictima.accidente_id == Accidente.id)
            .join(Persona, AccidenteVictima.persona_id == Persona.id)
            .join(TipoIdentificacion, Persona.tipo_identificacion_id == TipoIdentificacion.id)
        )
        
        # Aplicar filtros
        if filtros.get("id"):
            query = query.filter(Accidente.id == filtros["id"])
        
        if filtros.get("consecutivo"):
            query = query.filter(Accidente.numero_consecutivo.like(f"%{filtros['consecutivo']}%"))
        
        if filtros.get("factura"):
            query = query.filter(Accidente.numero_factura.like(f"%{filtros['factura']}%"))
        
        if filtros.get("documento"):
            query = query.filter(Persona.numero_identificacion.like(f"%{filtros['documento']}%"))

        # Mostrar solo accidentes activos (estado = 1)
        query = query.filter(Accidente.estado == 1)
        
        # Ordenar por fecha descendente
        query = query.order_by(Accidente.fecha_evento.desc())
        
        # Limitar resultados
        query = query.limit(100)
        # Intentar mostrar la consulta SQL que se ejecutará (con valores cuando sea posible)
        try:
            # Obtener dialecto del engine ligado a la sesión
            dialect = self.session.get_bind().dialect
            compiled = query.statement.compile(dialect=dialect, compile_kwargs={"literal_binds": True})
            print("[AccidenteRepository] SQL ejecutada:", compiled)
        except Exception as e:
            # Fallback: mostrar representación del query
            try:
                print("[AccidenteRepository] SQL (fallback):", str(query))
            except Exception:
                print("[AccidenteRepository] No se pudo compilar la consulta para mostrarla")

        results = query.all()
        # Imprimir registros devueltos (para depuración)
        try:
            print(f"[AccidenteRepository] Registros devueltos: {len(results)}")
            for r in results:
                print(repr(r))
        except Exception:
            pass

        return results

    def resumen_relaciones(self, accidente_id: int) -> dict:
        """
        Devuelve un resumen con conteos de las tablas relacionadas a un `accidente`.

        Resultado ejemplo:
        {
            'victimas': 2,
            'conductores': 1,
            'propietarios': 1,
            'detalles': 5,
            'totales': 1,
            'medicos_tratantes': 1,
            'remisiones': 0,
        }
        """
        from app.data.models import (
            AccidenteVictima,
            AccidenteConductor,
            AccidentePropietario,
            AccidenteDetalle,
            AccidenteTotales,
            AccidenteMedicoTratante,
            AccidenteRemision,
        )

        resumen = {}

        resumen['victimas'] = (
            self.session.query(AccidenteVictima)
            .filter(AccidenteVictima.accidente_id == accidente_id)
            .count()
        )

        resumen['conductores'] = (
            self.session.query(AccidenteConductor)
            .filter(AccidenteConductor.accidente_id == accidente_id)
            .count()
        )

        resumen['propietarios'] = (
            self.session.query(AccidentePropietario)
            .filter(AccidentePropietario.accidente_id == accidente_id)
            .count()
        )

        resumen['detalles'] = (
            self.session.query(AccidenteDetalle)
            .filter(AccidenteDetalle.accidente_id == accidente_id)
            .count()
        )

        resumen['totales'] = (
            self.session.query(AccidenteTotales)
            .filter(AccidenteTotales.accidente_id == accidente_id)
            .count()
        )

        resumen['medicos_tratantes'] = (
            self.session.query(AccidenteMedicoTratante)
            .filter(AccidenteMedicoTratante.accidente_id == accidente_id)
            .count()
        )

        resumen['remisiones'] = (
            self.session.query(AccidenteRemision)
            .filter(AccidenteRemision.accidente_id == accidente_id)
            .count()
        )

        return resumen
