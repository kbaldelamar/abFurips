"""
Diálogo para seleccionar un vehículo de una lista.
"""
from typing import Optional, List, Dict, Any
from datetime import date
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QLabel,
    QHeaderView,
    QAbstractItemView,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QBrush


class SeleccionarVehiculoDialog(QDialog):
    """Diálogo para seleccionar un vehículo de una lista."""
    
    def __init__(self, vehiculos: List[Dict[str, Any]], parent=None):
        super().__init__(parent)
        self.vehiculos = vehiculos
        self.vehiculo_seleccionado: Optional[Dict[str, Any]] = None
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura la interfaz del diálogo."""
        self.setWindowTitle("Seleccionar Vehículo")
        self.setMinimumWidth(700)
        self.setMinimumHeight(400)
        
        layout = QVBoxLayout(self)
        
        # Título
        lbl_titulo = QLabel("El propietario tiene varios vehículos registrados.\nSeleccione el vehículo que desea usar:")
        lbl_titulo.setStyleSheet("font-weight: bold; font-size: 11pt; margin-bottom: 10px;")
        layout.addWidget(lbl_titulo)
        
        # Leyenda
        lbl_leyenda = QLabel("ℹ️ Las filas en rojo indican pólizas vencidas")
        lbl_leyenda.setStyleSheet("color: #666; font-size: 9pt; margin-bottom: 5px;")
        layout.addWidget(lbl_leyenda)
        
        # Tabla de vehículos
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Placa", "Marca", "Tipo", "Aseguradora", "Nro. Póliza", "Vigencia Fin"
        ])
        
        # Configurar tabla
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        
        # Ajustar columnas
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Placa
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # Marca
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)  # Tipo
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Aseguradora
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)  # Póliza
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)  # Vigencia
        
        # Doble clic para seleccionar
        self.table.doubleClicked.connect(self._on_aceptar)
        
        layout.addWidget(self.table)
        
        # Llenar tabla
        self._llenar_tabla()
        
        # Botones
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.btn_aceptar = QPushButton("✓ Seleccionar")
        self.btn_aceptar.setMinimumWidth(120)
        self.btn_aceptar.clicked.connect(self._on_aceptar)
        self.btn_aceptar.setDefault(True)
        btn_layout.addWidget(self.btn_aceptar)
        
        btn_cancelar = QPushButton("✗ Cancelar")
        btn_cancelar.setMinimumWidth(120)
        btn_cancelar.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancelar)
        
        layout.addLayout(btn_layout)
    
    def _llenar_tabla(self):
        """Llena la tabla con los vehículos."""
        self.table.setRowCount(len(self.vehiculos))
        
        fecha_actual = date.today()
        
        for row, vehiculo in enumerate(self.vehiculos):
            # Verificar si la póliza está vencida
            vigencia_fin = vehiculo.get("vigencia_fin")
            poliza_vencida = False
            
            if vigencia_fin:
                # Convertir a date si es necesario
                if isinstance(vigencia_fin, str):
                    from datetime import datetime
                    try:
                        vigencia_fin = datetime.strptime(vigencia_fin, "%Y-%m-%d").date()
                    except:
                        pass
                
                if isinstance(vigencia_fin, date) and vigencia_fin < fecha_actual:
                    poliza_vencida = True
            
            # Color de fondo para fila vencida
            color_fondo = QBrush(QColor(255, 200, 200)) if poliza_vencida else QBrush(Qt.GlobalColor.white)
            
            # ID
            item = QTableWidgetItem(str(vehiculo.get("id", "")))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setBackground(color_fondo)
            self.table.setItem(row, 0, item)
            
            # Placa
            item = QTableWidgetItem(vehiculo.get("placa", ""))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setData(Qt.ItemDataRole.UserRole, vehiculo)  # Guardar datos completos
            item.setBackground(color_fondo)
            self.table.setItem(row, 1, item)
            
            # Marca
            item = QTableWidgetItem(vehiculo.get("marca", ""))
            item.setBackground(color_fondo)
            self.table.setItem(row, 2, item)
            
            # Tipo
            item = QTableWidgetItem(vehiculo.get("tipo_vehiculo", ""))
            item.setBackground(color_fondo)
            self.table.setItem(row, 3, item)
            
            # Aseguradora
            item = QTableWidgetItem(vehiculo.get("aseguradora_codigo", ""))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setBackground(color_fondo)
            self.table.setItem(row, 4, item)
            
            # Número de póliza
            item = QTableWidgetItem(vehiculo.get("numero_poliza", ""))
            item.setBackground(color_fondo)
            self.table.setItem(row, 5, item)
            
            # Vigencia Fin (con indicador de vencimiento)
            if vigencia_fin:
                if isinstance(vigencia_fin, date):
                    fecha_texto = vigencia_fin.strftime("%d/%m/%Y")
                else:
                    fecha_texto = str(vigencia_fin)
                
                if poliza_vencida:
                    fecha_texto += " ⚠️ VENCIDA"
                
                item = QTableWidgetItem(fecha_texto)
            else:
                item = QTableWidgetItem("Sin fecha")
            
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setBackground(color_fondo)
            
            # Texto en rojo si está vencida
            if poliza_vencida:
                item.setForeground(QBrush(QColor(200, 0, 0)))
            
            self.table.setItem(row, 6, item)
        
        # Seleccionar primera fila por defecto
        if self.vehiculos:
            self.table.selectRow(0)
    
    def _on_aceptar(self):
        """Maneja el evento de aceptar."""
        current_row = self.table.currentRow()
        if current_row >= 0:
            # Obtener datos del vehículo desde el item de la columna placa
            item = self.table.item(current_row, 1)
            self.vehiculo_seleccionado = item.data(Qt.ItemDataRole.UserRole)
            self.accept()
    
    def get_vehiculo_seleccionado(self) -> Optional[Dict[str, Any]]:
        """Retorna el vehículo seleccionado."""
        return self.vehiculo_seleccionado
