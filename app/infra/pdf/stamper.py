"""Clean PDF stamper for FURIPS generation.

Provides a single `PDFStamper` class with a single implementation of
`estampar_furips_desde_cero` and the minimal helpers the project needs.
"""
from pathlib import Path
from typing import Dict, Any
import os
import subprocess
import sys
from datetime import datetime
import tempfile

try:
    import fitz  # PyMuPDF
except Exception:
    fitz = None


class PDFStamper:
    """Single, clean PDF stamper used to generate a compact FURIPS page."""

    def __init__(self) -> None:
        if fitz is None:
            raise ImportError("PyMuPDF no está instalado. Instalar con: pip install PyMuPDF")

    def estampar_furips_desde_cero(self, imagen_encabezado_path: Path, output_path: Path, datos: Dict[str, Any]) -> str:
        """Generate a compact, single-page FURIPS using values from `datos`.

        Returns the path where the PDF was saved.
        """
        doc = fitz.open()
        page = doc.new_page(width=595, height=842)
        page_w, page_h = page.rect.width, page.rect.height

        # short resumen for debugging
        try:
            resumen = {k: datos.get(k) for k in ("idAccidente", "codigo_habilitacion", "numero_factura", "numero_consecutivo")}
            print("[PDFStamper] resumen datos recibidos:", resumen)
        except Exception:
            pass

        margin = 36

        # header image (if present)
        img_path = Path(imagen_encabezado_path)
        if img_path.exists():
            img_w = page_w - margin * 2
            img_rect = fitz.Rect(margin, margin, margin + img_w, margin + 90)
            try:
                page.insert_image(img_rect, filename=str(img_path))
            except Exception:
                self._rect(page, margin, margin, img_w, 90, color=(0.6, 0.6, 0.6), width=0.5)
        else:
            self._rect(page, margin, margin, page_w - 72, 90, color=(0.6, 0.6, 0.6), width=0.5)

        # Section I title
        box_x = margin
        box_y = margin + 90 + 6
        box_w = page_w - 72
        box_h = 12
        self._fill_rect(page, box_x, box_y, box_w, box_h, color=(0.92, 0.92, 0.92))
        self._rect(page, box_x, box_y, box_w, box_h, color=(0, 0, 0), width=0.35)
        self._centered_text(page, box_x, box_y, box_w, box_h, datos.get("_section_title", "I.DATOS DE LA RECLAMACION"), fontsize=7, bold=True)

        # Row 1: Radicado + RGO
        row1_label_y = box_y + box_h + 4
        available_w = page_w - 2 * margin
        label_font = 8
        long_label_text = "No. Radicado Anterior"
        long_label_w = int(max(80, self._estimate_text_width(long_label_text, label_font) + 8))
        rgo_w = max(24, int(available_w * 0.05))
        label_box_gap = max(6, int(available_w * 0.01))
        right_padding = 12
        boxes_available = available_w - long_label_w - label_box_gap - right_padding
        long_w = int(max(120, boxes_available - rgo_w - 8))
        long_x = margin + long_label_w + label_box_gap
        rgo_x = long_x + long_w + 8
        row1_box_y = row1_label_y + 10
        box_h = 14
        self._fill_rect(page, long_x, row1_box_y, long_w, box_h, color=(1, 1, 1))
        self._rect(page, long_x, row1_box_y, long_w, box_h, color=(0, 0, 0), width=0.6)
        self._fill_rect(page, rgo_x, row1_box_y, rgo_w, box_h, color=(1, 1, 1))
        self._rect(page, rgo_x, row1_box_y, rgo_w, box_h, color=(0, 0, 0), width=0.6)
        self._left_text(page, margin, row1_box_y + (box_h - label_font) / 2 - 1, long_label_w, box_h, long_label_text, fontsize=label_font)
        self._left_text(page, max(margin, rgo_x - 30 - label_box_gap), row1_box_y + (box_h - label_font) / 2 - 1, 30, box_h, "RGO", fontsize=label_font)

        # Row 2: Factura + Número consecutivo
        row2_label_y = row1_box_y + 18
        factura_text = str(datos.get("numero_factura", datos.get("factura", ""))).strip()
        numero_text = str(datos.get("numero_consecutivo", datos.get("consecutivo", ""))).strip()
        fact_font = 9
        label_font = 8
        inner_pad = 12
        fact_text_w = self._estimate_text_width(factura_text, fact_font)
        num_text_w = self._estimate_text_width(numero_text, fact_font)
        min_fact_w = 80
        min_num_w = 100
        fact_w = int(max(min_fact_w, fact_text_w + inner_pad))
        num_w = int(max(min_num_w, num_text_w + inner_pad))
        fact_label_text = "Nro Factura Cuenta de cobro"
        num_label_text = "Número consecutivo de la reclamación"
        fact_label_w = int(max(80, self._estimate_text_width(fact_label_text, label_font) + 8))
        num_label_w = int(max(100, self._estimate_text_width(num_label_text, label_font) + 8))
        label_box_gap = max(8, int(available_w * 0.01))
        group1_w = fact_label_w + label_box_gap + fact_w
        group2_w = num_label_w + label_box_gap + num_w
        mid_gap = max(20, int(available_w * 0.06))
        total_groups_w = group1_w + mid_gap + group2_w
        if total_groups_w > available_w:
            scale = available_w / total_groups_w
            fact_label_w = int(fact_label_w * scale)
            num_label_w = int(num_label_w * scale)
            fact_w = int(fact_w * scale)
            num_w = int(num_w * scale)
            group1_w = fact_label_w + label_box_gap + fact_w
            group2_w = num_label_w + label_box_gap + num_w
            total_groups_w = group1_w + mid_gap + group2_w
        start_groups_x = margin + max(0, (available_w - total_groups_w) / 2)
        fact_label_x = int(start_groups_x)
        fact_x = int(fact_label_x + fact_label_w + label_box_gap)
        group2_start = int(start_groups_x + group1_w + mid_gap)
        num_label_x = group2_start
        num_x = int(num_label_x + num_label_w + label_box_gap)
        row2_box_y = row2_label_y + 10
        self._fill_rect(page, fact_x, row2_box_y, fact_w, box_h, color=(1, 1, 1))
        self._rect(page, fact_x, row2_box_y, fact_w, box_h, color=(0, 0, 0), width=0.6)
        self._fill_rect(page, num_x, row2_box_y, num_w, box_h, color=(1, 1, 1))
        self._rect(page, num_x, row2_box_y, num_w, box_h, color=(0, 0, 0), width=0.6)

        # draw centered text manually (use insert_text for reliability)
        fact_text_w = self._estimate_text_width(factura_text, fact_font)
        num_text_w = self._estimate_text_width(numero_text, fact_font)
        fact_draw_x = fact_x + max(2, (fact_w - fact_text_w) / 2)
        num_draw_x = num_x + max(2, (num_w - num_text_w) / 2)
        fact_draw_y = row2_box_y + (box_h - fact_font) / 2 + fact_font * 0.75
        num_draw_y = row2_box_y + (box_h - fact_font) / 2 + fact_font * 0.75
        if factura_text:
            page.insert_text((fact_draw_x, fact_draw_y), factura_text, fontsize=fact_font, fontname="Times-Roman", color=(0, 0, 0))
            page.insert_text((fact_draw_x + 0.5, fact_draw_y), factura_text, fontsize=fact_font, fontname="Times-Roman", color=(0, 0, 0))
        if numero_text:
            page.insert_text((num_draw_x, num_draw_y), numero_text, fontsize=fact_font, fontname="Times-Roman", color=(0, 0, 0))
            page.insert_text((num_draw_x + 0.5, num_draw_y), numero_text, fontsize=fact_font, fontname="Times-Roman", color=(0, 0, 0))

        # Section II
        section2_y = row2_box_y + box_h + 6
        sec2_x = margin
        sec2_w = page_w - 72
        sec2_h = 12
        self._fill_rect(page, sec2_x, section2_y, sec2_w, sec2_h, color=(0.92, 0.92, 0.92))
        self._rect(page, sec2_x, section2_y, sec2_w, sec2_h, color=(0, 0, 0), width=0.35)
        self._centered_text(page, sec2_x, section2_y, sec2_w, sec2_h, "II. DATOS DE LA INSTITUCIÓN PRESTADORA DE SERVICIOS DE SALUD", fontsize=7, bold=True)

        # Section III header
        section3_y = section2_y + sec2_h + 6
        sec3_x = margin
        sec3_w = page_w - 72
        sec3_h = 12
        self._fill_rect(page, sec3_x, section3_y, sec3_w, sec3_h, color=(0.92, 0.92, 0.92))
        self._rect(page, sec3_x, section3_y, sec3_w, sec3_h, color=(0, 0, 0), width=0.35)
        self._centered_text(page, sec3_x, section3_y, sec3_w, sec3_h, "III. DATOS DE LA VICTIMA DEL EVENTO CATASTRÓFICO O ACCIDENTE DE TRANSITO", fontsize=7, bold=True)

        # Victim fields
        try:
            use_label_font = label_font
        except NameError:
            use_label_font = 8
        field_h = 14
        gap_small = 8
        col_w = int((available_w - gap_small) / 2)
        victim_y = section3_y + sec3_h + 6

        # Nombre
        name_label_w = int(max(60, self._estimate_text_width("Nombre víctima", use_label_font) + 6))
        name_box_x = margin + name_label_w + 6
        self._left_text(page, margin, victim_y, name_label_w, field_h, "Nombre víctima", fontsize=use_label_font)
        self._fill_rect(page, name_box_x, victim_y, col_w - name_label_w - 6, field_h, color=(1, 1, 1))
        self._rect(page, name_box_x, victim_y, col_w - name_label_w - 6, field_h, color=(0, 0, 0), width=0.45)
        self._centered_text(page, name_box_x, victim_y, col_w - name_label_w - 6, field_h, datos.get("victima_nombre", ""), fontsize=8)

        # Documento
        doc_label_w = int(max(50, self._estimate_text_width("Documento", use_label_font) + 6))
        doc_col_x = margin + col_w + gap_small
        doc_box_x = doc_col_x + doc_label_w + 6
        self._left_text(page, doc_col_x, victim_y, doc_label_w, field_h, "Documento", fontsize=use_label_font)
        self._fill_rect(page, doc_box_x, victim_y, col_w - doc_label_w - 6, field_h, color=(1, 1, 1))
        self._rect(page, doc_box_x, victim_y, col_w - doc_label_w - 6, field_h, color=(0, 0, 0), width=0.45)
        self._centered_text(page, doc_box_x, victim_y, col_w - doc_label_w - 6, field_h, datos.get("victima_documento", ""), fontsize=8)

        # Edad y Sexo
        victim_y += field_h + 6
        small_label_w = int(max(40, self._estimate_text_width("Edad", use_label_font) + 6))
        age_box_x = margin + small_label_w + 6
        self._left_text(page, margin, victim_y, small_label_w, field_h, "Edad", fontsize=use_label_font)
        self._fill_rect(page, age_box_x, victim_y, 40, field_h, color=(1, 1, 1))
        self._rect(page, age_box_x, victim_y, 40, field_h, color=(0, 0, 0), width=0.45)
        self._centered_text(page, age_box_x, victim_y, 40, field_h, datos.get("victima_edad", ""), fontsize=8)
        sex_col_x = margin + col_w + gap_small
        sex_label_w = int(max(40, self._estimate_text_width("Sexo", use_label_font) + 6))
        sex_box_x = sex_col_x + sex_label_w + 6
        self._left_text(page, sex_col_x, victim_y, sex_label_w, field_h, "Sexo", fontsize=use_label_font)
        self._fill_rect(page, sex_box_x, victim_y, 40, field_h, color=(1, 1, 1))
        self._rect(page, sex_box_x, victim_y, 40, field_h, color=(0, 0, 0), width=0.45)
        self._centered_text(page, sex_box_x, victim_y, 40, field_h, datos.get("victima_sexo", ""), fontsize=8)

        # Dirección
        victim_y += field_h + 6
        dir_label_w = int(max(70, self._estimate_text_width("Dirección", use_label_font) + 6))
        dir_box_x = margin + dir_label_w + 6
        self._left_text(page, margin, victim_y, dir_label_w, field_h, "Dirección", fontsize=use_label_font)
        self._fill_rect(page, dir_box_x, victim_y, available_w - dir_label_w - 6, field_h, color=(1, 1, 1))
        self._rect(page, dir_box_x, victim_y, available_w - dir_label_w - 6, field_h, color=(0, 0, 0), width=0.45)
        self._centered_text(page, dir_box_x, victim_y, available_w - dir_label_w - 6, field_h, datos.get("victima_direccion", ""), fontsize=8)

        # Código de habilitación (bajo los campos de la víctima)
        label_text = "Código de habilitación del prestador"
        label_y = victim_y + field_h + 8
        self._left_text(page, margin, label_y, int(available_w * 0.5), box_h, label_text, fontsize=use_label_font)
        est_label_w = int(self._estimate_text_width(label_text, use_label_font))
        boxes_start_x = margin + est_label_w + 8
        codigo = self._resolve_codigo_habilitacion(datos)
        print(f"[PDFStamper] resolved codigo_habilitacion: {repr(codigo)}")
        # Draw a small visible debug label to the right (can be removed when confirmed)
        try:
            debug_x = boxes_start_x + 12 * 12 + 8
            self._left_text(page, debug_x, label_y, 200, box_h, f"COD: {codigo}", fontsize=8, fontname="Times-Roman")
        except Exception:
            pass

        self._draw_char_boxes(page, boxes_start_x, label_y, codigo, count=12, box_size=12, gap=0, fontsize=9, border_width=0.45)

        out_path = Path(output_path)
        saved = self._atomic_save(doc, out_path)
        try:
            self._maybe_open_file(saved)
        except Exception:
            pass
        return saved

    # --- helpers ---
    def _resolve_codigo_habilitacion(self, datos: Dict[str, Any]) -> str:
        """Try several keys and patterns to extract the prestador's codigo_habilitacion."""
        if not isinstance(datos, dict):
            return ""
        # common explicit names
        for k in ("codigo_habilitacion", "prestador_codigo_habilitacion", "prestador_codigo", "codigo"):
            v = datos.get(k)
            if v:
                return str(v)

        # scan keys for dotted/backticked forms like setPrestador.`codigo_habilitacion` or setPrestador.codigo_habilitacion
        target = "codigo_habilitacion"
        for key in datos.keys():
            if not isinstance(key, str):
                continue
            knorm = key.replace('`', '').replace('"', '').replace("'", '').replace('.', '_').lower()
            if target in knorm:
                v = datos.get(key)
                if v:
                    return str(v)

        # last-resort: return any plausible alphanumeric value
        for v in datos.values():
            if not v:
                continue
            s = str(v).strip()
            if 4 <= len(s) <= 20 and any(ch.isdigit() for ch in s):
                return s
        return ""

    def _draw_char_boxes(self, page: "fitz.Page", x: float, y: float, text: str, count: int = 12,
                         box_size: float = 14, gap: float = 4, fontsize: float = 8, border_width: float = 0.5) -> float:
        """Draw `count` boxes starting at (x,y) and render each character using `insert_text`.

        Using `insert_text` for single characters avoids textbox rendering differences
        some PDF viewers have with `insert_textbox`.
        """
        txt = str(text or "")
        cur_x = x
        for i in range(count):
            # box
            self._rect(page, cur_x, y, box_size, box_size, color=(0, 0, 0), width=border_width)
            ch = txt[i] if i < len(txt) else ""
            if ch:
                # approximate centering
                ch_w = self._estimate_text_width(ch, fontsize)
                tx = cur_x + max(1, (box_size - ch_w) / 2)
                ty = y + (box_size - fontsize) / 2 + fontsize * 0.75
                page.insert_text((tx, ty), ch, fontsize=fontsize, fontname="Times-Roman", color=(0, 0, 0))
            cur_x += box_size + gap
        return cur_x - gap

    def _rect(self, page: "fitz.Page", x: float, y: float, w: float, h: float, color=(0, 0, 0), width: float = 0.5) -> None:
        r = fitz.Rect(x, y, x + w, y + h)
        page.draw_rect(r, color=color, width=width)

    def _fill_rect(self, page: "fitz.Page", x: float, y: float, w: float, h: float, color=(1, 1, 1)) -> None:
        r = fitz.Rect(x, y, x + w, y + h)
        page.draw_rect(r, color=color, fill=color)

    def _centered_text(self, page: "fitz.Page", x: float, y: float, w: float, h: float, text: str,
                       fontsize: float = 10, fontname: str = "Times-Roman", color=(0, 0, 0), bold: bool = False) -> None:
        r = fitz.Rect(x, y, x + w, y + h)
        page.insert_textbox(r, text or "", fontsize=fontsize, fontname=fontname, align=fitz.TEXT_ALIGN_CENTER, color=color)
        if bold and (text or ""):
            shift = 0.6
            r2 = fitz.Rect(x + shift, y, x + w + shift, y + h)
            page.insert_textbox(r2, text or "", fontsize=fontsize, fontname=fontname, align=fitz.TEXT_ALIGN_CENTER, color=color)

    def _left_text(self, page: "fitz.Page", x: float, y: float, w: float, h: float, text: str,
                   fontsize: float = 10, fontname: str = "Times-Roman", color=(0, 0, 0), align: str = "left") -> None:
        r = fitz.Rect(x, y, x + w, y + h)
        align_flag = fitz.TEXT_ALIGN_LEFT if align == "left" else fitz.TEXT_ALIGN_RIGHT
        page.insert_textbox(r, text or "", fontsize=fontsize, fontname=fontname, align=align_flag, color=color)

    def _atomic_save(self, doc: "fitz.Document", out_path: Path) -> str:
        out_path = Path(out_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            tmpf = tempfile.NamedTemporaryFile(delete=False, dir=str(out_path.parent), prefix=out_path.stem + "_tmp_", suffix=".pdf")
            tmp_path = Path(tmpf.name)
            tmpf.close()
            doc.save(str(tmp_path))
            doc.close()
            try:
                os.replace(str(tmp_path), str(out_path))
                print(f"[PDFStamper] Guardado correcto: {out_path}")
                return str(out_path)
            except Exception:
                alt = out_path.with_name(f"{out_path.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
                try:
                    os.replace(str(tmp_path), str(alt))
                    print(f"[PDFStamper] No se pudo sobrescribir {out_path}; guardado en archivo alternativo: {alt}")
                    return str(alt)
                except Exception:
                    print(f"[PDFStamper] Guardado en temporal {tmp_path}, pero no se pudo mover a {out_path} ni a {alt}.")
                    return str(tmp_path)
        except Exception as e:
            try:
                now = datetime.now().strftime("%Y%m%d_%H%M%S")
                alt = out_path.with_name(f"{out_path.stem}_{now}.pdf")
                doc.save(str(alt))
                doc.close()
                print(f"[PDFStamper] Fallback directo: guardado en {alt}")
                return str(alt)
            except Exception as e2:
                try:
                    doc.close()
                except Exception:
                    pass
                raise RuntimeError(f"No fue posible guardar el PDF. Errores: {e} / {e2}")

    def _maybe_open_file(self, path: str) -> None:
        """Attempt to open the file in the OS default viewer (best-effort)."""
        try:
            p = Path(path)
            if os.name == "nt":
                os.startfile(str(p))
                return
            if sys.platform == "darwin":
                subprocess.run(["open", str(p)], check=False)
                return
            subprocess.run(["xdg-open", str(p)], check=False)
        except Exception:
            pass

    def _estimate_text_width(self, text: str, fontsize: float) -> float:
        if not text:
            return 0.0
        avg_char = fontsize * 0.55
        return len(str(text)) * avg_char
