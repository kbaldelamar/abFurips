"""
Dialog para buscar accidentes y enviar comando de impresión.
"""
from typing import Any, Dict, List, Optional

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QWidget,
    QHeaderView,
    QSizePolicy,
    QAbstractItemView,
)
from PySide6.QtCore import Signal, Qt

from app.config.db import get_db_session
from app.data.repositories.accidente_repo import AccidenteRepository


class BuscarImprimirDialog(QWidget):
    """Panel para buscar accidentes y permitir imprimir desde la lista.

    Este widget se puede incrustar en la ventana principal (no es modal).
    """

    imprimir_accidente = Signal(int)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        # Si se muestra como ventana independiente, el título es útil;
        # cuando se incrusta, la ventana principal maneja el título.
        try:
            self.setWindowTitle("Buscar accidentes - Imprimir")
        except Exception:
            pass
        self.resize(900, 500)

        # Aplicar estilo similar al formulario de diligenciar
        self.setStyleSheet("""
            QWidget {
                background-color: #E8F4F8;
                font-family: Segoe UI;
                font-size: 9pt;
            }
            QLineEdit {
                padding: 5px;
                border: 1px solid #B0C4DE;
                border-radius: 3px;
                background-color: white;
            }
            QPushButton {
                background-color: #4A90B5;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #5BA0C5; }
            QTableWidget {
                background-color: white;
                gridline-color: #DDEBF5;
            }
            QHeaderView::section {
                background-color: #D0E8F0;
                padding: 4px;
                border: 1px solid #B0C4DE;
            }
        """)

        self._build_ui()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)

        # Filtros
        form = QFormLayout()
        self.input_consecutivo = QLineEdit()
        self.input_factura = QLineEdit()
        self.input_documento = QLineEdit()

        form.addRow("Consecutivo:", self.input_consecutivo)
        form.addRow("Factura:", self.input_factura)
        form.addRow("Documento víctima:", self.input_documento)

        btn_layout = QHBoxLayout()
        self.btn_buscar = QPushButton("Buscar")
        self.btn_cerrar = QPushButton("Cerrar")
        btn_layout.addWidget(self.btn_buscar)
        btn_layout.addWidget(self.btn_cerrar)

        main_layout.addLayout(form)
        main_layout.addLayout(btn_layout)

        # Tabla de resultados
        self.table = QTableWidget(0, 10)
        self.table.setHorizontalHeaderLabels([
            "ID",
            "Consecutivo",
            "Factura",
            "Fecha",
            "Hora",
            "Tipo ID",
            "Documento",
            "Nombre",
            "Resumen relaciones",
            "Acción",
        ])
        # Ocultar columna ID y encabezado vertical (números de fila)
        self.table.setColumnHidden(0, True)
        self.table.verticalHeader().setVisible(False)
        # No usar colores alternados (evita filas en tono grisáceo)
        self.table.setAlternatingRowColors(False)
        self.table.setSortingEnabled(True)
        # Comportamiento de selección y edición
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # Ajustes de ancho de columnas: usar ResizeToContents por defecto
        # y Stretch para columnas de texto largo para ocupar el espacio disponible
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)   # Consecutivo
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)   # Factura
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)   # Fecha
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)   # Hora
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)   # Tipo ID
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)   # Documento
        # Nombre y Resumen: expanden para llenar el espacio disponible
        header.setSectionResizeMode(7, QHeaderView.Stretch)            # Nombre
        header.setSectionResizeMode(8, QHeaderView.Stretch)            # Resumen relaciones
        header.setSectionResizeMode(9, QHeaderView.ResizeToContents)   # Acción (botones)
        header.setStretchLastSection(False)

        # Permitir que la tabla expanda en el layout y ocupe todo el espacio
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # Anchos mínimos para columnas expansibles para evitar celdas demasiado estrechas
        self.table.setColumnWidth(7, 200)
        self.table.setColumnWidth(8, 180)
        main_layout.addWidget(self.table)

        # Conexiones
        self.btn_buscar.clicked.connect(self.on_buscar)
        self.btn_cerrar.clicked.connect(self._on_cerrar)

    def _on_cerrar(self):
        # Si el panel está embebido, limpiar y volver al contenido previo
        self.hide()
        # Si el parent es la ventana principal, restaurar el welcome
        from app.ui.views.main_window import MainWindow
        if isinstance(self.parent(), MainWindow):
            self.parent()._create_welcome_widget()

    def on_buscar(self):
        filtros: Dict[str, Any] = {}
        if self.input_consecutivo.text().strip():
            filtros['consecutivo'] = self.input_consecutivo.text().strip()
        if self.input_factura.text().strip():
            filtros['factura'] = self.input_factura.text().strip()
        if self.input_documento.text().strip():
            filtros['documento'] = self.input_documento.text().strip()

        # Ejecutar consulta en contexto de sesión
        with get_db_session() as session:
            repo = AccidenteRepository(session)
            rows = repo.buscar_accidentes_con_victima(filtros)
            # Desactivar ordenamiento y actualizaciones visuales durante la carga
            was_sorting = self.table.isSortingEnabled()
            self.table.setSortingEnabled(False)
            self.table.setUpdatesEnabled(False)

            # Limpiar completamente la tabla antes de poblarla
            self.table.clearContents()
            # Fijar el número de filas para evitar inserciones desajustadas
            self.table.setRowCount(len(rows))

            for row_idx, r in enumerate(rows):
                # Depuración: imprimir lo que vamos a pintar
                try:
                    print(f"[BuscarImprimirDialog] Pintando fila {row_idx}")
                except Exception:
                    pass
                # r puede ser Row/KeyedTuple o tupla; manejar ambos casos
                try:
                    accidente_id = getattr(r, 'id', None) or r[0]
                except Exception:
                    accidente_id = r[0]

                consecutivo = getattr(r, 'numero_consecutivo', None) or r[1]
                factura = getattr(r, 'numero_factura', None) or r[2]
                fecha = getattr(r, 'fecha_evento', None) or r[3]
                hora = getattr(r, 'hora_evento', None) or r[4]
                tipo_id = getattr(r, 'tipo_identificacion', None) or r[5]
                documento = getattr(r, 'numero_identificacion', None) or r[6]
                nombres = (
                    f"{getattr(r, 'primer_nombre', None) or r[7]} "
                    f"{getattr(r, 'segundo_nombre', '') or (r[8] if len(r) > 8 else '')} "
                    f"{getattr(r, 'primer_apellido', None) or (r[9] if len(r) > 9 else '')} "
                    f"{getattr(r, 'segundo_apellido', '') or (r[10] if len(r) > 10 else '')}"
                ).strip()

                resumen = repo.resumen_relaciones(accidente_id)
                resumen_txt = (
                    f"V:{resumen.get('victimas',0)} "
                    f"C:{resumen.get('conductores',0)} "
                    f"P:{resumen.get('propietarios',0)} "
                    f"D:{resumen.get('detalles',0)} "
                    f"T:{resumen.get('totales',0)} "
                    f"M:{resumen.get('medicos_tratantes',0)} "
                    f"R:{resumen.get('remisiones',0)}"
                )

                self.table.setItem(row_idx, 0, QTableWidgetItem(str(accidente_id)))
                self.table.setItem(row_idx, 1, QTableWidgetItem(str(consecutivo)))
                self.table.setItem(row_idx, 2, QTableWidgetItem(str(factura)))
                self.table.setItem(row_idx, 3, QTableWidgetItem(str(fecha)))
                self.table.setItem(row_idx, 4, QTableWidgetItem(str(hora)))
                self.table.setItem(row_idx, 5, QTableWidgetItem(str(tipo_id)))
                self.table.setItem(row_idx, 6, QTableWidgetItem(str(documento)))
                self.table.setItem(row_idx, 7, QTableWidgetItem(str(nombres)))
                self.table.setItem(row_idx, 8, QTableWidgetItem(resumen_txt))

                # Botón imprimir
                btn = QPushButton("Imprimir")
                btn.clicked.connect(self._make_imprimir_handler(accidente_id))

                self.table.setCellWidget(row_idx, 9, btn)
                # Depuración: confirmar textos escritos en celdas
                try:
                    texts = [self.table.item(row_idx, c).text() if self.table.item(row_idx, c) else "<None>" for c in range(self.table.columnCount())]
                    print(f"[BuscarImprimirDialog] Fila {row_idx} valores: {texts}")
                except Exception:
                    pass

            # Restaurar actualizaciones y ordenamiento
            self.table.setUpdatesEnabled(True)
            self.table.setSortingEnabled(was_sorting)

            # Eliminar filas que quedan completamente vacías (por si hubo inconsistencias)
            # Recorremos de abajo hacia arriba para poder eliminar por índice
            for r_idx in range(self.table.rowCount() - 1, -1, -1):
                empty = True
                for c in range(self.table.columnCount()):
                    item = self.table.item(r_idx, c)
                    widget = self.table.cellWidget(r_idx, c)
                    if widget is not None:
                        empty = False
                        break
                    if item is not None and item.text().strip() != "":
                        empty = False
                        break
                if empty:
                    self.table.removeRow(r_idx)

            # Si no hay resultados, asegurarse que no queden filas vacías
            if len(rows) == 0:
                self.table.setRowCount(0)

            # Ajustar filas y columnas de forma estable
            try:
                header.resizeSections(QHeaderView.ResizeToContents)
            except Exception:
                pass
            self.table.resizeRowsToContents()

    def _make_imprimir_handler(self, accidente_id: int):
        def handler():
            # Emitir señal para que el presenter o quien abra el dialog maneje la impresión
            self.imprimir_accidente.emit(accidente_id)

        return handler
