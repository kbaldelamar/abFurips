"""
PDF Stamper - Estampa datos sobre plantillas PDF oficiales.
Usa PyMuPDF (fitz) para escribir texto y marcar checkboxes en coordenadas específicas.
"""
from pathlib import Path
from typing import Dict, Any, List, Tuple

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None


class PDFStamper:
    """Clase para estampar texto y checkboxes sobre PDFs base."""
    
    def __init__(self):
        if fitz is None:
            raise ImportError(
                "PyMuPDF no está instalado. "
                "Instalar con: pip install PyMuPDF"
            )
    
    def estampar_furips1(
        self,
        template_path: Path,
        output_path: Path,
        datos: Dict[str, Any]
    ) -> None:
        """
        Estampa datos en la plantilla FURIPS1.
        
        Args:
            template_path: Ruta de la plantilla PDF base
            output_path: Ruta donde guardar el PDF resultante
            datos: Diccionario con los datos a estampar
        """
        # Abrir plantilla
        doc = fitz.open(template_path)
        
        # Coordenadas de campos en FURIPS1 (ajustar según plantilla real)
        # Formato: (pagina, x, y, ancho, alto)
        coordenadas = self._get_coordenadas_furips1()
        
        # Estampar cada campo
        for campo, valor in datos.items():
            if campo in coordenadas:
                coords = coordenadas[campo]
                self._escribir_texto(
                    doc=doc,
                    pagina=coords["pagina"],
                    x=coords["x"],
                    y=coords["y"],
                    texto=str(valor),
                    font_size=coords.get("font_size", 10),
                )
        
        # Guardar
        doc.save(output_path)
        doc.close()
    
    def estampar_furips2(
        self,
        template_path: Path,
        output_path: Path,
        datos: Dict[str, Any]
    ) -> None:
        """
        Estampa datos en la plantilla FURIPS2.
        
        Args:
            template_path: Ruta de la plantilla PDF base
            output_path: Ruta donde guardar el PDF resultante
            datos: Diccionario con los datos a estampar (incluye lista de detalles)
        """
        # Abrir plantilla
        doc = fitz.open(template_path)
        
        # Coordenadas de encabezado
        coords_header = self._get_coordenadas_furips2_header()
        
        # Estampar encabezado
        self._escribir_texto(doc, 0, coords_header["consecutivo"]["x"], coords_header["consecutivo"]["y"], datos["consecutivo"])
        self._escribir_texto(doc, 0, coords_header["prestador"]["x"], coords_header["prestador"]["y"], datos["prestador"])
        
        # Coordenadas de tabla de detalles
        coords_tabla = self._get_coordenadas_furips2_tabla()
        
        # Estampar cada detalle (fila por fila)
        for idx, detalle in enumerate(datos.get("detalles", [])):
            if idx >= coords_tabla["max_filas"]:
                break  # Máximo de filas en la página
            
            y_base = coords_tabla["y_inicio"] + (idx * coords_tabla["altura_fila"])
            
            self._escribir_texto(doc, 0, coords_tabla["col_tipo_servicio"], y_base, detalle["tipo_servicio"], font_size=8)
            self._escribir_texto(doc, 0, coords_tabla["col_codigo"], y_base, detalle["codigo"], font_size=8)
            self._escribir_texto(doc, 0, coords_tabla["col_descripcion"], y_base, detalle["descripcion"], font_size=8)
            self._escribir_texto(doc, 0, coords_tabla["col_cantidad"], y_base, detalle["cantidad"], font_size=8)
            self._escribir_texto(doc, 0, coords_tabla["col_valor_unitario"], y_base, detalle["valor_unitario"], font_size=8)
            self._escribir_texto(doc, 0, coords_tabla["col_valor_facturado"], y_base, detalle["valor_facturado"], font_size=8)
            self._escribir_texto(doc, 0, coords_tabla["col_valor_reclamado"], y_base, detalle["valor_reclamado"], font_size=8)
        
        # Guardar
        doc.save(output_path)
        doc.close()
    
    def _escribir_texto(
        self,
        doc: "fitz.Document",
        pagina: int,
        x: float,
        y: float,
        texto: str,
        font_size: int = 10,
        color: Tuple[float, float, float] = (0, 0, 0)
    ) -> None:
        """Escribe texto en una posición específica del PDF."""
        page = doc[pagina]
        
        # Insertar texto
        page.insert_text(
            (x, y),
            texto,
            fontsize=font_size,
            color=color,
        )
    
    def _marcar_checkbox(
        self,
        doc: "fitz.Document",
        pagina: int,
        x: float,
        y: float,
        marcado: bool = True
    ) -> None:
        """Marca un checkbox en una posición específica."""
        if not marcado:
            return
        
        page = doc[pagina]
        
        # Dibujar una X
        rect = fitz.Rect(x, y, x + 10, y + 10)
        page.draw_line((x, y), (x + 10, y + 10), color=(0, 0, 0), width=1)
        page.draw_line((x + 10, y), (x, y + 10), color=(0, 0, 0), width=1)
    
    def _get_coordenadas_furips1(self) -> Dict[str, Dict[str, Any]]:
        """
        Retorna las coordenadas de los campos en la plantilla FURIPS1.
        NOTA: Estos valores son EJEMPLOS. Deben ajustarse según la plantilla oficial real.
        """
        return {
            "codigo_habilitacion": {"pagina": 0, "x": 100, "y": 50, "font_size": 10},
            "razon_social": {"pagina": 0, "x": 100, "y": 70, "font_size": 10},
            "consecutivo": {"pagina": 0, "x": 400, "y": 50, "font_size": 10},
            "factura": {"pagina": 0, "x": 400, "y": 70, "font_size": 10},
            "rad_siras": {"pagina": 0, "x": 400, "y": 90, "font_size": 10},
            "fecha_evento": {"pagina": 0, "x": 100, "y": 120, "font_size": 10},
            "hora_evento": {"pagina": 0, "x": 200, "y": 120, "font_size": 10},
            "municipio": {"pagina": 0, "x": 100, "y": 140, "font_size": 10},
            "direccion": {"pagina": 0, "x": 100, "y": 160, "font_size": 10},
            "placa": {"pagina": 0, "x": 100, "y": 180, "font_size": 10},
            "victima_nombre": {"pagina": 0, "x": 100, "y": 220, "font_size": 10},
            "victima_documento": {"pagina": 0, "x": 300, "y": 220, "font_size": 10},
            "total_gmq_facturado": {"pagina": 0, "x": 100, "y": 600, "font_size": 10},
            "total_gmq_reclamado": {"pagina": 0, "x": 200, "y": 600, "font_size": 10},
            "total_transporte_facturado": {"pagina": 0, "x": 100, "y": 620, "font_size": 10},
            "total_transporte_reclamado": {"pagina": 0, "x": 200, "y": 620, "font_size": 10},
            "descripcion_evento": {"pagina": 0, "x": 100, "y": 650, "font_size": 9},
        }
    
    def _get_coordenadas_furips2_header(self) -> Dict[str, Dict[str, float]]:
        """Coordenadas del encabezado FURIPS2."""
        return {
            "consecutivo": {"x": 100, "y": 50},
            "prestador": {"x": 100, "y": 70},
        }
    
    def _get_coordenadas_furips2_tabla(self) -> Dict[str, Any]:
        """Coordenadas de la tabla de detalles FURIPS2."""
        return {
            "y_inicio": 120,
            "altura_fila": 15,
            "max_filas": 20,
            "col_tipo_servicio": 50,
            "col_codigo": 150,
            "col_descripcion": 200,
            "col_cantidad": 350,
            "col_valor_unitario": 400,
            "col_valor_facturado": 450,
            "col_valor_reclamado": 500,
        }
