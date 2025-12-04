"""
Validadores para datos FURIPS según circular.
"""
from typing import Optional, List, Tuple
from datetime import date


class FuripsValidator:
    """Validaciones de negocio según circular FURIPS."""
    
    # ========================================================================
    # CÓDIGOS VÁLIDOS SEGÚN CIRCULAR
    # ========================================================================
    
    NATURALEZAS_VALIDAS = [
        "01", "02", "03", "04", "05", "06", "07", "08", "09", "10",
        "11", "12", "13", "14", "15", "16", "17", "25", "26", "27"
    ]
    
    ESTADOS_ASEGURAMIENTO_VALIDOS = ["1", "2", "3", "4", "6", "7", "8"]
    
    TIPOS_VEHICULO_VALIDOS = [
        "01", "02", "03", "04", "05", "06", "07", "08", "10",
        "14", "17", "19", "20", "21", "22"
    ]
    
    TIPOS_SERVICIO_VALIDOS = ["1", "2", "3", "4", "5", "6", "7", "8"]
    
    CONDICIONES_VICTIMA_VALIDAS = ["1", "2", "3", "4"]  # conductor, peatón, ocupante, ciclista
    
    ZONAS_VALIDAS = ["U", "R"]  # Urbana, Rural
    
    # ========================================================================
    # VALIDACIONES DE LONGITUD
    # ========================================================================
    
    @staticmethod
    def validar_consecutivo(consecutivo: str) -> Tuple[bool, Optional[str]]:
        """Valida formato de consecutivo (12 dígitos)."""
        if not consecutivo:
            return False, "El consecutivo es obligatorio"
        
        if len(consecutivo) > 12:
            return False, "El consecutivo no puede exceder 12 caracteres"
        
        if not consecutivo.isdigit():
            return False, "El consecutivo debe contener solo dígitos"
        
        return True, None
    
    @staticmethod
    def validar_factura(factura: str) -> Tuple[bool, Optional[str]]:
        """Valida número de factura."""
        if not factura:
            return False, "El número de factura es obligatorio"
        
        if len(factura) > 20:
            return False, "El número de factura no puede exceder 20 caracteres"
        
        return True, None
    
    @staticmethod
    def validar_rad_siras(rad_siras: str) -> Tuple[bool, Optional[str]]:
        """Valida radicado SIRAS."""
        if not rad_siras:
            return False, "El radicado SIRAS es obligatorio"
        
        if len(rad_siras) > 20:
            return False, "El radicado SIRAS no puede exceder 20 caracteres"
        
        return True, None
    
    @staticmethod
    def validar_placa(placa: Optional[str]) -> Tuple[bool, Optional[str]]:
        """Valida formato de placa (opcional según estado)."""
        if placa and len(placa) > 10:
            return False, "La placa no puede exceder 10 caracteres"
        
        return True, None
    
    @staticmethod
    def validar_diagnostico_cie10(codigo: Optional[str]) -> Tuple[bool, Optional[str]]:
        """Valida código CIE-10 (4 caracteres)."""
        if codigo and len(codigo) != 4:
            return False, f"El código CIE-10 debe tener 4 caracteres (recibido: '{codigo}')"
        
        return True, None
    
    # ========================================================================
    # VALIDACIONES DE CÓDIGOS
    # ========================================================================
    
    @staticmethod
    def validar_naturaleza_evento(codigo: str) -> Tuple[bool, Optional[str]]:
        """Valida código de naturaleza del evento."""
        if codigo not in FuripsValidator.NATURALEZAS_VALIDAS:
            return False, f"Código de naturaleza '{codigo}' no válido"
        
        return True, None
    
    @staticmethod
    def validar_estado_aseguramiento(codigo: str) -> Tuple[bool, Optional[str]]:
        """Valida código de estado de aseguramiento."""
        if codigo not in FuripsValidator.ESTADOS_ASEGURAMIENTO_VALIDOS:
            return False, f"Código de estado de aseguramiento '{codigo}' no válido"
        
        return True, None
    
    @staticmethod
    def validar_tipo_vehiculo(codigo: str) -> Tuple[bool, Optional[str]]:
        """Valida código de tipo de vehículo."""
        if codigo not in FuripsValidator.TIPOS_VEHICULO_VALIDOS:
            return False, f"Código de tipo de vehículo '{codigo}' no válido"
        
        return True, None
    
    @staticmethod
    def validar_tipo_servicio(codigo: str) -> Tuple[bool, Optional[str]]:
        """Valida código de tipo de servicio."""
        if codigo not in FuripsValidator.TIPOS_SERVICIO_VALIDOS:
            return False, f"Código de tipo de servicio '{codigo}' no válido"
        
        return True, None
    
    @staticmethod
    def validar_condicion_victima(codigo: Optional[str]) -> Tuple[bool, Optional[str]]:
        """Valida código de condición de víctima."""
        if codigo and codigo not in FuripsValidator.CONDICIONES_VICTIMA_VALIDAS:
            return False, f"Código de condición '{codigo}' no válido"
        
        return True, None
    
    @staticmethod
    def validar_zona(zona: Optional[str]) -> Tuple[bool, Optional[str]]:
        """Valida zona urbana/rural."""
        if zona and zona not in FuripsValidator.ZONAS_VALIDAS:
            return False, f"Zona '{zona}' no válida (debe ser U o R)"
        
        return True, None
    
    # ========================================================================
    # VALIDACIONES DE NEGOCIO
    # ========================================================================
    
    @staticmethod
    def validar_vigencia_poliza(vigencia_inicio: Optional[date], vigencia_fin: Optional[date], fecha_evento: date) -> Tuple[bool, Optional[str]]:
        """Valida que el evento ocurrió dentro de la vigencia de la póliza."""
        if not vigencia_inicio or not vigencia_fin:
            return True, None  # Si no hay póliza, no validar
        
        if fecha_evento < vigencia_inicio or fecha_evento > vigencia_fin:
            return False, f"Evento fuera de vigencia de póliza ({vigencia_inicio} - {vigencia_fin})"
        
        return True, None
    
    @staticmethod
    def validar_totales_consistentes(total_facturado: int, total_reclamado: int) -> Tuple[bool, Optional[str]]:
        """Valida que el total reclamado no exceda el facturado."""
        if total_reclamado > total_facturado:
            return False, "El total reclamado no puede exceder el facturado"
        
        return True, None
    
    @staticmethod
    def validar_detalle_consistente(cantidad: int, valor_unitario: int, valor_facturado: int) -> Tuple[bool, Optional[str]]:
        """Valida que cantidad * valor_unitario = valor_facturado."""
        esperado = cantidad * valor_unitario
        
        if valor_facturado != esperado:
            return False, f"Valor facturado inconsistente: {cantidad} x {valor_unitario} = {esperado}, pero se declaró {valor_facturado}"
        
        return True, None
    
    @staticmethod
    def validar_totales_vs_detalles(
        total_gmq_detalle: int,
        total_transporte_detalle: int,
        total_gmq_declarado: int,
        total_transporte_declarado: int
    ) -> Tuple[bool, Optional[str]]:
        """
        Valida que los totales en accidente_totales coincidan con la suma de detalles.
        """
        errores = []
        
        if total_gmq_detalle != total_gmq_declarado:
            errores.append(
                f"Total GMQ inconsistente: suma detalles={total_gmq_detalle}, "
                f"declarado={total_gmq_declarado}"
            )
        
        if total_transporte_detalle != total_transporte_declarado:
            errores.append(
                f"Total transporte inconsistente: suma detalles={total_transporte_detalle}, "
                f"declarado={total_transporte_declarado}"
            )
        
        if errores:
            return False, "; ".join(errores)
        
        return True, None
    
    @staticmethod
    def validar_descripcion_otro_evento(naturaleza_codigo: str, descripcion: Optional[str]) -> Tuple[bool, Optional[str]]:
        """Valida que si naturaleza es '17' (Otro), debe haber descripción."""
        if naturaleza_codigo == "17" and not descripcion:
            return False, "Cuando la naturaleza es 'Otro' (17), debe especificar una descripción"
        
        return True, None
    
    # ========================================================================
    # VALIDACIÓN COMPLETA
    # ========================================================================
    
    @staticmethod
    def validar_accidente_completo(accidente_data: dict) -> Tuple[bool, List[str]]:
        """
        Realiza todas las validaciones sobre un accidente completo.
        Retorna (es_valido, lista_de_errores).
        """
        errores = []
        
        # Validar consecutivo
        ok, err = FuripsValidator.validar_consecutivo(accidente_data.get("numero_consecutivo", ""))
        if not ok:
            errores.append(err)
        
        # Validar factura
        ok, err = FuripsValidator.validar_factura(accidente_data.get("numero_factura", ""))
        if not ok:
            errores.append(err)
        
        # Validar SIRAS
        ok, err = FuripsValidator.validar_rad_siras(accidente_data.get("numero_rad_siras", ""))
        if not ok:
            errores.append(err)
        
        # Validar zona
        ok, err = FuripsValidator.validar_zona(accidente_data.get("zona"))
        if not ok:
            errores.append(err)
        
        # Validar descripción si es "Otro"
        ok, err = FuripsValidator.validar_descripcion_otro_evento(
            accidente_data.get("naturaleza_codigo", ""),
            accidente_data.get("descripcion_otro_evento")
        )
        if not ok:
            errores.append(err)
        
        return len(errores) == 0, errores
