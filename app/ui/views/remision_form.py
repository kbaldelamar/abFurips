"""
Formulario para gestión de remisiones.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QGridLayout,
    QLineEdit, QComboBox, QDateEdit, QTimeEdit, QPushButton, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
)
from PySide6.QtCore import Signal, QDate, QTime, Qt


class RemisionForm(QWidget):
    """Formulario para gestión de remisiones."""
    
    # Señales
    guardar_remision_signal = Signal(dict)
    actualizar_remision_signal = Signal(dict)
    eliminar_remision_signal = Signal(int)
    
    def __init__(self):
        super().__init__()
        self.remision_id_actual = None
        self.especialidades_medicos = {}  # Diccionario para guardar especialidades por persona_id
        self._setup_ui()
        
        # Conectar señal del combo para auto-completar cargo
        self.combo_profesional_remite.currentIndexChanged.connect(self._on_medico_seleccionado)
    
    def _setup_ui(self):
        """Configura la interfaz."""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(5)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Grupo: Tipo de Referencia
        group_tipo = self._create_tipo_group()
        main_layout.addWidget(group_tipo)
        
        # Grupo: Datos de Remisión
        group_remision = self._create_remision_group()
        main_layout.addWidget(group_remision)
        
        # Tabla de remisiones
        group_tabla = self._create_tabla_group()
        main_layout.addWidget(group_tabla)
        
        # Botones
        btn_layout = self._create_buttons()
        main_layout.addLayout(btn_layout)
        
        main_layout.addStretch()
    
    def _create_tipo_group(self) -> QGroupBox:
        """Crea el grupo de tipo de referencia."""
        group = QGroupBox("📋 Tipo de Referencia")
        grid = QGridLayout()
        grid.setSpacing(8)
        
        grid.addWidget(QLabel("Tipo:"), 0, 0)
        self.combo_tipo = QComboBox()
        self.combo_tipo.addItem("-- Seleccione --", None)
        self.combo_tipo.addItem("1 - Remite paciente", 1)
        self.combo_tipo.addItem("2 - Orden de servicio", 2)
        self.combo_tipo.addItem("3 - Recibe paciente", 3)
        self.combo_tipo.setMinimumWidth(250)
        grid.addWidget(self.combo_tipo, 0, 1)
        
        group.setLayout(grid)
        return group
    
    def _create_remision_group(self) -> QGroupBox:
        """Crea el grupo de datos de remisión."""
        group = QGroupBox("📄 Datos de la Remisión")
        grid = QGridLayout()
        grid.setSpacing(8)
        
        # Fila 0: Fechas
        grid.addWidget(QLabel("Fecha Remisión:"), 0, 0)
        self.date_remision = QDateEdit()
        self.date_remision.setCalendarPopup(True)
        self.date_remision.setDisplayFormat("dd/MM/yyyy")
        self.date_remision.setDate(QDate.currentDate())  # Fecha actual por defecto
        grid.addWidget(self.date_remision, 0, 1)
        
        grid.addWidget(QLabel("Hora Salida:"), 0, 2)
        self.time_salida = QTimeEdit()
        self.time_salida.setDisplayFormat("HH:mm")
        self.time_salida.setTime(QTime.currentTime())  # Hora actual por defecto
        grid.addWidget(self.time_salida, 0, 3)
        
        grid.addWidget(QLabel("Fecha Aceptación:"), 0, 4)
        self.date_aceptacion = QDateEdit()
        self.date_aceptacion.setCalendarPopup(True)
        self.date_aceptacion.setDisplayFormat("dd/MM/yyyy")
        self.date_aceptacion.setDate(QDate.currentDate())  # Fecha actual por defecto
        grid.addWidget(self.date_aceptacion, 0, 5)
        
        grid.addWidget(QLabel("Hora Aceptación:"), 0, 6)
        self.time_aceptacion = QTimeEdit()
        self.time_aceptacion.setDisplayFormat("HH:mm")
        self.time_aceptacion.setTime(QTime.currentTime())  # Hora actual por defecto
        grid.addWidget(self.time_aceptacion, 0, 7)
        
        # Fila 1: Remitente
        grid.addWidget(QLabel("Cód. Hab. Remitente:"), 1, 0)
        self.txt_cod_hab_remitente = QLineEdit()
        self.txt_cod_hab_remitente.setMaxLength(12)
        grid.addWidget(self.txt_cod_hab_remitente, 1, 1)
        
        grid.addWidget(QLabel("Profesional Remite:"), 1, 2)
        self.combo_profesional_remite = QComboBox()
        self.combo_profesional_remite.setMinimumWidth(250)
        grid.addWidget(self.combo_profesional_remite, 1, 3, 1, 3)
        
        grid.addWidget(QLabel("Cargo:"), 1, 6)
        self.txt_cargo_remite = QLineEdit()
        self.txt_cargo_remite.setMaxLength(30)
        grid.addWidget(self.txt_cargo_remite, 1, 7)
        
        # Fila 2: Receptor
        grid.addWidget(QLabel("Cód. Hab. Recibe:"), 2, 0)
        self.txt_cod_hab_recibe = QLineEdit()
        self.txt_cod_hab_recibe.setMaxLength(12)
        grid.addWidget(self.txt_cod_hab_recibe, 2, 1)
        
        grid.addWidget(QLabel("Profesional Recibe:"), 2, 2)
        self.txt_profesional_recibe = QLineEdit()
        self.txt_profesional_recibe.setMaxLength(60)
        self.txt_profesional_recibe.setPlaceholderText("Nombre del profesional que recibe...")
        grid.addWidget(self.txt_profesional_recibe, 2, 3, 1, 3)
        
        grid.addWidget(QLabel("Placa Ambulancia:"), 2, 6)
        self.txt_placa = QLineEdit()
        self.txt_placa.setMaxLength(12)
        grid.addWidget(self.txt_placa, 2, 7)
        
        group.setLayout(grid)
        return group
    
    def _create_tabla_group(self) -> QGroupBox:
        """Crea el grupo de tabla de remisiones."""
        group = QGroupBox("📋 Remisiones Registradas")
        layout = QVBoxLayout()
        
        self.tabla_remisiones = QTableWidget()
        self.tabla_remisiones.setColumnCount(9)
        self.tabla_remisiones.setHorizontalHeaderLabels([
            "Tipo", "Fecha Rem.", "Hora", "Remitente", "Receptor", 
            "Placa", "Fecha Acept.", "Hora Acept.", "Acciones"
        ])
        
        header = self.tabla_remisiones.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla_remisiones.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabla_remisiones.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabla_remisiones.setMinimumHeight(300)  # Altura mínima para la tabla
        
        layout.addWidget(self.tabla_remisiones)
        group.setLayout(layout)
        return group
    
    def _create_buttons(self) -> QHBoxLayout:
        """Crea los botones de acción."""
        layout = QHBoxLayout()
        layout.setSpacing(10)
        
        self.btn_agregar = QPushButton("➕ Agregar Remisión")
        self.btn_agregar.setMinimumWidth(150)
        self.btn_agregar.clicked.connect(self._on_agregar)
        layout.addWidget(self.btn_agregar)
        
        self.btn_limpiar = QPushButton("🔄 Limpiar")
        self.btn_limpiar.setMinimumWidth(80)
        self.btn_limpiar.clicked.connect(self.limpiar_formulario)
        layout.addWidget(self.btn_limpiar)
        
        layout.addStretch()
        return layout
    
    def _on_agregar(self):
        """Maneja el evento de agregar remisión."""
        datos = self.get_datos_remision()
        self.guardar_remision_signal.emit(datos)
    
    def _on_eliminar_fila(self):
        """Elimina una remisión de la tabla."""
        boton = self.sender()
        if not boton:
            return
        
        for i in range(self.tabla_remisiones.rowCount()):
            if self.tabla_remisiones.cellWidget(i, 8) == boton:
                remision_id = int(self.tabla_remisiones.item(i, 0).data(Qt.ItemDataRole.UserRole))
                if remision_id:
                    self.eliminar_remision_signal.emit(remision_id)
                break
    
    def get_datos_remision(self) -> dict:
        """Obtiene los datos del formulario."""
        return {
            "tipo_referencia": self.combo_tipo.currentData(),
            "fecha_remision": self.date_remision.date().toPython(),
            "hora_salida": self.time_salida.time().toPython(),
            "codigo_hab_remitente": self.txt_cod_hab_remitente.text().strip() or None,
            "profesional_remite": self.combo_profesional_remite.currentText() if self.combo_profesional_remite.currentIndex() > 0 else None,
            "cargo_remite": self.txt_cargo_remite.text().strip() or None,
            "fecha_aceptacion": self.date_aceptacion.date().toPython(),
            "hora_aceptacion": self.time_aceptacion.time().toPython(),
            "codigo_hab_recibe": self.txt_cod_hab_recibe.text().strip() or None,
            "profesional_recibe": self.txt_profesional_recibe.text().strip() or None,
            "placa_ambulancia": self.txt_placa.text().strip() or None,
            "persona_remite_id": self.combo_profesional_remite.currentData(),
            "persona_recibe_id": None,  # Ya no es combo, no hay ID
        }
    
    def cargar_profesionales(self, profesionales: list):
        """Carga profesionales en el combo (solo para profesional_remite)."""
        self.combo_profesional_remite.clear()
        self.especialidades_medicos.clear()
        
        self.combo_profesional_remite.addItem("-- Seleccione --", None)
        
        for p in profesionales:
            texto = f"{p['nombre_completo']}"
            self.combo_profesional_remite.addItem(texto, p["persona_id"])
            # Guardar especialidad por persona_id
            if p.get("especialidad"):
                self.especialidades_medicos[p["persona_id"]] = p["especialidad"]
    
    def agregar_remision_tabla(self, remision: dict):
        """Agrega una remisión a la tabla."""
        fila = self.tabla_remisiones.rowCount()
        self.tabla_remisiones.insertRow(fila)
        
        tipo_map = {1: "Remite", 2: "Orden", 3: "Recibe"}
        tipo = tipo_map.get(remision.get("tipo_referencia"), "")
        
        item_tipo = QTableWidgetItem(tipo)
        item_tipo.setData(Qt.ItemDataRole.UserRole, remision.get("id"))
        self.tabla_remisiones.setItem(fila, 0, item_tipo)
        self.tabla_remisiones.setItem(fila, 1, QTableWidgetItem(str(remision.get("fecha_remision", ""))))
        self.tabla_remisiones.setItem(fila, 2, QTableWidgetItem(str(remision.get("hora_salida", ""))))
        self.tabla_remisiones.setItem(fila, 3, QTableWidgetItem(remision.get("profesional_remite", "")))
        self.tabla_remisiones.setItem(fila, 4, QTableWidgetItem(remision.get("profesional_recibe", "")))
        self.tabla_remisiones.setItem(fila, 5, QTableWidgetItem(remision.get("placa_ambulancia", "")))
        self.tabla_remisiones.setItem(fila, 6, QTableWidgetItem(str(remision.get("fecha_aceptacion", ""))))
        self.tabla_remisiones.setItem(fila, 7, QTableWidgetItem(str(remision.get("hora_aceptacion", ""))))
        
        btn_eliminar = QPushButton("🗑️")
        btn_eliminar.setStyleSheet("background-color: #f44336; color: white;")
        btn_eliminar.clicked.connect(self._on_eliminar_fila)
        self.tabla_remisiones.setCellWidget(fila, 8, btn_eliminar)
    
    def limpiar_formulario(self):
        """Limpia los campos del formulario."""
        self.remision_id_actual = None
        self.combo_tipo.setCurrentIndex(0)
        self.date_remision.setDate(QDate.currentDate())
        self.time_salida.setTime(QTime.currentTime())
        self.txt_cod_hab_remitente.clear()
        self.combo_profesional_remite.setCurrentIndex(0)
        self.txt_cargo_remite.clear()
        self.date_aceptacion.setDate(QDate.currentDate())
        self.time_aceptacion.setTime(QTime.currentTime())
        self.txt_cod_hab_recibe.clear()
        self.txt_profesional_recibe.clear()
        self.txt_placa.clear()
    
    def _on_medico_seleccionado(self, index: int):
        """Auto-completa el campo cargo cuando se selecciona un médico."""
        if index > 0:  # Si no es "-- Seleccione --"
            persona_id = self.combo_profesional_remite.currentData()
            if persona_id and persona_id in self.especialidades_medicos:
                especialidad = self.especialidades_medicos[persona_id]
                self.txt_cargo_remite.setText(especialidad)
        else:
            self.txt_cargo_remite.clear()
    
    def limpiar_tabla(self):
        """Limpia la tabla de remisiones."""
        self.tabla_remisiones.setRowCount(0)
