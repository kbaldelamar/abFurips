"""
Formulario para gestión del vehículo.
"""
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QGridLayout,
    QLineEdit,
    QComboBox,
    QDateEdit,
    QPushButton,
    QLabel,
    QScrollArea,
    QMessageBox,
)
from PySide6.QtCore import Signal, QDate, Qt, QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator


class VehiculoForm(QWidget):
    """Formulario para gestión del vehículo del accidente."""
    
    # Señales
    buscar_vehiculo_signal = Signal(str)  # placa
    guardar_vehiculo_signal = Signal(dict)
    actualizar_vehiculo_signal = Signal(dict)
    anular_vehiculo_signal = Signal(int)  # vehiculo_id
    
    def __init__(self):
        super().__init__()
        self.vehiculo_id_actual = None
        # Variables para control de cambio de propietario
        self.vehiculo_cambiar_propietario = False
        self.vehiculo_propietario_bd = None
        self.propietario_recien_actualizado = False
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura la interfaz."""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(5)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Crear área scrolleable
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Widget contenedor
        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)
        layout.setSpacing(5)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Grupo: Datos del Vehículo
        group_vehiculo = self._create_vehiculo_group()
        layout.addWidget(group_vehiculo)
        
        # Botones de acción
        btn_layout = self._create_buttons()
        layout.addLayout(btn_layout)
        
        layout.addStretch()
        
        scroll.setWidget(scroll_widget)
        main_layout.addWidget(scroll, 1)
    
    def _create_vehiculo_group(self) -> QGroupBox:
        """Crea el grupo de datos del vehículo."""
        group = QGroupBox("🚗 Datos del Vehículo")
        grid = QGridLayout()
        grid.setSpacing(8)
        grid.setContentsMargins(8, 10, 8, 8)
        
        # Configurar proporciones de columnas
        grid.setColumnStretch(0, 0)  # Label
        grid.setColumnStretch(1, 1)  # Campo
        grid.setColumnStretch(2, 0)  # Label
        grid.setColumnStretch(3, 1)  # Campo
        
        # Validadores
        validator_placa = QRegularExpressionValidator(QRegularExpression(r"^[A-Za-z0-9]*$"))
        validator_alfanumerico = QRegularExpressionValidator(QRegularExpression(r"^[A-Za-z0-9\s]*$"))
        
        # Fila 0: Búsqueda por placa
        lbl = QLabel("Placa:")
        lbl.setMaximumWidth(80)
        grid.addWidget(lbl, 0, 0)
        self.txt_placa = QLineEdit()
        self.txt_placa.setMinimumWidth(130)
        self.txt_placa.setMaxLength(10)
        self.txt_placa.setPlaceholderText("ABC123")
        self.txt_placa.setValidator(validator_placa)
        grid.addWidget(self.txt_placa, 0, 1)
        
        self.btn_buscar = QPushButton("🔍 Buscar")
        self.btn_buscar.setFixedWidth(90)
        self.btn_buscar.clicked.connect(self._on_buscar_vehiculo)
        grid.addWidget(self.btn_buscar, 0, 2)
        
        self.lbl_vehiculo_encontrado = QLabel("")
        self.lbl_vehiculo_encontrado.setStyleSheet("color: green; font-weight: bold; font-size: 9pt;")
        grid.addWidget(self.lbl_vehiculo_encontrado, 0, 3)
        
        # Fila 1: Marca y Tipo de Vehículo
        lbl = QLabel("Marca:")
        lbl.setMaximumWidth(80)
        grid.addWidget(lbl, 1, 0)
        self.txt_marca = QLineEdit()
        self.txt_marca.setMinimumWidth(130)
        self.txt_marca.setMaxLength(30)
        self.txt_marca.setPlaceholderText("Chevrolet, Toyota, etc.")
        grid.addWidget(self.txt_marca, 1, 1)
        
        lbl = QLabel("Tipo Vehículo:")
        lbl.setMaximumWidth(100)
        grid.addWidget(lbl, 1, 2)
        self.combo_tipo_vehiculo = QComboBox()
        self.combo_tipo_vehiculo.setMinimumWidth(160)
        grid.addWidget(self.combo_tipo_vehiculo, 1, 3)
        
        # Fila 2: Aseguradora y Número de Póliza
        lbl = QLabel("Aseguradora:")
        lbl.setMaximumWidth(80)
        grid.addWidget(lbl, 2, 0)
        self.txt_aseguradora = QLineEdit()
        self.txt_aseguradora.setMinimumWidth(130)
        self.txt_aseguradora.setMaxLength(6)
        self.txt_aseguradora.setPlaceholderText("AT0012")
        self.txt_aseguradora.setValidator(validator_alfanumerico)
        grid.addWidget(self.txt_aseguradora, 2, 1)
        
        lbl = QLabel("Nro. Póliza:")
        lbl.setMaximumWidth(100)
        grid.addWidget(lbl, 2, 2)
        self.txt_numero_poliza = QLineEdit()
        self.txt_numero_poliza.setMinimumWidth(160)
        self.txt_numero_poliza.setMaxLength(20)
        self.txt_numero_poliza.setPlaceholderText("SOAT-456789")
        self.txt_numero_poliza.setValidator(validator_alfanumerico)
        grid.addWidget(self.txt_numero_poliza, 2, 3)
        
        # Fila 3: Vigencia Póliza
        lbl = QLabel("Vigencia Inicio:")
        lbl.setMaximumWidth(100)
        grid.addWidget(lbl, 3, 0)
        self.date_vigencia_inicio = QDateEdit()
        self.date_vigencia_inicio.setCalendarPopup(True)
        self.date_vigencia_inicio.setDisplayFormat("dd/MM/yyyy")
        self.date_vigencia_inicio.setMinimumWidth(130)
        self.date_vigencia_inicio.dateChanged.connect(self._on_vigencia_inicio_changed)
        grid.addWidget(self.date_vigencia_inicio, 3, 1)
        
        lbl = QLabel("Vigencia Fin:")
        lbl.setMaximumWidth(100)
        grid.addWidget(lbl, 3, 2)
        self.date_vigencia_fin = QDateEdit()
        self.date_vigencia_fin.setCalendarPopup(True)
        self.date_vigencia_fin.setDisplayFormat("dd/MM/yyyy")
        self.date_vigencia_fin.setMinimumWidth(160)
        self.date_vigencia_fin.dateChanged.connect(self._on_vigencia_fin_changed)
        grid.addWidget(self.date_vigencia_fin, 3, 3)
        
        # Fila 4: Estado de Aseguramiento
        lbl = QLabel("Estado Aseg.:")
        lbl.setMaximumWidth(100)
        grid.addWidget(lbl, 4, 0)
        self.combo_estado_aseguramiento = QComboBox()
        self.combo_estado_aseguramiento.setMinimumWidth(200)
        grid.addWidget(self.combo_estado_aseguramiento, 4, 1, 1, 3)
        
        group.setLayout(grid)
        return group
    
    def _create_buttons(self) -> QHBoxLayout:
        """Crea los botones de acción."""
        layout = QHBoxLayout()
        layout.setSpacing(10)
        
        self.btn_guardar = QPushButton("💾 Guardar Vehículo")
        self.btn_guardar.setMinimumWidth(150)
        self.btn_guardar.clicked.connect(self._on_guardar)
        layout.addWidget(self.btn_guardar)
        
        self.btn_actualizar = QPushButton("✏️ Actualizar Vehículo")
        self.btn_actualizar.setMinimumWidth(150)
        self.btn_actualizar.clicked.connect(self._on_actualizar)
        self.btn_actualizar.setVisible(False)
        layout.addWidget(self.btn_actualizar)
        
        self.btn_anular = QPushButton("❌ Anular Vehículo")
        self.btn_anular.setMinimumWidth(150)
        self.btn_anular.clicked.connect(self._on_anular)
        self.btn_anular.setVisible(False)
        self.btn_anular.setStyleSheet("""
            QPushButton {
                background-color: #DC3545;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #C82333;
            }
        """)
        layout.addWidget(self.btn_anular)
        
        self.btn_limpiar = QPushButton("🔄 Limpiar")
        self.btn_limpiar.setMinimumWidth(80)
        self.btn_limpiar.clicked.connect(self.limpiar_formulario)
        layout.addWidget(self.btn_limpiar)
        
        # Label de estado
        self.lbl_estado = QLabel("")
        self.lbl_estado.setStyleSheet("""
            QLabel {
                padding: 5px 15px;
                border-radius: 3px;
                font-weight: bold;
                font-size: 11pt;
            }
        """)
        self.lbl_estado.setVisible(False)
        layout.addWidget(self.lbl_estado)
        
        layout.addStretch()
        return layout
    
    def _on_buscar_vehiculo(self):
        """Maneja el evento de búsqueda de vehículo."""
        placa = self.txt_placa.text().strip().upper()
        if not placa:
            return
        self.buscar_vehiculo_signal.emit(placa)
    
    def _on_guardar(self):
        """Maneja el evento de guardar vehículo."""
        datos = self.get_datos_vehiculo()
        self.guardar_vehiculo_signal.emit(datos)
    
    def _on_actualizar(self):
        """Maneja el evento de actualizar vehículo."""
        datos = self.get_datos_vehiculo()
        self.actualizar_vehiculo_signal.emit(datos)
    
    def _on_anular(self):
        """Maneja el evento de anular vehículo."""
        if not self.vehiculo_id_actual:
            return
        
        respuesta = QMessageBox.question(
            self,
            "Confirmar Anulación",
            f"¿Está seguro de anular el vehículo?\n\n"
            f"El vehículo no se eliminará, solo cambiará su estado a ANULADO.\n"
            f"Esto permitirá registrar un nuevo vehículo para este accidente.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if respuesta == QMessageBox.StandardButton.Yes:
            self.anular_vehiculo_signal.emit(self.vehiculo_id_actual)
    
    def _on_vigencia_inicio_changed(self, date: QDate):
        """Calcula automáticamente la fecha fin cuando cambia la fecha inicio (+ 1 año)."""
        # Calcular fecha fin = fecha inicio + 1 año
        fecha_fin = date.addYears(1)
        
        # Bloquear señales temporalmente para evitar bucle infinito
        self.date_vigencia_fin.blockSignals(True)
        self.date_vigencia_fin.setDate(fecha_fin)
        self.date_vigencia_fin.blockSignals(False)
    
    def _on_vigencia_fin_changed(self, date: QDate):
        """Calcula automáticamente la fecha inicio cuando cambia la fecha fin (- 1 año)."""
        # Calcular fecha inicio = fecha fin - 1 año
        fecha_inicio = date.addYears(-1)
        
        # Bloquear señales temporalmente para evitar bucle infinito
        self.date_vigencia_inicio.blockSignals(True)
        self.date_vigencia_inicio.setDate(fecha_inicio)
        self.date_vigencia_inicio.blockSignals(False)
    
    def _bloquear_busqueda_vehiculo(self):
        """SEGURIDAD: Bloquea solo el botón de búsqueda cuando ya existe un vehículo guardado."""
        # Solo bloquear el botón, permitir editar placa manualmente
        self.btn_buscar.setEnabled(False)
        self.btn_buscar.setStyleSheet("background-color: #E0E0E0;")
        self.lbl_vehiculo_encontrado.setText("🔒 Búsqueda deshabilitada. Para buscar otro, debe anular este primero")
        self.lbl_vehiculo_encontrado.setStyleSheet("color: #FF6B6B; font-weight: bold; font-size: 9pt;")
        print("🔒 VehiculoForm: Botón búsqueda bloqueado - puede editar placa manualmente")
    
    def _desbloquear_busqueda_vehiculo(self):
        """SEGURIDAD: Desbloquea la búsqueda después de anular un vehículo."""
        self.btn_buscar.setEnabled(True)
        self.btn_buscar.setStyleSheet("")
        self.lbl_vehiculo_encontrado.setText("")
        print("🔓 VehiculoForm: Botón búsqueda desbloqueado - puede buscar nuevo vehículo")
    
    def get_datos_vehiculo(self) -> dict:
        """Obtiene los datos del formulario."""
        return {
            "vehiculo_id": self.vehiculo_id_actual,
            "placa": self.txt_placa.text().strip().upper() or None,
            "marca": self.txt_marca.text().strip() or None,
            "tipo_vehiculo_id": self.combo_tipo_vehiculo.currentData(),
            "aseguradora_codigo": self.txt_aseguradora.text().strip() or None,
            "numero_poliza": self.txt_numero_poliza.text().strip() or None,
            "vigencia_inicio": self.date_vigencia_inicio.date().toPython(),
            "vigencia_fin": self.date_vigencia_fin.date().toPython(),
            "estado_aseguramiento_id": self.combo_estado_aseguramiento.currentData(),
        }
    
    def cargar_vehiculo(self, vehiculo: dict):
        """Carga datos de un vehículo en el formulario."""
        self.vehiculo_id_actual = vehiculo.get("id")
        
        self.txt_placa.setText(vehiculo.get("placa", ""))
        self.txt_marca.setText(vehiculo.get("marca", ""))
        
        if vehiculo.get("tipo_vehiculo_id"):
            idx = self.combo_tipo_vehiculo.findData(vehiculo["tipo_vehiculo_id"])
            if idx >= 0:
                self.combo_tipo_vehiculo.setCurrentIndex(idx)
        
        self.txt_aseguradora.setText(vehiculo.get("aseguradora_codigo", ""))
        self.txt_numero_poliza.setText(vehiculo.get("numero_poliza", ""))
        
        if vehiculo.get("vigencia_inicio"):
            self.date_vigencia_inicio.setDate(QDate(vehiculo["vigencia_inicio"]))
        
        if vehiculo.get("vigencia_fin"):
            self.date_vigencia_fin.setDate(QDate(vehiculo["vigencia_fin"]))
        
        if vehiculo.get("estado_aseguramiento_id"):
            idx = self.combo_estado_aseguramiento.findData(vehiculo["estado_aseguramiento_id"])
            if idx >= 0:
                self.combo_estado_aseguramiento.setCurrentIndex(idx)
        
        placa = vehiculo.get("placa", "N/A")
        self.lbl_vehiculo_encontrado.setText(f"✓ Vehículo encontrado: {placa}")
    
    def limpiar_formulario(self):
        """Limpia todos los campos del formulario."""
        self.vehiculo_id_actual = None
        
        # Limpiar variables de control de cambio de propietario
        self.vehiculo_cambiar_propietario = False
        self.vehiculo_propietario_bd = None
        self.propietario_recien_actualizado = False
        
        self.txt_placa.clear()
        self.txt_marca.clear()
        self.combo_tipo_vehiculo.setCurrentIndex(0)
        self.txt_aseguradora.clear()
        self.txt_numero_poliza.clear()
        self.date_vigencia_inicio.setDate(QDate.currentDate())
        self.date_vigencia_fin.setDate(QDate.currentDate())
        self.combo_estado_aseguramiento.setCurrentIndex(0)
        
        self.lbl_vehiculo_encontrado.clear()
        self.lbl_estado.clear()
        self.lbl_estado.setVisible(False)
        self.btn_guardar.setEnabled(True)
        
        # SEGURIDAD: Desbloquear búsqueda después de limpiar
        self._desbloquear_busqueda_vehiculo()
        
        # Restaurar botones
        self.btn_guardar.setVisible(True)
        self.btn_actualizar.setVisible(False)
        self.btn_anular.setVisible(False)
    
    def cargar_tipos_vehiculo(self, tipos: list):
        """Carga tipos de vehículo."""
        self.combo_tipo_vehiculo.clear()
        for t in tipos:
            self.combo_tipo_vehiculo.addItem(t["descripcion"], t["id"])
    
    def cargar_estados_aseguramiento(self, estados: list):
        """Carga estados de aseguramiento."""
        self.combo_estado_aseguramiento.clear()
        for e in estados:
            self.combo_estado_aseguramiento.addItem(e["descripcion"], e["id"])
    
    def mostrar_vehiculo_guardado(self, vehiculo_id: int, placa: str):
        """Muestra el vehículo guardado."""
        self.vehiculo_id_actual = vehiculo_id
        self.lbl_estado.setText(f"✅ Vehículo guardado: {placa}")
        self.lbl_estado.setStyleSheet("""
            QLabel {
                background-color: #90EE90; 
                color: #006400; 
                font-weight: bold; 
                padding: 8px 15px;
                border-radius: 4px;
                font-size: 11pt;
            }
        """)
        self.lbl_estado.setVisible(True)
        
        # Mostrar botón Actualizar y Anular, ocultar Guardar
        self.btn_guardar.setVisible(False)
        self.btn_actualizar.setVisible(True)
        self.btn_anular.setVisible(True)
    
    def cargar_vehiculo_existente(self, vehiculo: dict):
        """Carga un vehículo existente."""
        self.cargar_vehiculo(vehiculo)
        
        placa = vehiculo.get("placa", "N/A")
        self.lbl_estado.setText(f"📝 Vehículo actual: {placa}")
        self.lbl_estado.setStyleSheet("""
            QLabel {
                background-color: #ADD8E6; 
                color: #00008B; 
                font-weight: bold; 
                padding: 8px 15px;
                border-radius: 4px;
                font-size: 11pt;
            }
        """)
        self.lbl_estado.setVisible(True)
        
        # SEGURIDAD: Bloquear búsqueda por placa cuando ya existe vehículo guardado
        self._bloquear_busqueda_vehiculo()
        
        # Mostrar botón Actualizar y Anular, ocultar Guardar
        self.btn_guardar.setVisible(False)
        self.btn_actualizar.setVisible(True)
        self.btn_anular.setVisible(True)
