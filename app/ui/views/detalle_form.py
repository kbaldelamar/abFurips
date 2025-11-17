"""
Formulario de tabla de detalles (FURIPS2).
"""
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QHeaderView,
)
from PySide6.QtCore import Signal


class DetalleForm(QWidget):
    """Formulario para gestionar los detalles (FURIPS2)."""
    
    # Señales
    agregar_detalle_signal = Signal()
    editar_detalle_signal = Signal(int)
    eliminar_detalle_signal = Signal(int)
    
    def __init__(self):
        super().__init__()
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura la interfaz."""
        layout = QVBoxLayout(self)
        
        # Tabla de detalles
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(8)
        self.tabla.setHorizontalHeaderLabels([
            "Tipo Servicio",
            "Código",
            "Descripción",
            "Cantidad",
            "Valor Unitario",
            "Valor Facturado",
            "Valor Reclamado",
            "Acciones"
        ])
        
        # Ajustar columnas
        header = self.tabla.horizontalHeader()
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # Descripción
        
        layout.addWidget(self.tabla)
        
        # Botones
        button_layout = QHBoxLayout()
        
        self.btn_agregar = QPushButton("Agregar Detalle")
        self.btn_agregar.clicked.connect(self.agregar_detalle_signal.emit)
        button_layout.addWidget(self.btn_agregar)
        
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
    
    def cargar_detalles(self, detalles: list):
        """Carga los detalles en la tabla."""
        self.tabla.setRowCount(0)
        
        for detalle in detalles:
            self._agregar_fila(detalle)
    
    def _agregar_fila(self, detalle: dict):
        """Agrega una fila a la tabla."""
        row = self.tabla.rowCount()
        self.tabla.insertRow(row)
        
        self.tabla.setItem(row, 0, QTableWidgetItem(detalle.get("tipo_servicio", "")))
        self.tabla.setItem(row, 1, QTableWidgetItem(detalle.get("codigo_servicio", "")))
        self.tabla.setItem(row, 2, QTableWidgetItem(detalle.get("descripcion", "")))
        self.tabla.setItem(row, 3, QTableWidgetItem(str(detalle.get("cantidad", 0))))
        self.tabla.setItem(row, 4, QTableWidgetItem(str(detalle.get("valor_unitario", 0))))
        self.tabla.setItem(row, 5, QTableWidgetItem(str(detalle.get("valor_facturado", 0))))
        self.tabla.setItem(row, 6, QTableWidgetItem(str(detalle.get("valor_reclamado", 0))))
        
        # Botones de acción
        btn_widget = QWidget()
        btn_layout = QHBoxLayout(btn_widget)
        btn_layout.setContentsMargins(4, 4, 4, 4)
        
        btn_editar = QPushButton("Editar")
        btn_editar.clicked.connect(lambda: self.editar_detalle_signal.emit(row))
        btn_layout.addWidget(btn_editar)
        
        btn_eliminar = QPushButton("Eliminar")
        btn_eliminar.clicked.connect(lambda: self.eliminar_detalle_signal.emit(row))
        btn_layout.addWidget(btn_eliminar)
        
        self.tabla.setCellWidget(row, 7, btn_widget)
    
    def limpiar_tabla(self):
        """Limpia la tabla."""
        self.tabla.setRowCount(0)
