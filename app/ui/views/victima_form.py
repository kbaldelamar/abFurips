"""
Formulario para gestión de víctimas.
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
    QCheckBox,
    QScrollArea,
)
from PySide6.QtCore import Signal, QDate, Qt, QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator


class VictimaForm(QWidget):
    """Formulario para gestión de víctimas del accidente."""
    
    # Señales
    buscar_persona_signal = Signal(str, str)  # tipo_id, numero
    guardar_victima_signal = Signal(dict)
    actualizar_victima_signal = Signal(dict)
    anular_victima_signal = Signal(int)  # victima_id
    
    def __init__(self):
        super().__init__()
        self.victima_id_actual = None  # Para actualización
        self.persona_id_actual = None
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura la interfaz."""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(5)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Crear área scrolleable para los formularios
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Widget contenedor para el scroll
        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)
        layout.setSpacing(5)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Grupo: Datos de la Persona
        group_persona = self._create_persona_group()
        layout.addWidget(group_persona)
        
        # Grupo: Datos de la Víctima
        group_victima = self._create_victima_group()
        layout.addWidget(group_victima)
        
        # Grupo: Copiar datos a otros roles
        group_copiar = self._create_copiar_datos_group()
        layout.addWidget(group_copiar)
        
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
        group = QGroupBox("📋 Datos de la Persona")
        grid = QGridLayout()
        grid.setSpacing(8)
        grid.setContentsMargins(8, 10, 8, 8)
        
        # Configurar proporciones de columnas: labels pequeños, campos grandes
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
        
        # Fila 3: Dirección, Teléfono y Municipio
        lbl = QLabel("Dirección:")
        lbl.setMaximumWidth(80)
        grid.addWidget(lbl, 3, 0)
        self.txt_direccion_persona = QLineEdit()
        self.txt_direccion_persona.setMinimumWidth(130)
        self.txt_direccion_persona.setPlaceholderText("Dirección de residencia")
        grid.addWidget(self.txt_direccion_persona, 3, 1, 1, 3)  # Ocupa 3 columnas
        
        lbl = QLabel("Teléfono:")
        lbl.setMaximumWidth(80)
        grid.addWidget(lbl, 3, 4)
        self.txt_telefono_persona = QLineEdit()
        self.txt_telefono_persona.setMinimumWidth(130)
        self.txt_telefono_persona.setPlaceholderText("Teléfono de contacto")
        self.txt_telefono_persona.setMaxLength(15)
        # Validador: solo números
        self.txt_telefono_persona.setValidator(validator_numeros)
        grid.addWidget(self.txt_telefono_persona, 3, 5)
        
        lbl = QLabel("Municipio:")
        lbl.setMaximumWidth(80)
        grid.addWidget(lbl, 3, 6)
        self.combo_municipio_residencia = QComboBox()
        self.combo_municipio_residencia.setMinimumWidth(160)
        grid.addWidget(self.combo_municipio_residencia, 3, 7)
        
        group.setLayout(grid)
        return group
    
    def _create_victima_group(self) -> QGroupBox:
        """Crea el grupo de datos de la víctima."""
        group = QGroupBox("⚕️ Datos de la Víctima en el Accidente")
        grid = QGridLayout()
        grid.setSpacing(8)
        grid.setContentsMargins(8, 10, 8, 8)
        
        # Solo Condición
        lbl = QLabel("Condición:")
        lbl.setMaximumWidth(70)
        grid.addWidget(lbl, 0, 0)
        self.combo_condicion = QComboBox()
        self.combo_condicion.addItems(["", "1 - Conductor", "2 - Peatón", "3 - Ocupante", "4 - Ciclista"])
        self.combo_condicion.setMinimumWidth(160)
        grid.addWidget(self.combo_condicion, 0, 1)
        
        group.setLayout(grid)
        return group
    
    def _create_copiar_datos_group(self) -> QGroupBox:
        """Crea el grupo de checkboxes para copiar datos a otros roles."""
        group = QGroupBox("Copiar datos de la víctima a:")
        group.setStyleSheet("QGroupBox { font-weight: bold; }")
        
        layout = QHBoxLayout()
        layout.setSpacing(20)
        
        self.chk_es_conductor = QCheckBox("Es también el Conductor")
        self.chk_es_conductor.setStyleSheet("QCheckBox { font-weight: normal; }")
        layout.addWidget(self.chk_es_conductor)
        
        self.chk_es_propietario = QCheckBox("Es también el Propietario")
        self.chk_es_propietario.setStyleSheet("QCheckBox { font-weight: normal; }")
        layout.addWidget(self.chk_es_propietario)
        
        layout.addStretch()
        group.setLayout(layout)
        return group
    
    def _create_buttons(self) -> QHBoxLayout:
        """Crea los botones de acción."""
        layout = QHBoxLayout()
        layout.setSpacing(10)
        
        self.btn_guardar = QPushButton("💾 Guardar Víctima")
        self.btn_guardar.setMinimumWidth(150)
        self.btn_guardar.clicked.connect(self._on_guardar)
        layout.addWidget(self.btn_guardar)
        
        self.btn_actualizar = QPushButton("✏️ Actualizar Víctima")
        self.btn_actualizar.setMinimumWidth(150)
        self.btn_actualizar.clicked.connect(self._on_actualizar)
        self.btn_actualizar.setVisible(False)  # Oculto por defecto
        layout.addWidget(self.btn_actualizar)
        
        self.btn_anular = QPushButton("❌ Anular Víctima")
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
        """Maneja el evento de guardar víctima."""
        datos = self.get_datos_victima()
        self.guardar_victima_signal.emit(datos)
    
    def _on_actualizar(self):
        """Maneja el evento de actualizar víctima."""
        datos = self.get_datos_victima()
        self.actualizar_victima_signal.emit(datos)
    
    def _on_anular(self):
        """Maneja el evento de anular víctima."""
        from PySide6.QtWidgets import QMessageBox
        
        if not self.victima_id_actual:
            return
        
        # Confirmar anulación
        respuesta = QMessageBox.question(
            self,
            "Confirmar Anulación",
            f"¿Está seguro de anular la víctima?\n\n"
            f"La víctima no se eliminará, solo cambiará su estado a ANULADO.\n"
            f"Esto permitirá registrar una nueva víctima para este accidente.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if respuesta == QMessageBox.StandardButton.Yes:
            self.anular_victima_signal.emit(self.victima_id_actual)
    
    def get_datos_victima(self) -> dict:
        """Obtiene los datos del formulario."""
        condicion_text = self.combo_condicion.currentText()
        condicion = condicion_text[0] if condicion_text else None
        
        return {
            "victima_id": self.victima_id_actual,
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
            "direccion": self.txt_direccion_persona.text().strip() or None,
            "telefono": self.txt_telefono_persona.text().strip() or None,
            "municipio_residencia_id": self.combo_municipio_residencia.currentData(),
            # Datos víctima (solo condicion)
            "condicion": condicion,
            # Copiar a otros roles
            "es_conductor": self.chk_es_conductor.isChecked(),
            "es_propietario": self.chk_es_propietario.isChecked(),
        }
    
    def cargar_persona(self, persona: dict):
        """Carga datos de una persona en el formulario."""
        self.persona_id_actual = persona.get("id")
        self.txt_primer_nombre.setText(persona.get("primer_nombre", ""))
        self.txt_segundo_nombre.setText(persona.get("segundo_nombre", "") or "")
        self.txt_primer_apellido.setText(persona.get("primer_apellido", ""))
        self.txt_segundo_apellido.setText(persona.get("segundo_apellido", "") or "")
        
        if persona.get("fecha_nacimiento"):
            self.date_nacimiento.setDate(QDate(persona["fecha_nacimiento"]))
        
        if persona.get("sexo_id"):
            idx = self.combo_sexo.findData(persona["sexo_id"])
            if idx >= 0:
                self.combo_sexo.setCurrentIndex(idx)
        
        self.txt_direccion_persona.setText(persona.get("direccion", "") or "")
        self.txt_telefono_persona.setText(persona.get("telefono", "") or "")
        
        if persona.get("municipio_residencia_id"):
            idx = self.combo_municipio_residencia.findData(persona["municipio_residencia_id"])
            if idx >= 0:
                self.combo_municipio_residencia.setCurrentIndex(idx)
        
        nombre_completo = f"{persona.get('primer_nombre', '')} {persona.get('primer_apellido', '')}"
        self.lbl_persona_encontrada.setText(f"✓ Persona encontrada: {nombre_completo}")
    
    def _bloquear_busqueda_victima(self):
        """SEGURIDAD: Bloquea solo el botón de búsqueda cuando ya existe una víctima guardada."""
        # Solo bloquear el botón, permitir editar tipo y número de documento manualmente
        self.btn_buscar.setEnabled(False)
        self.btn_buscar.setStyleSheet("background-color: #E0E0E0;")
        self.lbl_persona_encontrada.setText("🔒 Búsqueda deshabilitada. Para buscar otro, debe anular este primero")
        self.lbl_persona_encontrada.setStyleSheet("color: #FF6B6B; font-weight: bold; font-size: 9pt;")
        print("🔒 VictimaForm: Botón búsqueda bloqueado - puede editar documento manualmente")
    
    def _desbloquear_busqueda_victima(self):
        """SEGURIDAD: Desbloquea la búsqueda después de anular una víctima."""
        self.btn_buscar.setEnabled(True)
        self.btn_buscar.setStyleSheet("")
        self.lbl_persona_encontrada.setText("")
        print("🔓 VictimaForm: Botón búsqueda desbloqueado - puede buscar nueva víctima")
    
    def limpiar_formulario(self):
        """Limpia todos los campos del formulario."""
        self.victima_id_actual = None
        self.persona_id_actual = None
        
        self.txt_numero_id.clear()
        self.txt_primer_nombre.clear()
        self.txt_segundo_nombre.clear()
        self.txt_primer_apellido.clear()
        self.txt_segundo_apellido.clear()
        self.date_nacimiento.setDate(QDate.currentDate())
        self.combo_sexo.setCurrentIndex(0)
        self.txt_direccion_persona.clear()
        self.txt_telefono_persona.clear()
        self.combo_municipio_residencia.setCurrentIndex(0)
        
        self.combo_condicion.setCurrentIndex(0)
        
        self.lbl_persona_encontrada.clear()
        self.lbl_estado.clear()
        self.lbl_estado.setVisible(False)
        self.btn_guardar.setEnabled(True)
        
        # SEGURIDAD: Desbloquear búsqueda después de limpiar
        self._desbloquear_busqueda_victima()
        
        # Restaurar botones
        self.btn_guardar.setVisible(True)
        self.btn_actualizar.setVisible(False)
        self.btn_anular.setVisible(False)
        
        # Limpiar checkboxes de copiar
        self.chk_es_conductor.setChecked(False)
        self.chk_es_propietario.setChecked(False)
    
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
        """Carga municipios de residencia."""
        self.combo_municipio_residencia.clear()
        for m in municipios:
            self.combo_municipio_residencia.addItem(m["nombre"], m["id"])
    
    def mostrar_victima_guardada(self, victima_id: int, nombre: str):
        """Muestra la víctima guardada."""
        self.victima_id_actual = victima_id
        self.lbl_estado.setText(f"✅ Víctima guardada: {nombre}")
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
    
    def cargar_victima_existente(self, victima: dict):
        """Carga una víctima existente."""
        self.victima_id_actual = victima.get("id")
        
        persona = victima.get("persona")
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
            
            # Datos víctima (solo condicion)
            condicion = victima.get("condicion")
            if condicion:
                condicion_map = {"1": 1, "2": 2, "3": 3, "4": 4}
                idx = condicion_map.get(condicion, 0)
                self.combo_condicion.setCurrentIndex(idx)
            
            nombre_completo = f"{persona.get('primer_nombre', '')} {persona.get('primer_apellido', '')}"
            self.lbl_estado.setText(f"📝 Víctima actual: {nombre_completo}")
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
            
            # SEGURIDAD: Bloquear búsqueda cuando ya existe víctima guardada
            self._bloquear_busqueda_victima()
            
            # Mostrar botón Actualizar y Anular, ocultar Guardar
            self.btn_guardar.setVisible(False)
            self.btn_actualizar.setVisible(True)
            self.btn_anular.setVisible(True)
