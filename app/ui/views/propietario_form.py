"""
Formulario para gestión del propietario.
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


class PropietarioForm(QWidget):
    """Formulario para gestión del propietario del vehículo."""
    
    # Señales
    buscar_persona_signal = Signal(str, str)  # tipo_id, numero
    guardar_propietario_signal = Signal(dict)
    actualizar_propietario_signal = Signal(dict)
    anular_propietario_signal = Signal(int)  # propietario_id
    
    def __init__(self):
        super().__init__()
        self.persona_id_actual = None
        self.propietario_id_actual = None
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
        
        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)
        layout.setSpacing(5)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Grupo: Datos de la Persona
        group_persona = self._create_persona_group()
        layout.addWidget(group_persona)
        
        # Botones de acción
        btn_layout = self._create_buttons()
        layout.addLayout(btn_layout)
        
        # Label de estado
        self.lbl_estado = QLabel("")
        self.lbl_estado.setStyleSheet("font-weight: bold; padding: 5px;")
        self.lbl_estado.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_estado)
        
        layout.addStretch()
        
        scroll.setWidget(scroll_widget)
        main_layout.addWidget(scroll, 1)
    
    def _create_persona_group(self) -> QGroupBox:
        """Crea el grupo de datos de persona."""
        group = QGroupBox("👤 Datos del Propietario")
        grid = QGridLayout()
        grid.setSpacing(8)
        grid.setContentsMargins(8, 10, 8, 8)
        
        # Configurar proporciones de columnas
        grid.setColumnStretch(0, 0)  # Label
        grid.setColumnStretch(1, 1)  # Campo
        grid.setColumnStretch(2, 0)  # Label
        grid.setColumnStretch(3, 1)  # Campo
        grid.setColumnStretch(4, 0)  # Label  
        grid.setColumnStretch(5, 1)  # Campo
        grid.setColumnStretch(6, 0)  # Label
        grid.setColumnStretch(7, 1)  # Campo
        
        # Fila 0: Búsqueda
        lbl = QLabel("Tipo:")
        lbl.setMaximumWidth(50)
        grid.addWidget(lbl, 0, 0)
        self.combo_tipo_id = QComboBox()
        self.combo_tipo_id.setMinimumWidth(100)
        grid.addWidget(self.combo_tipo_id, 0, 1)
        
        lbl = QLabel("Número:")
        lbl.setMaximumWidth(60)
        grid.addWidget(lbl, 0, 2)
        self.txt_numero_id = QLineEdit()
        self.txt_numero_id.setMinimumWidth(130)
        self.txt_numero_id.setPlaceholderText("Documento")
        # Validador: solo números
        validator_numeros = QRegularExpressionValidator(QRegularExpression(r"^\d*$"))
        self.txt_numero_id.setValidator(validator_numeros)
        grid.addWidget(self.txt_numero_id, 0, 3)
        
        self.btn_buscar = QPushButton("🔍 Buscar")
        self.btn_buscar.setFixedWidth(90)
        self.btn_buscar.clicked.connect(self._on_buscar_persona)
        grid.addWidget(self.btn_buscar, 0, 4)
        
        self.lbl_persona_encontrada = QLabel("")
        self.lbl_persona_encontrada.setStyleSheet("color: green; font-weight: bold; font-size: 9pt;")
        grid.addWidget(self.lbl_persona_encontrada, 0, 5, 1, 3)
        
        # Fila 1: Nombres completos
        lbl = QLabel("1er Nombre:")
        lbl.setMaximumWidth(80)
        grid.addWidget(lbl, 1, 0)
        self.txt_primer_nombre = QLineEdit()
        self.txt_primer_nombre.setMinimumWidth(130)
        # Validador: solo letras, espacios, tildes y ñ
        validator_letras = QRegularExpressionValidator(QRegularExpression(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]*$"))
        self.txt_primer_nombre.setValidator(validator_letras)
        grid.addWidget(self.txt_primer_nombre, 1, 1)
        
        lbl = QLabel("2do Nombre:")
        lbl.setMaximumWidth(80)
        grid.addWidget(lbl, 1, 2)
        self.txt_segundo_nombre = QLineEdit()
        self.txt_segundo_nombre.setMinimumWidth(130)
        self.txt_segundo_nombre.setValidator(validator_letras)
        grid.addWidget(self.txt_segundo_nombre, 1, 3)
        
        lbl = QLabel("1er Apellido:")
        lbl.setMaximumWidth(80)
        grid.addWidget(lbl, 1, 4)
        self.txt_primer_apellido = QLineEdit()
        self.txt_primer_apellido.setMinimumWidth(130)
        self.txt_primer_apellido.setValidator(validator_letras)
        grid.addWidget(self.txt_primer_apellido, 1, 5)
        
        lbl = QLabel("2do Apellido:")
        lbl.setMaximumWidth(80)
        grid.addWidget(lbl, 1, 6)
        self.txt_segundo_apellido = QLineEdit()
        self.txt_segundo_apellido.setMinimumWidth(130)
        self.txt_segundo_apellido.setValidator(validator_letras)
        grid.addWidget(self.txt_segundo_apellido, 1, 7)
        
        # Fila 2: Fecha nacimiento y sexo
        lbl = QLabel("F. Nac:")
        lbl.setMaximumWidth(80)
        grid.addWidget(lbl, 2, 0)
        self.date_nacimiento = QDateEdit()
        self.date_nacimiento.setCalendarPopup(True)
        self.date_nacimiento.setDisplayFormat("dd/MM/yyyy")
        self.date_nacimiento.setMinimumWidth(130)
        grid.addWidget(self.date_nacimiento, 2, 1)
        
        lbl = QLabel("Sexo:")
        lbl.setMaximumWidth(80)
        grid.addWidget(lbl, 2, 2)
        self.combo_sexo = QComboBox()
        self.combo_sexo.setMinimumWidth(130)
        grid.addWidget(self.combo_sexo, 2, 3)
        
        # Fila 3: Dirección, teléfono, municipio
        lbl = QLabel("Dirección:")
        lbl.setMaximumWidth(80)
        grid.addWidget(lbl, 3, 0)
        self.txt_direccion = QLineEdit()
        self.txt_direccion.setMaxLength(200)
        self.txt_direccion.setMinimumWidth(160)
        grid.addWidget(self.txt_direccion, 3, 1, 1, 3)  # Span 3 columns
        
        lbl = QLabel("Teléfono:")
        lbl.setMaximumWidth(80)
        grid.addWidget(lbl, 3, 4)
        self.txt_telefono = QLineEdit()
        self.txt_telefono.setMaxLength(15)
        self.txt_telefono.setMinimumWidth(130)
        # Validador: solo números
        self.txt_telefono.setValidator(validator_numeros)
        grid.addWidget(self.txt_telefono, 3, 5)
        
        lbl = QLabel("Municipio:")
        lbl.setMaximumWidth(80)
        grid.addWidget(lbl, 3, 6)
        self.combo_municipio_residencia = QComboBox()
        self.combo_municipio_residencia.setMinimumWidth(160)
        grid.addWidget(self.combo_municipio_residencia, 3, 7)
        
        group.setLayout(grid)
        return group
    
    def _create_buttons(self) -> QHBoxLayout:
        """Crea los botones de acción."""
        layout = QHBoxLayout()
        layout.setSpacing(10)
        
        self.btn_guardar = QPushButton("💾 Guardar Propietario")
        self.btn_guardar.setMinimumWidth(150)
        self.btn_guardar.clicked.connect(self._on_guardar)
        layout.addWidget(self.btn_guardar)
        
        self.btn_actualizar = QPushButton("✏️ Actualizar Propietario")
        self.btn_actualizar.setMinimumWidth(150)
        self.btn_actualizar.clicked.connect(self._on_actualizar)
        self.btn_actualizar.setVisible(False)  # Oculto por defecto
        layout.addWidget(self.btn_actualizar)
        
        self.btn_anular = QPushButton("❌ Anular Propietario")
        self.btn_anular.setMinimumWidth(150)
        self.btn_anular.clicked.connect(self._on_anular)
        self.btn_anular.setVisible(False)  # Oculto por defecto
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
        
        # Label de estado - visible junto a botones
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
    
    def _on_buscar_persona(self):
        """Maneja el evento de búsqueda de persona."""
        tipo_id = self.combo_tipo_id.currentData()
        numero = self.txt_numero_id.text().strip()
        
        if not numero:
            return
        
        self.buscar_persona_signal.emit(str(tipo_id) if tipo_id else "", numero)
    
    def _on_guardar(self):
        """Maneja el evento de guardar propietario."""
        datos = self.get_datos_propietario()
        self.guardar_propietario_signal.emit(datos)
    
    def _on_actualizar(self):
        """Maneja el evento de actualizar propietario."""
        datos = self.get_datos_propietario()
        self.actualizar_propietario_signal.emit(datos)
    
    def _on_anular(self):
        """Maneja el evento de anular propietario."""
        if not self.propietario_id_actual:
            return
        
        # Confirmar anulación
        respuesta = QMessageBox.question(
            self,
            "Confirmar Anulación",
            f"¿Está seguro de anular el propietario?\n\n"
            f"El propietario no se eliminará, solo cambiará su estado a ANULADO.\n"
            f"Esto permitirá registrar un nuevo propietario para este accidente.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if respuesta == QMessageBox.StandardButton.Yes:
            self.anular_propietario_signal.emit(self.propietario_id_actual)
    
    def get_datos_propietario(self) -> dict:
        """Obtiene los datos del formulario."""
        return {
            "propietario_id": self.propietario_id_actual,
            "persona_id": self.persona_id_actual,
            # Datos persona
            "tipo_identificacion_id": self.combo_tipo_id.currentData(),
            "numero_identificacion": self.txt_numero_id.text().strip(),
            "primer_nombre": self.txt_primer_nombre.text().strip(),
            "segundo_nombre": self.txt_segundo_nombre.text().strip() or None,
            "primer_apellido": self.txt_primer_apellido.text().strip(),
            "segundo_apellido": self.txt_segundo_apellido.text().strip() or None,
            "fecha_nacimiento": self.date_nacimiento.date().toPython(),
            "sexo_id": self.combo_sexo.currentData(),
            "direccion": self.txt_direccion.text().strip() or "N/A",
            "telefono": self.txt_telefono.text().strip() or "N/A",
            "municipio_residencia_id": self.combo_municipio_residencia.currentData() or 1,
        }
    
    def cargar_persona(self, persona: dict):
        """Carga datos de una persona en el formulario."""
        self.persona_id_actual = persona.get("id")
        self.txt_primer_nombre.setText(persona.get("primer_nombre", ""))
        self.txt_segundo_nombre.setText(persona.get("segundo_nombre", "") or "")
        self.txt_primer_apellido.setText(persona.get("primer_apellido", ""))
        self.txt_segundo_apellido.setText(persona.get("segundo_apellido", "") or "")
        self.txt_direccion.setText(persona.get("direccion", ""))
        self.txt_telefono.setText(persona.get("telefono", ""))
        
        if persona.get("fecha_nacimiento"):
            self.date_nacimiento.setDate(QDate(persona["fecha_nacimiento"]))
        
        if persona.get("sexo_id"):
            idx = self.combo_sexo.findData(persona["sexo_id"])
            if idx >= 0:
                self.combo_sexo.setCurrentIndex(idx)
        
        if persona.get("municipio_residencia_id"):
            idx = self.combo_municipio_residencia.findData(persona["municipio_residencia_id"])
            if idx >= 0:
                self.combo_municipio_residencia.setCurrentIndex(idx)
        
        nombre_completo = f"{persona.get('primer_nombre', '')} {persona.get('primer_apellido', '')}"
        self.lbl_persona_encontrada.setText(f"✓ Persona encontrada: {nombre_completo}")
    
    def limpiar_formulario(self):
        """Limpia todos los campos del formulario."""
        self.propietario_id_actual = None
        self.persona_id_actual = None
        
        self.txt_numero_id.clear()
        self.txt_primer_nombre.clear()
        self.txt_segundo_nombre.clear()
        self.txt_primer_apellido.clear()
        self.txt_segundo_apellido.clear()
        self.txt_direccion.clear()
        self.txt_telefono.clear()
        self.date_nacimiento.setDate(QDate.currentDate())
        self.combo_sexo.setCurrentIndex(0)
        self.combo_municipio_residencia.setCurrentIndex(0)
        
        self.lbl_persona_encontrada.clear()
        self.lbl_estado.clear()
        self.lbl_estado.setVisible(False)
        self.btn_guardar.setEnabled(True)
        
        # SEGURIDAD: Desbloquear búsqueda después de limpiar
        self._desbloquear_busqueda_propietario()
        
        # Restaurar botones
        self.btn_guardar.setVisible(True)
        self.btn_actualizar.setVisible(False)
        self.btn_anular.setVisible(False)
    
    def _bloquear_busqueda_propietario(self):
        """SEGURIDAD: Bloquea solo el botón de búsqueda cuando ya existe un propietario guardado."""
        # Solo bloquear el botón, permitir editar tipo y número de documento manualmente
        self.btn_buscar.setEnabled(False)
        self.btn_buscar.setStyleSheet("background-color: #E0E0E0;")
        self.lbl_persona_encontrada.setText("🔒 Búsqueda deshabilitada. Para buscar otro, debe anular este primero")
        self.lbl_persona_encontrada.setStyleSheet("color: #FF6B6B; font-weight: bold; font-size: 9pt;")
        print("🔒 PropietarioForm: Botón búsqueda bloqueado - puede editar documento manualmente")
    
    def _desbloquear_busqueda_propietario(self):
        """SEGURIDAD: Desbloquea la búsqueda después de anular un propietario."""
        self.btn_buscar.setEnabled(True)
        self.btn_buscar.setStyleSheet("")
        self.lbl_persona_encontrada.setText("")
        print("🔓 PropietarioForm: Botón búsqueda desbloqueado - puede buscar nuevo propietario")
    
    def cargar_tipos_identificacion(self, tipos: list):
        """Carga tipos de identificación."""
        self.combo_tipo_id.clear()
        for t in tipos:
            self.combo_tipo_id.addItem(t["descripcion"], t["id"])
    
    def cargar_sexos(self, sexos: list):
        """Carga sexos."""
        self.combo_sexo.clear()
        for s in sexos:
            self.combo_sexo.addItem(s["descripcion"], s["id"])
    
    def cargar_municipios(self, municipios: list):
        """Carga municipios."""
        self.combo_municipio_residencia.clear()
        for m in municipios:
            self.combo_municipio_residencia.addItem(m["nombre"], m["id"])
    
    def mostrar_propietario_guardado(self, propietario_id: int, nombre: str):
        """Muestra el propietario guardado."""
        self.propietario_id_actual = propietario_id
        self.lbl_estado.setText(f"✅ Propietario guardado: {nombre}")
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
    
    def cargar_propietario_existente(self, propietario: dict):
        """Carga un propietario existente."""
        self.propietario_id_actual = propietario.get("id")
        
        persona = propietario.get("persona")
        if persona:
            self.cargar_persona({
                "id": persona.get("id"),
                "primer_nombre": persona.get("primer_nombre"),
                "segundo_nombre": persona.get("segundo_nombre"),
                "primer_apellido": persona.get("primer_apellido"),
                "segundo_apellido": persona.get("segundo_apellido"),
                "fecha_nacimiento": persona.get("fecha_nacimiento"),
                "sexo_id": persona.get("sexo_id"),
                "direccion": persona.get("direccion"),
                "telefono": persona.get("telefono"),
                "municipio_residencia_id": persona.get("municipio_residencia_id"),
            })
            
            # Tipo ID
            idx = self.combo_tipo_id.findData(persona.get("tipo_identificacion_id"))
            if idx >= 0:
                self.combo_tipo_id.setCurrentIndex(idx)
            
            self.txt_numero_id.setText(persona.get("numero_identificacion", ""))
            
            nombre_completo = f"{persona.get('primer_nombre', '')} {persona.get('primer_apellido', '')}"
            self.lbl_estado.setText(f"📝 Propietario actual: {nombre_completo}")
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
            
            # SEGURIDAD: Bloquear búsqueda cuando ya existe propietario guardado
            self._bloquear_busqueda_propietario()
            
            # Mostrar botón Actualizar y Anular, ocultar Guardar
            self.btn_guardar.setVisible(False)
            self.btn_actualizar.setVisible(True)
            self.btn_anular.setVisible(True)
