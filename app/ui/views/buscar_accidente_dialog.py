"""
Diálogo para buscar accidentes.
"""
from typing import Optional, Dict, Any
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QGroupBox,
    QGridLayout,
    QAbstractItemView,
)
from PySide6.QtCore import Qt, Signal
from datetime import datetime


class BuscarAccidenteDialog(QDialog):
    """Diálogo para buscar accidentes."""
    
    accidente_seleccionado = Signal(int)  # Emite el ID del accidente
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.accidente_id_seleccionado = None
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura la interfaz."""
        self.setWindowTitle("Buscar Accidente")
        self.setMinimumSize(1000, 600)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Grupo de filtros
        filtros_group = self._create_filtros_group()
        layout.addWidget(filtros_group)
        
        # Tabla de resultados
        self.table_resultados = self._create_tabla()
        layout.addWidget(self.table_resultados)
        
        # Botones
        botones_layout = self._create_botones()
        layout.addLayout(botones_layout)
        
        # Aplicar estilos
        self.setStyleSheet("""
            QDialog {
                background-color: #F5F5F5;
            }
            QGroupBox {
                background-color: white;
                border: 1px solid #CCCCCC;
                border-radius: 5px;
                margin-top: 10px;
                padding: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QLineEdit {
                padding: 5px;
                border: 1px solid #CCCCCC;
                border-radius: 3px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #4A90B5;
            }
            QPushButton {
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton#btn_buscar {
                background-color: #4A90B5;
                color: white;
            }
            QPushButton#btn_buscar:hover {
                background-color: #3A7A9F;
            }
            QPushButton#btn_limpiar {
                background-color: #E0E0E0;
                color: #333333;
            }
            QPushButton#btn_limpiar:hover {
                background-color: #D0D0D0;
            }
            QPushButton#btn_seleccionar {
                background-color: #28A745;
                color: white;
            }
            QPushButton#btn_seleccionar:hover {
                background-color: #218838;
            }
            QPushButton#btn_cancelar {
                background-color: #DC3545;
                color: white;
            }
            QPushButton#btn_cancelar:hover {
                background-color: #C82333;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #CCCCCC;
                border-radius: 3px;
                gridline-color: #E0E0E0;
            }
            QHeaderView::section {
                background-color: #4A90B5;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)
    
    def _create_filtros_group(self) -> QGroupBox:
        """Crea el grupo de filtros."""
        group = QGroupBox("Filtros de Búsqueda")
        grid = QGridLayout()
        grid.setSpacing(10)
        
        # ID Accidente
        grid.addWidget(QLabel("ID Accidente:"), 0, 0)
        self.txt_id = QLineEdit()
        self.txt_id.setPlaceholderText("Ej: 1")
        self.txt_id.setMaximumWidth(120)
        grid.addWidget(self.txt_id, 0, 1)
        
        # Consecutivo
        grid.addWidget(QLabel("Consecutivo:"), 0, 2)
        self.txt_consecutivo = QLineEdit()
        self.txt_consecutivo.setPlaceholderText("Ej: 000000000008")
        self.txt_consecutivo.setMaximumWidth(150)
        grid.addWidget(self.txt_consecutivo, 0, 3)
        
        # Número Factura
        grid.addWidget(QLabel("Nro. Factura:"), 1, 0)
        self.txt_factura = QLineEdit()
        self.txt_factura.setPlaceholderText("Ej: 123123")
        self.txt_factura.setMaximumWidth(150)
        grid.addWidget(self.txt_factura, 1, 1)
        
        # Número Documento Víctima
        grid.addWidget(QLabel("Doc. Víctima:"), 1, 2)
        self.txt_documento = QLineEdit()
        self.txt_documento.setPlaceholderText("Ej: 1122334455")
        self.txt_documento.setMaximumWidth(150)
        grid.addWidget(self.txt_documento, 1, 3)
        
        # Botones de acción de filtros
        botones_layout = QHBoxLayout()
        
        self.btn_buscar = QPushButton("🔍 Buscar")
        self.btn_buscar.setObjectName("btn_buscar")
        self.btn_buscar.setMinimumWidth(120)
        self.btn_buscar.clicked.connect(self._on_buscar)
        botones_layout.addWidget(self.btn_buscar)
        
        self.btn_limpiar = QPushButton("🔄 Limpiar Filtros")
        self.btn_limpiar.setObjectName("btn_limpiar")
        self.btn_limpiar.clicked.connect(self._on_limpiar_filtros)
        botones_layout.addWidget(self.btn_limpiar)
        
        botones_layout.addStretch()
        
        grid.addLayout(botones_layout, 2, 0, 1, 4)
        
        group.setLayout(grid)
        return group
    
    def _create_tabla(self) -> QTableWidget:
        """Crea la tabla de resultados."""
        table = QTableWidget()
        table.setColumnCount(11)
        table.setHorizontalHeaderLabels([
            "ID",
            "Consecutivo",
            "Factura",
            "Fecha",
            "Hora",
            "Placa",
            "Tipo Doc",
            "Nro. Doc",
            "Primer Nombre",
            "Primer Apellido",
            "Segundo Apellido"
        ])
        
        # Configuración de la tabla
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setAlternatingRowColors(True)
        
        # Ajustar columnas
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Consecutivo
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Factura
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Fecha
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Hora
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Placa
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)  # Tipo Doc
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)  # Nro Doc
        header.setSectionResizeMode(8, QHeaderView.ResizeMode.Stretch)  # Nombre
        header.setSectionResizeMode(9, QHeaderView.ResizeMode.Stretch)  # Apellido
        header.setSectionResizeMode(10, QHeaderView.ResizeMode.Stretch)  # 2do Apellido
        
        # Doble clic para seleccionar
        table.doubleClicked.connect(self._on_seleccionar)
        
        return table
    
    def _create_botones(self) -> QHBoxLayout:
        """Crea los botones del diálogo."""
        layout = QHBoxLayout()
        layout.setSpacing(10)
        
        layout.addStretch()
        
        self.btn_seleccionar = QPushButton("✅ Seleccionar")
        self.btn_seleccionar.setObjectName("btn_seleccionar")
        self.btn_seleccionar.setMinimumWidth(120)
        self.btn_seleccionar.clicked.connect(self._on_seleccionar)
        self.btn_seleccionar.setEnabled(False)
        layout.addWidget(self.btn_seleccionar)
        
        self.btn_cancelar = QPushButton("❌ Cancelar")
        self.btn_cancelar.setObjectName("btn_cancelar")
        self.btn_cancelar.setMinimumWidth(120)
        self.btn_cancelar.clicked.connect(self.reject)
        layout.addWidget(self.btn_cancelar)
        
        return layout
    
    def _on_buscar(self):
        """Maneja el evento de búsqueda."""
        filtros = self.get_filtros()
        
        # Verificar que al menos un filtro esté presente
        if not any(filtros.values()):
            return
        
        # Emitir señal personalizada si es necesario
        # Por ahora, el presenter manejará la búsqueda
        from app.ui.presenters.buscar_accidente_presenter import BuscarAccidentePresenter
        if hasattr(self, 'presenter'):
            self.presenter.buscar_accidentes(filtros)
    
    def _on_limpiar_filtros(self):
        """Limpia los filtros."""
        self.txt_id.clear()
        self.txt_consecutivo.clear()
        self.txt_factura.clear()
        self.txt_documento.clear()
        self.table_resultados.setRowCount(0)
        self.btn_seleccionar.setEnabled(False)
    
    def _on_seleccionar(self):
        """Maneja la selección de un accidente."""
        fila = self.table_resultados.currentRow()
        if fila >= 0:
            id_item = self.table_resultados.item(fila, 0)
            if id_item:
                self.accidente_id_seleccionado = int(id_item.text())
                self.accidente_seleccionado.emit(self.accidente_id_seleccionado)
                self.accept()
    
    def get_filtros(self) -> Dict[str, Any]:
        """Obtiene los filtros del formulario."""
        filtros = {}
        
        if self.txt_id.text().strip():
            filtros["id"] = int(self.txt_id.text().strip())
        
        if self.txt_consecutivo.text().strip():
            filtros["consecutivo"] = self.txt_consecutivo.text().strip()
        
        if self.txt_factura.text().strip():
            filtros["factura"] = self.txt_factura.text().strip()
        
        if self.txt_documento.text().strip():
            filtros["documento"] = self.txt_documento.text().strip()
        
        return filtros
    
    def cargar_resultados(self, accidentes: list):
        """Carga los resultados en la tabla."""
        self.table_resultados.setRowCount(0)
        
        for acc in accidentes:
            row = self.table_resultados.rowCount()
            self.table_resultados.insertRow(row)
            
            # ID
            self.table_resultados.setItem(row, 0, QTableWidgetItem(str(acc.get("id", ""))))
            
            # Consecutivo
            self.table_resultados.setItem(row, 1, QTableWidgetItem(acc.get("consecutivo", "")))
            
            # Factura
            self.table_resultados.setItem(row, 2, QTableWidgetItem(acc.get("factura", "")))
            
            # Fecha
            fecha = acc.get("fecha_evento")
            fecha_str = fecha.strftime("%d/%m/%Y") if fecha else ""
            self.table_resultados.setItem(row, 3, QTableWidgetItem(fecha_str))
            
            # Hora
            self.table_resultados.setItem(row, 4, QTableWidgetItem(acc.get("hora_evento", "")))
            
            # Placa
            self.table_resultados.setItem(row, 5, QTableWidgetItem(acc.get("placa", "") or ""))
            
            # Tipo Doc
            self.table_resultados.setItem(row, 6, QTableWidgetItem(acc.get("tipo_identificacion", "")))
            
            # Nro Doc
            self.table_resultados.setItem(row, 7, QTableWidgetItem(acc.get("numero_identificacion", "")))
            
            # Nombres
            self.table_resultados.setItem(row, 8, QTableWidgetItem(acc.get("primer_nombre", "")))
            self.table_resultados.setItem(row, 9, QTableWidgetItem(acc.get("primer_apellido", "")))
            self.table_resultados.setItem(row, 10, QTableWidgetItem(acc.get("segundo_apellido", "") or ""))
        
        # Habilitar botón de selección si hay resultados
        self.btn_seleccionar.setEnabled(self.table_resultados.rowCount() > 0)
        
        # Seleccionar primera fila
        if self.table_resultados.rowCount() > 0:
            self.table_resultados.selectRow(0)
