"""
Formulario para gestión de médico tratante.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QGridLayout,
    QLineEdit, QComboBox, QDateEdit, QTimeEdit, QPushButton, QLabel, QCheckBox, QSpinBox
)
from PySide6.QtCore import Signal, QDate, QTime, Qt


class MedicoTratanteForm(QWidget):
    """Formulario para gestión del médico tratante de la víctima."""
    
    # Señales
    guardar_medico_signal = Signal(dict)
    actualizar_medico_signal = Signal(dict)
    anular_medico_signal = Signal(int)
    
    def __init__(self):
        super().__init__()
        self.medico_id_actual = None
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura la interfaz."""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(5)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Grupo: Médico Tratante
        group_medico = self._create_medico_group()
        main_layout.addWidget(group_medico)
        
        # Grupo: Fechas y Diagnósticos
        group_atencion = self._create_atencion_group()
        main_layout.addWidget(group_atencion)
        
        # Grupo: UCI
        group_uci = self._create_uci_group()
        main_layout.addWidget(group_uci)
        
        # Botones de acción
        btn_layout = self._create_buttons()
        main_layout.addLayout(btn_layout)
        
        main_layout.addStretch()
    
    def _create_medico_group(self) -> QGroupBox:
        """Crea el grupo de médico tratante."""
        group = QGroupBox("👨‍⚕️ Médico Tratante")
        grid = QGridLayout()
        grid.setSpacing(8)
        grid.setContentsMargins(8, 10, 8, 8)
        
        # Víctima (read-only)
        grid.addWidget(QLabel("Víctima:"), 0, 0)
        self.lbl_victima = QLabel("No hay víctima registrada")
        self.lbl_victima.setStyleSheet("color: #FF6B6B; font-weight: bold;")
        grid.addWidget(self.lbl_victima, 0, 1, 1, 3)
        
        # Médico
        grid.addWidget(QLabel("Médico:"), 1, 0)
        self.combo_medico = QComboBox()
        self.combo_medico.setMinimumWidth(400)
        grid.addWidget(self.combo_medico, 1, 1, 1, 3)
        
        group.setLayout(grid)
        return group
    
    def _create_atencion_group(self) -> QGroupBox:
        """Crea el grupo de atención médica."""
        group = QGroupBox("📋 Datos de Atención")
        grid = QGridLayout()
        grid.setSpacing(8)
        grid.setContentsMargins(8, 10, 8, 8)
        
        # Fila 0: Fechas Ingreso/Egreso
        grid.addWidget(QLabel("Fecha Ingreso:"), 0, 0)
        self.date_ingreso = QDateEdit()
        self.date_ingreso.setCalendarPopup(True)
        self.date_ingreso.setDisplayFormat("dd/MM/yyyy")
        self.date_ingreso.setDate(QDate.currentDate())  # Fecha actual por defecto
        self.date_ingreso.setMinimumWidth(120)
        grid.addWidget(self.date_ingreso, 0, 1)
        
        grid.addWidget(QLabel("Hora Ingreso:"), 0, 2)
        self.time_ingreso = QTimeEdit()
        self.time_ingreso.setDisplayFormat("HH:mm")
        self.time_ingreso.setTime(QTime.currentTime())  # Hora actual por defecto
        self.time_ingreso.setMinimumWidth(80)
        grid.addWidget(self.time_ingreso, 0, 3)
        
        grid.addWidget(QLabel("Fecha Egreso:"), 0, 4)
        self.date_egreso = QDateEdit()
        self.date_egreso.setCalendarPopup(True)
        self.date_egreso.setDisplayFormat("dd/MM/yyyy")
        self.date_egreso.setDate(QDate.currentDate())  # Fecha actual por defecto
        self.date_egreso.setMinimumWidth(120)
        grid.addWidget(self.date_egreso, 0, 5)
        
        grid.addWidget(QLabel("Hora Egreso:"), 0, 6)
        self.time_egreso = QTimeEdit()
        self.time_egreso.setDisplayFormat("HH:mm")
        self.time_egreso.setTime(QTime.currentTime())  # Hora actual por defecto
        self.time_egreso.setMinimumWidth(80)
        grid.addWidget(self.time_egreso, 0, 7)
        
        # Fila 1: Diagnósticos de Ingreso
        grid.addWidget(QLabel("Diag. Ingreso Principal:"), 1, 0)
        self.txt_diag_ingreso = QLineEdit()
        self.txt_diag_ingreso.setMaxLength(4)
        self.txt_diag_ingreso.setFixedWidth(70)
        self.txt_diag_ingreso.setPlaceholderText("S000")
        grid.addWidget(self.txt_diag_ingreso, 1, 1)
        
        grid.addWidget(QLabel("Ing. Sec. 1:"), 1, 2)
        self.txt_diag_ingreso_sec1 = QLineEdit()
        self.txt_diag_ingreso_sec1.setMaxLength(4)
        self.txt_diag_ingreso_sec1.setFixedWidth(70)
        grid.addWidget(self.txt_diag_ingreso_sec1, 1, 3)
        
        grid.addWidget(QLabel("Ing. Sec. 2:"), 1, 4)
        self.txt_diag_ingreso_sec2 = QLineEdit()
        self.txt_diag_ingreso_sec2.setMaxLength(4)
        self.txt_diag_ingreso_sec2.setFixedWidth(70)
        grid.addWidget(self.txt_diag_ingreso_sec2, 1, 5)
        
        # Fila 2: Diagnósticos de Egreso
        grid.addWidget(QLabel("Diag. Egreso Principal:"), 2, 0)
        self.txt_diag_egreso = QLineEdit()
        self.txt_diag_egreso.setMaxLength(4)
        self.txt_diag_egreso.setFixedWidth(70)
        self.txt_diag_egreso.setPlaceholderText("S000")
        grid.addWidget(self.txt_diag_egreso, 2, 1)
        
        grid.addWidget(QLabel("Egr. Sec. 1:"), 2, 2)
        self.txt_diag_egreso_sec1 = QLineEdit()
        self.txt_diag_egreso_sec1.setMaxLength(4)
        self.txt_diag_egreso_sec1.setFixedWidth(70)
        grid.addWidget(self.txt_diag_egreso_sec1, 2, 3)
        
        grid.addWidget(QLabel("Egr. Sec. 2:"), 2, 4)
        self.txt_diag_egreso_sec2 = QLineEdit()
        self.txt_diag_egreso_sec2.setMaxLength(4)
        self.txt_diag_egreso_sec2.setFixedWidth(70)
        grid.addWidget(self.txt_diag_egreso_sec2, 2, 5)
        
        group.setLayout(grid)
        return group
    
    def _create_uci_group(self) -> QGroupBox:
        """Crea el grupo de UCI."""
        group = QGroupBox("🏥 UCI")
        grid = QGridLayout()
        grid.setSpacing(8)
        grid.setContentsMargins(8, 10, 8, 8)
        
        self.chk_uci = QCheckBox("Ingresó a UCI")
        grid.addWidget(self.chk_uci, 0, 0)
        
        grid.addWidget(QLabel("Días en UCI:"), 0, 1)
        self.spin_dias_uci = QSpinBox()
        self.spin_dias_uci.setMinimum(0)
        self.spin_dias_uci.setMaximum(365)
        self.spin_dias_uci.setEnabled(False)
        grid.addWidget(self.spin_dias_uci, 0, 2)
        
        # Conectar checkbox
        self.chk_uci.toggled.connect(self.spin_dias_uci.setEnabled)
        
        group.setLayout(grid)
        return group
    
    def _create_buttons(self) -> QHBoxLayout:
        """Crea los botones de acción."""
        layout = QHBoxLayout()
        layout.setSpacing(10)
        
        self.btn_guardar = QPushButton("💾 Guardar Médico Tratante")
        self.btn_guardar.setMinimumWidth(180)
        self.btn_guardar.clicked.connect(self._on_guardar)
        layout.addWidget(self.btn_guardar)
        
        self.btn_actualizar = QPushButton("✏️ Actualizar")
        self.btn_actualizar.setMinimumWidth(120)
        self.btn_actualizar.clicked.connect(self._on_actualizar)
        self.btn_actualizar.setVisible(False)
        layout.addWidget(self.btn_actualizar)
        
        self.btn_anular = QPushButton("❌ Anular")
        self.btn_anular.setMinimumWidth(100)
        self.btn_anular.clicked.connect(self._on_anular)
        self.btn_anular.setVisible(False)
        self.btn_anular.setStyleSheet("background-color: #DC3545; color: white;")
        layout.addWidget(self.btn_anular)
        
        self.btn_limpiar = QPushButton("🔄 Limpiar")
        self.btn_limpiar.setMinimumWidth(80)
        self.btn_limpiar.clicked.connect(self.limpiar_formulario)
        layout.addWidget(self.btn_limpiar)
        
        self.lbl_estado = QLabel("")
        self.lbl_estado.setStyleSheet("padding: 5px 15px; border-radius: 3px; font-weight: bold;")
        self.lbl_estado.setVisible(False)
        layout.addWidget(self.lbl_estado)
        
        layout.addStretch()
        return layout
    
    def _on_guardar(self):
        """Maneja el evento de guardar."""
        datos = self.get_datos_medico()
        self.guardar_medico_signal.emit(datos)
    
    def _on_actualizar(self):
        """Maneja el evento de actualizar."""
        datos = self.get_datos_medico()
        self.actualizar_medico_signal.emit(datos)
    
    def _on_anular(self):
        """Maneja el evento de anular."""
        from PySide6.QtWidgets import QMessageBox
        
        if not self.medico_id_actual:
            return
        
        respuesta = QMessageBox.question(
            self, "Confirmar Anulación",
            "¿Está seguro de anular el médico tratante?\n\nEsto permitirá registrar uno nuevo.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if respuesta == QMessageBox.StandardButton.Yes:
            self.anular_medico_signal.emit(self.medico_id_actual)
    
    def get_datos_medico(self) -> dict:
        """Obtiene los datos del formulario."""
        return {
            "medico_id": self.medico_id_actual,
            "persona_id": self.combo_medico.currentData(),
            "fecha_ingreso": self.date_ingreso.date().toPython() if self.date_ingreso.date().isValid() else None,
            "hora_ingreso": self.time_ingreso.time().toPython() if self.time_ingreso.time().isValid() else None,
            "fecha_egreso": self.date_egreso.date().toPython() if self.date_egreso.date().isValid() else None,
            "hora_egreso": self.time_egreso.time().toPython() if self.time_egreso.time().isValid() else None,
            "diagnostico_ingreso": self.txt_diag_ingreso.text().strip() or None,
            "diagnostico_ingreso_sec1": self.txt_diag_ingreso_sec1.text().strip() or None,
            "diagnostico_ingreso_sec2": self.txt_diag_ingreso_sec2.text().strip() or None,
            "diagnostico_egreso": self.txt_diag_egreso.text().strip() or None,
            "diagnostico_egreso_sec1": self.txt_diag_egreso_sec1.text().strip() or None,
            "diagnostico_egreso_sec2": self.txt_diag_egreso_sec2.text().strip() or None,
            "servicio_uci": self.chk_uci.isChecked(),
            "dias_uci": self.spin_dias_uci.value() if self.chk_uci.isChecked() else None,
        }
    
    def cargar_medicos(self, medicos: list):
        """Carga médicos en el combo."""
        self.combo_medico.clear()
        self.combo_medico.addItem("-- Seleccione un médico --", None)
        for m in medicos:
            texto = f"{m['nombre_completo']} - {m['registro_medico']} ({m['especialidad']})"
            self.combo_medico.addItem(texto, m["persona_id"])
    
    def set_victima_info(self, victima_nombre: str):
        """Establece la información de la víctima."""
        self.lbl_victima.setText(f"✓ {victima_nombre}")
        self.lbl_victima.setStyleSheet("color: green; font-weight: bold;")
    
    def limpiar_formulario(self):
        """Limpia todos los campos del formulario."""
        self.medico_id_actual = None
        self.combo_medico.setCurrentIndex(0)
        self.date_ingreso.setDate(QDate.currentDate())
        self.time_ingreso.setTime(QTime.currentTime())
        self.date_egreso.setDate(QDate.currentDate())
        self.time_egreso.setTime(QTime.currentTime())
        self.txt_diag_ingreso.clear()
        self.txt_diag_ingreso_sec1.clear()
        self.txt_diag_ingreso_sec2.clear()
        self.txt_diag_egreso.clear()
        self.txt_diag_egreso_sec1.clear()
        self.txt_diag_egreso_sec2.clear()
        self.chk_uci.setChecked(False)
        self.spin_dias_uci.setValue(0)
        
        self.lbl_estado.clear()
        self.lbl_estado.setVisible(False)
        self.btn_guardar.setVisible(True)
        self.btn_actualizar.setVisible(False)
        self.btn_anular.setVisible(False)
        self.combo_medico.setEnabled(True)
    
    def cargar_medico_existente(self, medico: dict):
        """Carga un médico tratante existente."""
        self.medico_id_actual = medico.get("id")
        
        # Seleccionar médico
        idx = self.combo_medico.findData(medico.get("persona_id"))
        if idx >= 0:
            self.combo_medico.setCurrentIndex(idx)
        
        # Fechas y horas
        if medico.get("fecha_ingreso"):
            self.date_ingreso.setDate(QDate(medico["fecha_ingreso"]))
        if medico.get("hora_ingreso"):
            self.time_ingreso.setTime(QTime(medico["hora_ingreso"]))
        if medico.get("fecha_egreso"):
            self.date_egreso.setDate(QDate(medico["fecha_egreso"]))
        if medico.get("hora_egreso"):
            self.time_egreso.setTime(QTime(medico["hora_egreso"]))
        
        # Diagnósticos
        self.txt_diag_ingreso.setText(medico.get("diagnostico_ingreso", "") or "")
        self.txt_diag_ingreso_sec1.setText(medico.get("diagnostico_ingreso_sec1", "") or "")
        self.txt_diag_ingreso_sec2.setText(medico.get("diagnostico_ingreso_sec2", "") or "")
        self.txt_diag_egreso.setText(medico.get("diagnostico_egreso", "") or "")
        self.txt_diag_egreso_sec1.setText(medico.get("diagnostico_egreso_sec1", "") or "")
        self.txt_diag_egreso_sec2.setText(medico.get("diagnostico_egreso_sec2", "") or "")
        
        # UCI
        self.chk_uci.setChecked(medico.get("servicio_uci", False))
        self.spin_dias_uci.setValue(medico.get("dias_uci", 0) or 0)
        
        # Estado
        self.lbl_estado.setText("📝 Médico tratante registrado")
        self.lbl_estado.setStyleSheet("background-color: #ADD8E6; color: #00008B; padding: 5px 15px; border-radius: 3px; font-weight: bold;")
        self.lbl_estado.setVisible(True)
        
        # Botones
        self.btn_guardar.setVisible(False)
        self.btn_actualizar.setVisible(True)
        self.btn_anular.setVisible(True)
        self.combo_medico.setEnabled(False)
    
    def mostrar_guardado(self, mensaje: str):
        """Muestra mensaje de guardado exitoso."""
        self.lbl_estado.setText(f"✅ {mensaje}")
        self.lbl_estado.setStyleSheet("background-color: #90EE90; color: #006400; padding: 5px 15px; border-radius: 3px; font-weight: bold;")
        self.lbl_estado.setVisible(True)
