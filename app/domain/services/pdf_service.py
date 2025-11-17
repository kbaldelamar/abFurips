"""
Servicio para generar PDFs estampados sobre plantillas oficiales.
"""
from pathlib import Path
from typing import Optional, Tuple
from datetime import datetime

from sqlalchemy.orm import Session

from app.data.repositories import AccidenteRepository
from app.config import get_settings
from app.infra.pdf.stamper import PDFStamper


class PDFService:
    """Servicio para generar PDFs FURIPS."""
    
    def __init__(self, session: Session):
        self.session = session
        self.accidente_repo = AccidenteRepository(session)
        self.settings = get_settings()
        self.stamper = PDFStamper()
    
    def generar_furips1_pdf(self, accidente_id: int) -> Tuple[bool, Optional[Path], Optional[str]]:
        """
        Genera PDF FURIPS1 estampando datos sobre la plantilla oficial.
        Retorna (exito, path_archivo, error).
        """
        try:
            accidente = self.accidente_repo.get_by_id(accidente_id)
            if not accidente:
                return False, None, "Accidente no encontrado"
            
            if not accidente.totales:
                return False, None, "Accidente no tiene totales calculados"
            
            # Preparar datos para estampar
            datos = self._preparar_datos_furips1(accidente)
            
            # Obtener plantilla
            template_path = self.settings.get_pdf_template_path("furips1")
            if not template_path.exists():
                return False, None, f"Plantilla no encontrada: {template_path}"
            
            # Generar archivo de salida
            output_dir = self.settings.get_output_dir()
            filename = f"FURIPS1_{accidente.numero_consecutivo}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            output_path = output_dir / filename
            
            # Estampar PDF
            self.stamper.estampar_furips1(
                template_path=template_path,
                output_path=output_path,
                datos=datos
            )
            
            return True, output_path, None
        
        except Exception as e:
            return False, None, f"Error al generar PDF FURIPS1: {str(e)}"
    
    def generar_furips2_pdf(self, accidente_id: int) -> Tuple[bool, Optional[Path], Optional[str]]:
        """
        Genera PDF FURIPS2 estampando datos sobre la plantilla oficial.
        Retorna (exito, path_archivo, error).
        """
        try:
            accidente = self.accidente_repo.get_by_id(accidente_id)
            if not accidente:
                return False, None, "Accidente no encontrado"
            
            if not accidente.detalles:
                return False, None, "Accidente no tiene detalles"
            
            # Preparar datos para estampar
            datos = self._preparar_datos_furips2(accidente)
            
            # Obtener plantilla
            template_path = self.settings.get_pdf_template_path("furips2")
            if not template_path.exists():
                return False, None, f"Plantilla no encontrada: {template_path}"
            
            # Generar archivo de salida
            output_dir = self.settings.get_output_dir()
            filename = f"FURIPS2_{accidente.numero_consecutivo}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            output_path = output_dir / filename
            
            # Estampar PDF
            self.stamper.estampar_furips2(
                template_path=template_path,
                output_path=output_path,
                datos=datos
            )
            
            return True, output_path, None
        
        except Exception as e:
            return False, None, f"Error al generar PDF FURIPS2: {str(e)}"
    
    def _preparar_datos_furips1(self, accidente) -> dict:
        """Prepara diccionario con datos para estampar en FURIPS1."""
        victima = accidente.victimas[0] if accidente.victimas else None
        totales = accidente.totales
        
        return {
            "codigo_habilitacion": accidente.prestador.codigo_habilitacion,
            "razon_social": accidente.prestador.razon_social,
            "consecutivo": accidente.numero_consecutivo,
            "factura": accidente.numero_factura,
            "rad_siras": accidente.numero_rad_siras,
            "fecha_evento": str(accidente.fecha_evento),
            "hora_evento": str(accidente.hora_evento),
            "municipio": accidente.municipio_evento.nombre,
            "direccion": accidente.direccion_evento,
            "zona": accidente.zona or "",
            "placa": accidente.vehiculo.placa if accidente.vehiculo else "",
            # Víctima
            "victima_nombre": victima.persona.nombre_completo if victima else "",
            "victima_documento": victima.persona.numero_identificacion if victima else "",
            # Totales
            "total_gmq_facturado": str(totales.total_facturado_gmq) if totales else "0",
            "total_gmq_reclamado": str(totales.total_reclamado_gmq) if totales else "0",
            "total_transporte_facturado": str(totales.total_facturado_transporte) if totales else "0",
            "total_transporte_reclamado": str(totales.total_reclamado_transporte) if totales else "0",
            "descripcion_evento": totales.descripcion_evento if totales else "",
        }
    
    def _preparar_datos_furips2(self, accidente) -> dict:
        """Prepara diccionario con datos para estampar en FURIPS2."""
        detalles_list = []
        
        for detalle in accidente.detalles:
            detalles_list.append({
                "tipo_servicio": detalle.tipo_servicio.descripcion,
                "codigo": detalle.codigo_servicio or "",
                "descripcion": detalle.descripcion or "",
                "cantidad": str(detalle.cantidad),
                "valor_unitario": str(detalle.valor_unitario),
                "valor_facturado": str(detalle.valor_facturado),
                "valor_reclamado": str(detalle.valor_reclamado),
            })
        
        return {
            "consecutivo": accidente.numero_consecutivo,
            "prestador": accidente.prestador.razon_social,
            "detalles": detalles_list,
        }
