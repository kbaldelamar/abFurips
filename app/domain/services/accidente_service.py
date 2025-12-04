"""
Servicio de negocio para gestión de Accidentes.
"""
from typing import List, Optional, Tuple
from datetime import date

from sqlalchemy.orm import Session

from app.data.models import (
    Accidente,
    AccidenteVictima,
    AccidenteConductor,
    AccidentePropietario,
    AccidenteDetalle,
    AccidenteTotales,
)
from app.data.repositories import (
    AccidenteRepository,
    DetalleRepository,
    TotalesRepository,
)
from app.domain.dto import (
    AccidenteDTO,
    VictimaDTO,
    DetalleDTO,
    TotalesDTO,
    AccidenteCompletoDTO,
)
from app.domain.validators import FuripsValidator


class AccidenteService:
    """Servicio de negocio para operaciones con Accidente."""
    
    def __init__(self, session: Session):
        self.session = session
        self.accidente_repo = AccidenteRepository(session)
        self.detalle_repo = DetalleRepository(session)
        self.totales_repo = TotalesRepository(session)
        self.validator = FuripsValidator()
    
    # ========================================================================
    # CRUD BÁSICO
    # ========================================================================
    
    def crear_accidente(self, accidente_dto: AccidenteDTO) -> Tuple[Optional[Accidente], List[str]]:
        """
        Crea un nuevo accidente con validaciones.
        - Si consecutivo está vacío: autogenera el siguiente consecutivo
        - Si consecutivo tiene valor: valida que no exista
        Retorna (accidente_creado, lista_errores).
        """
        errores = []
        
        # Validar que el prestador_id esté presente
        if not accidente_dto.prestador_id:
            return None, ["Debe seleccionar un prestador"]
        
        # Manejar consecutivo: autogenerar si está vacío, validar si tiene valor
        consecutivo_final = accidente_dto.numero_consecutivo.strip() if accidente_dto.numero_consecutivo else ""
        
        if not consecutivo_final:
            # AUTOGENERAR: Obtener el siguiente consecutivo
            consecutivo_final = self.accidente_repo.generar_siguiente_consecutivo(accidente_dto.prestador_id)
        else:
            # VALIDAR: Verificar que no exista ese consecutivo
            if self.accidente_repo.existe_consecutivo(accidente_dto.prestador_id, consecutivo_final):
                return None, [f"⚠️ El consecutivo '{consecutivo_final}' ya existe para este prestador"]
        
        # Actualizar el DTO con el consecutivo final
        accidente_dto.numero_consecutivo = consecutivo_final
        
        # Validar datos completos
        es_valido, errores_validacion = self.validator.validar_accidente_completo(accidente_dto.model_dump())
        if not es_valido:
            return None, errores_validacion
        
        # Crear entidad
        accidente = Accidente(**accidente_dto.model_dump(exclude={"id"}))
        
        try:
            accidente_creado = self.accidente_repo.create(accidente)
            self.session.commit()
            return accidente_creado, []
        except Exception as e:
            self.session.rollback()
            return None, [f"Error al crear accidente: {str(e)}"]
    
    def obtener_accidente(self, accidente_id: int) -> Optional[Accidente]:
        """Obtiene un accidente por ID con todas sus relaciones."""
        return self.accidente_repo.get_by_id(accidente_id)
    
    def actualizar_accidente(self, accidente_id: int, accidente_dto: AccidenteDTO) -> Tuple[Optional[Accidente], List[str]]:
        """Actualiza un accidente existente."""
        # Validar datos
        es_valido, errores = self.validator.validar_accidente_completo(accidente_dto.model_dump())
        if not es_valido:
            return None, errores
        
        # Obtener accidente existente
        accidente = self.accidente_repo.get_by_id(accidente_id)
        if not accidente:
            return None, ["Accidente no encontrado"]
        
        # Verificar unicidad de consecutivo (excluyendo el actual)
        if self.accidente_repo.existe_consecutivo(
            accidente_dto.prestador_id,
            accidente_dto.numero_consecutivo,
            excluir_id=accidente_id
        ):
            return None, ["El consecutivo ya existe para este prestador"]
        
        # Actualizar campos
        for campo, valor in accidente_dto.model_dump(exclude={"id"}).items():
            setattr(accidente, campo, valor)
        
        try:
            accidente_actualizado = self.accidente_repo.update(accidente)
            self.session.commit()
            return accidente_actualizado, []
        except Exception as e:
            self.session.rollback()
            return None, [f"Error al actualizar accidente: {str(e)}"]
    
    # ========================================================================
    # GESTIÓN DE VÍCTIMAS
    # ========================================================================
    
    def agregar_victima(self, accidente_id: int, victima_dto: VictimaDTO) -> Tuple[Optional[AccidenteVictima], List[str]]:
        """Agrega una víctima al accidente."""
        # Validar diagnósticos CIE-10
        errores = []
        for dx in [
            victima_dto.diagnostico_ingreso,
            victima_dto.diagnostico_ingreso_sec1,
            victima_dto.diagnostico_ingreso_sec2,
            victima_dto.diagnostico_egreso,
            victima_dto.diagnostico_egreso_sec1,
            victima_dto.diagnostico_egreso_sec2,
        ]:
            ok, err = self.validator.validar_diagnostico_cie10(dx)
            if not ok:
                errores.append(err)
        
        if errores:
            return None, errores
        
        # Crear víctima
        victima = AccidenteVictima(
            accidente_id=accidente_id,
            **victima_dto.model_dump(exclude={"id", "accidente_id"})
        )
        
        try:
            self.session.add(victima)
            self.session.flush()
            self.session.refresh(victima)
            self.session.commit()
            return victima, []
        except Exception as e:
            self.session.rollback()
            return None, [f"Error al agregar víctima: {str(e)}"]
    
    # ========================================================================
    # GESTIÓN DE DETALLES (FURIPS2)
    # ========================================================================
    
    def agregar_detalle(self, accidente_id: int, detalle_dto: DetalleDTO) -> Tuple[Optional[AccidenteDetalle], List[str]]:
        """Agrega un detalle al accidente con validaciones."""
        # Validar consistencia de valores
        ok, err = self.validator.validar_detalle_consistente(
            detalle_dto.cantidad,
            detalle_dto.valor_unitario,
            detalle_dto.valor_facturado
        )
        if not ok:
            return None, [err]
        
        # Crear detalle
        detalle = AccidenteDetalle(
            accidente_id=accidente_id,
            **detalle_dto.model_dump(exclude={"id", "accidente_id"})
        )
        
        try:
            detalle_creado = self.detalle_repo.create(detalle)
            self.session.commit()
            return detalle_creado, []
        except Exception as e:
            self.session.rollback()
            return None, [f"Error al agregar detalle: {str(e)}"]
    
    def calcular_y_guardar_totales(self, accidente_id: int, descripcion_evento: str, manifestacion_servicios: bool) -> Tuple[bool, List[str]]:
        """
        Calcula totales desde los detalles y guarda en accidente_totales.
        """
        try:
            # Calcular totales GMQ
            totales_gmq = self.detalle_repo.calcular_totales_gmq(accidente_id)
            
            # Calcular totales transporte
            totales_transporte = self.detalle_repo.calcular_totales_transporte(accidente_id)
            
            # Crear/actualizar totales
            totales = AccidenteTotales(
                accidente_id=accidente_id,
                total_facturado_gmq=totales_gmq["total_facturado"],
                total_reclamado_gmq=totales_gmq["total_reclamado"],
                total_facturado_transporte=totales_transporte["total_facturado"],
                total_reclamado_transporte=totales_transporte["total_reclamado"],
                manifestacion_servicios=manifestacion_servicios,
                descripcion_evento=descripcion_evento,
            )
            
            self.totales_repo.create_or_update(totales)
            self.session.commit()
            return True, []
        
        except Exception as e:
            self.session.rollback()
            return False, [f"Error al calcular totales: {str(e)}"]
    
    # ========================================================================
    # VALIDACIONES COMPLETAS
    # ========================================================================
    
    def validar_accidente_para_exportar(self, accidente_id: int) -> Tuple[bool, List[str]]:
        """
        Valida que el accidente esté completo y consistente para exportar.
        """
        errores = []
        
        # Obtener accidente
        accidente = self.accidente_repo.get_by_id(accidente_id)
        if not accidente:
            return False, ["Accidente no encontrado"]
        
        # Validar que tenga al menos una víctima
        if not accidente.victimas:
            errores.append("El accidente debe tener al menos una víctima")
        
        # Validar que tenga detalles
        if not accidente.detalles:
            errores.append("El accidente debe tener detalles de facturación")
        
        # Validar que tenga totales
        if not accidente.totales:
            errores.append("El accidente debe tener totales calculados")
        
        # Validar consistencia de totales
        if accidente.totales:
            totales_gmq = self.detalle_repo.calcular_totales_gmq(accidente_id)
            totales_transporte = self.detalle_repo.calcular_totales_transporte(accidente_id)
            
            ok, err = self.validator.validar_totales_vs_detalles(
                totales_gmq["total_facturado"],
                totales_transporte["total_facturado"],
                accidente.totales.total_facturado_gmq,
                accidente.totales.total_facturado_transporte,
            )
            if not ok:
                errores.append(err)
        
        return len(errores) == 0, errores
    
    # ========================================================================
    # BÚSQUEDAS
    # ========================================================================
    
    def buscar_accidentes(
        self,
        prestador_id: Optional[int] = None,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None,
        consecutivo: Optional[str] = None,
        factura: Optional[str] = None,
        limit: int = 50,
    ) -> List[Accidente]:
        """Busca accidentes por múltiples criterios."""
        return self.accidente_repo.search_by_filters(
            prestador_id=prestador_id,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            consecutivo=consecutivo,
            factura=factura,
            limit=limit,
        )
