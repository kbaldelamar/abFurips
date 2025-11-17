"""
Servicio de exportación de archivos planos FURIPS1 y FURIPS2.
"""
from pathlib import Path
from typing import Optional, Tuple, List
from datetime import datetime

from sqlalchemy.orm import Session

from app.data.repositories import AccidenteRepository
from app.config import get_settings


class ExportService:
    """Servicio para exportar archivos planos FURIPS."""
    
    def __init__(self, session: Session):
        self.session = session
        self.accidente_repo = AccidenteRepository(session)
        self.settings = get_settings()
    
    def exportar_furips1(self, accidente_id: int) -> Tuple[bool, Optional[Path], Optional[str]]:
        """
        Exporta el accidente al formato FURIPS1 (archivo plano).
        Retorna (exito, path_archivo, error).
        """
        try:
            accidente = self.accidente_repo.get_by_id(accidente_id)
            if not accidente:
                return False, None, "Accidente no encontrado"
            
            if not accidente.totales:
                return False, None, "Accidente no tiene totales calculados"
            
            if not accidente.victimas:
                return False, None, "Accidente no tiene víctimas"
            
            # Generar líneas del archivo
            lineas = self._generar_lineas_furips1(accidente)
            
            # Guardar archivo
            output_dir = self.settings.get_output_dir()
            filename = f"FURIPS1_{accidente.numero_consecutivo}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            filepath = output_dir / filename
            
            with open(filepath, "w", encoding="latin-1") as f:
                f.write("\n".join(lineas))
            
            return True, filepath, None
        
        except Exception as e:
            return False, None, f"Error al exportar FURIPS1: {str(e)}"
    
    def exportar_furips2(self, accidente_id: int) -> Tuple[bool, Optional[Path], Optional[str]]:
        """
        Exporta el accidente al formato FURIPS2 (archivo plano).
        Retorna (exito, path_archivo, error).
        """
        try:
            accidente = self.accidente_repo.get_by_id(accidente_id)
            if not accidente:
                return False, None, "Accidente no encontrado"
            
            if not accidente.detalles:
                return False, None, "Accidente no tiene detalles"
            
            # Generar líneas del archivo
            lineas = self._generar_lineas_furips2(accidente)
            
            # Guardar archivo
            output_dir = self.settings.get_output_dir()
            filename = f"FURIPS2_{accidente.numero_consecutivo}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            filepath = output_dir / filename
            
            with open(filepath, "w", encoding="latin-1") as f:
                f.write("\n".join(lineas))
            
            return True, filepath, None
        
        except Exception as e:
            return False, None, f"Error al exportar FURIPS2: {str(e)}"
    
    def _generar_lineas_furips1(self, accidente) -> List[str]:
        """Genera las líneas del archivo plano FURIPS1."""
        lineas = []
        
        # Encabezado: datos del prestador, accidente, víctima, totales
        # Formato según circular (campos separados por delimitador, ej: pipe |)
        # NOTA: Ajustar según especificación exacta de la circular
        
        victima = accidente.victimas[0] if accidente.victimas else None
        totales = accidente.totales
        
        # Ejemplo simplificado (ajustar según especificación real)
        linea = "|".join([
            str(accidente.prestador.codigo_habilitacion),
            accidente.numero_consecutivo,
            accidente.numero_factura,
            accidente.numero_rad_siras,
            str(accidente.fecha_evento),
            str(accidente.hora_evento),
            # ... más campos según circular
            str(totales.total_facturado_gmq) if totales else "0",
            str(totales.total_reclamado_gmq) if totales else "0",
            str(totales.total_facturado_transporte) if totales else "0",
            str(totales.total_reclamado_transporte) if totales else "0",
            totales.descripcion_evento if totales else "",
        ])
        
        lineas.append(linea)
        return lineas
    
    def _generar_lineas_furips2(self, accidente) -> List[str]:
        """Genera las líneas del archivo plano FURIPS2."""
        lineas = []
        
        # Cada detalle es una línea
        for detalle in accidente.detalles:
            linea = "|".join([
                accidente.numero_consecutivo,
                str(detalle.tipo_servicio.codigo),
                detalle.codigo_servicio or "",
                detalle.descripcion or "",
                str(detalle.cantidad),
                str(detalle.valor_unitario),
                str(detalle.valor_facturado),
                str(detalle.valor_reclamado),
            ])
            lineas.append(linea)
        
        return lineas
