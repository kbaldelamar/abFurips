"""
Formulario principal para diligenciar FURIPS.
"""
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QFormLayout,
    QGridLayout,
    QLineEdit,
    QComboBox,
    QDateEdit,
    QTimeEdit,
    QPushButton,
    QTabWidget,
    QLabel,
    QScrollArea,
)
from PySide6.QtCore import Signal, QDate, QTime, Qt


class AccidenteForm(QWidget):
    """Formulario para diligenciar datos del accidente."""
    
    # Señales
    guardar_accidente_signal = Signal(dict)
    actualizar_accidente_signal = Signal(dict)
    anular_accidente_signal = Signal(int)  # Emite el ID del accidente a anular
    buscar_accidente_signal = Signal()
    
    def __init__(self):
        super().__init__()
        self.accidente_id_actual = None  # Para trackear el accidente cargado
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura la interfaz."""
        # Aplicar estilos generales
        self.setStyleSheet("""
            QWidget {
                background-color: #E8F4F8;
                font-family: Segoe UI;
                font-size: 9pt;
            }
            QGroupBox {
                background-color: white;
                border: 1px solid #B0C4DE;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
                font-weight: bold;
                color: #2C5F7C;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 5px 10px;
                background-color: #4A90B5;
                color: white;
                border-radius: 3px;
            }
            QLineEdit, QComboBox, QDateEdit, QTimeEdit, QTextEdit {
                padding: 5px;
                border: 1px solid #B0C4DE;
                border-radius: 3px;
                background-color: white;
                min-height: 20px;
            }
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTimeEdit:focus, QTextEdit:focus {
                border: 2px solid #4A90B5;
            }
            QTextEdit {
                font-family: Segoe UI;
                font-size: 9pt;
            }
            QPushButton {
                background-color: #4A90B5;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 20px;
                font-weight: bold;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #5BA0C5;
            }
            QPushButton:pressed {
                background-color: #3A7095;
            }
            QTabWidget::pane {
                border: 1px solid #B0C4DE;
                background-color: white;
                border-radius: 5px;
            }
            QTabBar::tab {
                background-color: #D0E8F0;
                border: 1px solid #B0C4DE;
                padding: 8px 15px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: none;
            }
            QTabBar::tab:hover {
                background-color: #C0D8E8;
            }
            QLabel {
                color: #2C5F7C;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Barra de botones superior
        btn_toolbar = QHBoxLayout()
        btn_toolbar.setSpacing(10)
        
        self.btn_buscar = QPushButton("🔍 Buscar")
        self.btn_buscar.setMinimumWidth(100)
        self.btn_buscar.clicked.connect(self._on_buscar)
        btn_toolbar.addWidget(self.btn_buscar)
        
        self.btn_nuevo = QPushButton("🆕 Nuevo")
        self.btn_nuevo.setMinimumWidth(100)
        self.btn_nuevo.clicked.connect(self._on_nuevo)
        btn_toolbar.addWidget(self.btn_nuevo)
        
        self.btn_guardar_accidente = QPushButton("💾 Guardar")
        self.btn_guardar_accidente.setMinimumWidth(100)
        self.btn_guardar_accidente.clicked.connect(self._on_guardar_accidente)
        btn_toolbar.addWidget(self.btn_guardar_accidente)
        
        self.btn_actualizar_accidente = QPushButton("✏️ Actualizar")
        self.btn_actualizar_accidente.setMinimumWidth(100)
        self.btn_actualizar_accidente.clicked.connect(self._on_actualizar_accidente)
        self.btn_actualizar_accidente.setVisible(False)
        btn_toolbar.addWidget(self.btn_actualizar_accidente)
        
        self.btn_anular_accidente = QPushButton("❌ Anular")
        self.btn_anular_accidente.setMinimumWidth(100)
        self.btn_anular_accidente.clicked.connect(self._on_anular_accidente)
        self.btn_anular_accidente.setVisible(False)
        self.btn_anular_accidente.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        btn_toolbar.addWidget(self.btn_anular_accidente)
        
        btn_toolbar.addStretch()
        
        # Label para mostrar ID del accidente guardado
        self.lbl_accidente_id = QLabel("")
        self.lbl_accidente_id.setStyleSheet("""
            QLabel {
                background-color: #4CAF50;
                color: white;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 10pt;
            }
        """)
        self.lbl_accidente_id.setVisible(False)
        btn_toolbar.addWidget(self.lbl_accidente_id)
        
        layout.addLayout(btn_toolbar)
        
        # Panel superior: Datos del accidente
        group_accidente = self._create_accidente_group()
        layout.addWidget(group_accidente)
        
        # Pestañas inferiores
        self.tabs = QTabWidget()
        self.tab_victima = self._create_victima_tab()
        self.tab_conductor = self._create_conductor_tab()
        self.tab_propietario = self._create_propietario_tab()
        self.tab_vehiculo = self._create_vehiculo_tab()
        self.tab_medico_tratante = self._create_medico_tratante_tab()
        self.tab_remision = self._create_remision_tab()
        self.tab_detalle = self._create_detalle_tab()
        self.tab_totales = self._create_totales_tab()
        
        self.tabs.addTab(self.tab_victima, "👤 Víctima")
        self.tabs.addTab(self.tab_conductor, "🚗 Conductor")
        self.tabs.addTab(self.tab_propietario, "📝 Propietario")
        self.tabs.addTab(self.tab_vehiculo, "🚙 Vehículo")
        self.tabs.addTab(self.tab_medico_tratante, "🩺 Médico Tratante")
        self.tabs.addTab(self.tab_remision, "🚑 Remisiones")
        self.tabs.addTab(self.tab_detalle, "📋 Detalle (FURIPS2)")
        self.tabs.addTab(self.tab_totales, "💰 Totales / Declaración")
        
        layout.addWidget(self.tabs, 1)
    
    def _create_accidente_group(self) -> QGroupBox:
        """Crea el grupo de datos del accidente."""
        from PySide6.QtWidgets import QTextEdit
        
        group = QGroupBox("Datos del Accidente")
        grid = QGridLayout()
        grid.setSpacing(8)
        grid.setContentsMargins(10, 15, 10, 10)
        
        # Fila 0: Prestador (ocupa 2 columnas), Consecutivo, SIRAS
        grid.addWidget(QLabel("Prestador:"), 0, 0)
        self.combo_prestador = QComboBox()
        self.combo_prestador.setMinimumWidth(250)
        grid.addWidget(self.combo_prestador, 0, 1, 1, 2)
        
        grid.addWidget(QLabel("Consecutivo:"), 0, 3)
        self.txt_consecutivo = QLineEdit()
        self.txt_consecutivo.setMaxLength(12)
        self.txt_consecutivo.setFixedWidth(110)
        self.txt_consecutivo.setPlaceholderText("12 dígitos")
        grid.addWidget(self.txt_consecutivo, 0, 4)
        
        grid.addWidget(QLabel("Radicado SIRAS:"), 0, 5)
        self.txt_siras = QLineEdit()
        self.txt_siras.setMaxLength(20)
        self.txt_siras.setFixedWidth(130)
        grid.addWidget(self.txt_siras, 0, 6)
        
        # Fila 1: Número de Factura, Naturaleza del Evento, Descripción (si es otro)
        grid.addWidget(QLabel("Número de Factura:"), 1, 0)
        self.txt_factura = QLineEdit()
        self.txt_factura.setMaxLength(20)
        self.txt_factura.setFixedWidth(150)
        grid.addWidget(self.txt_factura, 1, 1)
        
        grid.addWidget(QLabel("Naturaleza del Evento:"), 1, 2)
        self.combo_naturaleza = QComboBox()
        self.combo_naturaleza.setMinimumWidth(300)
        grid.addWidget(self.combo_naturaleza, 1, 3, 1, 2)
        
        grid.addWidget(QLabel("Descripción (si es 'Otro'):"), 1, 5)
        self.txt_otro_evento = QLineEdit()
        self.txt_otro_evento.setMaxLength(25)
        self.txt_otro_evento.setPlaceholderText("Solo si naturaleza es 'Otro'")
        self.txt_otro_evento.setFixedWidth(200)
        grid.addWidget(self.txt_otro_evento, 1, 6)
        
        # Fila 2: Fecha, Hora, Municipio, Zona
        grid.addWidget(QLabel("Fecha del Evento:"), 2, 0)
        self.date_evento = QDateEdit()
        self.date_evento.setCalendarPopup(True)
        self.date_evento.setDate(QDate.currentDate())
        self.date_evento.setDisplayFormat("dd/MM/yyyy")
        self.date_evento.setFixedWidth(110)
        grid.addWidget(self.date_evento, 2, 1)
        
        grid.addWidget(QLabel("Hora:"), 2, 2)
        self.time_evento = QTimeEdit()
        self.time_evento.setTime(QTime.currentTime())
        self.time_evento.setDisplayFormat("HH:mm")
        self.time_evento.setFixedWidth(70)
        grid.addWidget(self.time_evento, 2, 3)
        
        grid.addWidget(QLabel("Municipio:"), 2, 4)
        self.combo_municipio = QComboBox()
        self.combo_municipio.setMinimumWidth(150)
        grid.addWidget(self.combo_municipio, 2, 5)
        
        grid.addWidget(QLabel("Zona:"), 2, 6)
        self.combo_zona = QComboBox()
        self.combo_zona.addItems(["", "Urbana", "Rural"])
        self.combo_zona.setFixedWidth(90)
        grid.addWidget(self.combo_zona, 2, 7)
        
        # Fila 3: Dirección del Evento y Descripción
        grid.addWidget(QLabel("Dirección del Evento:"), 3, 0)
        self.txt_direccion = QLineEdit()
        self.txt_direccion.setMaxLength(200)
        self.txt_direccion.setPlaceholderText("Dirección donde ocurrió el evento (máx. 200 caracteres)")
        grid.addWidget(self.txt_direccion, 3, 1, 1, 3)
        
        grid.addWidget(QLabel("Descripción:"), 3, 4)
        self.txt_descripcion = QLineEdit()
        self.txt_descripcion.setPlaceholderText("Descripción del evento (solo letras)")
        # Validación: solo letras y espacios
        from PySide6.QtGui import QRegularExpressionValidator
        from PySide6.QtCore import QRegularExpression
        regex_letras = QRegularExpression("[A-Za-zÁÉÍÓÚáéíóúÑñ ]*")
        self.txt_descripcion.setValidator(QRegularExpressionValidator(regex_letras))
        grid.addWidget(self.txt_descripcion, 3, 5, 1, 3)
        
        # Fila 4: Placa, Estado Aseguramiento
        grid.addWidget(QLabel("Placa del Vehículo:"), 4, 0)
        self.txt_placa = QLineEdit()
        self.txt_placa.setMaxLength(10)
        self.txt_placa.setFixedWidth(100)
        self.txt_placa.setPlaceholderText("ABC123")
        grid.addWidget(self.txt_placa, 4, 1)
        
        grid.addWidget(QLabel("Estado Aseguramiento:"), 4, 2)
        self.combo_estado_aseg = QComboBox()
        self.combo_estado_aseg.setMinimumWidth(250)
        grid.addWidget(self.combo_estado_aseg, 4, 3, 1, 5)
        
        # Configurar expansión de columnas
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(5, 2)
        
        group.setLayout(grid)
        return group
    
    def _create_victima_tab(self) -> QWidget:
        """Crea la pestaña de víctima."""
        from app.ui.views.victima_form import VictimaForm
        self.victima_form = VictimaForm()
        return self.victima_form
    
    def _create_conductor_tab(self) -> QWidget:
        """Crea la pestaña de conductor."""
        from app.ui.views.conductor_form import ConductorForm
        self.conductor_form = ConductorForm()
        return self.conductor_form
    
    def _create_propietario_tab(self) -> QWidget:
        """Crea la pestaña de propietario."""
        from app.ui.views.propietario_form import PropietarioForm
        self.propietario_form = PropietarioForm()
        return self.propietario_form
    
    def _create_vehiculo_tab(self) -> QWidget:
        """Crea la pestaña de vehículo."""
        from app.ui.views.vehiculo_form import VehiculoForm
        self.vehiculo_form = VehiculoForm()
        return self.vehiculo_form
    
    def _create_detalle_tab(self) -> QWidget:
        """Crea la pestaña de detalle."""
        from app.ui.views.detalle_form import DetalleForm
        self.detalle_form = DetalleForm()
        return self.detalle_form
    
    def _create_medico_tratante_tab(self) -> QWidget:
        """Crea la pestaña de médico tratante."""
        from app.ui.views.medico_tratante_form import MedicoTratanteForm
        self.medico_tratante_form = MedicoTratanteForm()
        return self.medico_tratante_form
    
    def _create_remision_tab(self) -> QWidget:
        """Crea la pestaña de remisiones."""
        from app.ui.views.remision_form import RemisionForm
        self.remision_form = RemisionForm()
        return self.remision_form
    
    def _create_totales_tab(self) -> QWidget:
        """Crea la pestaña de totales."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Encabezado
        header = QLabel("Totales y declaración (informativo)")
        header.setStyleSheet("font-weight: bold;")
        layout.addWidget(header)

        # Campos informativos: Gastos Movilización y Gastos Quirúrgicos
        row = QHBoxLayout()
        lbl_mov = QLabel("Gastos Movilización:")
        self.lbl_gastos_movilizacion = QLabel("0")
        row.addWidget(lbl_mov)
        row.addWidget(self.lbl_gastos_movilizacion)

        row.addSpacing(30)

        lbl_qx = QLabel("Gastos Médico Quirúrgicos:")
        self.lbl_gastos_qx = QLabel("0")
        row.addWidget(lbl_qx)
        row.addWidget(self.lbl_gastos_qx)

        layout.addLayout(row)

        # Nota explicativa
        note = QLabel("Los valores mostrados son sumas informativas de los procedimientos asociados al accidente.")
        layout.addWidget(note)

        layout.addStretch()

        return widget

    def set_totales(self, totales: dict):
        """Actualiza la vista de totales con los valores calculados.

        Espera dict con claves: 'gastosMovilizacion', 'gastosQx'.
        """
        try:
            gm = totales.get("gastosMovilizacion", 0)
            gq = totales.get("gastosQx", 0)
            # Formato con separador de miles
            self.lbl_gastos_movilizacion.setText(f"{int(gm):,}")
            self.lbl_gastos_qx.setText(f"{int(gq):,}")
        except Exception:
            pass
    
    def _on_nuevo(self):
        """Limpia el formulario para un nuevo accidente."""
        # Resetear ID actual
        self.accidente_id_actual = None
        
        # Limpiar campos de texto
        self.txt_consecutivo.clear()
        self.txt_factura.clear()
        self.txt_siras.clear()
        self.txt_otro_evento.clear()
        self.txt_direccion.clear()
        self.txt_descripcion.clear()
        self.txt_placa.clear()
        
        # Resetear combos a índice 0
        self.combo_prestador.setCurrentIndex(0)
        self.combo_naturaleza.setCurrentIndex(0)
        self.combo_municipio.setCurrentIndex(0)
        self.combo_zona.setCurrentIndex(0)
        self.combo_estado_aseg.setCurrentIndex(0)
        
        # Resetear fecha y hora a actuales
        self.date_evento.setDate(QDate.currentDate())
        self.time_evento.setTime(QTime.currentTime())
        
        # Ocultar el label del accidente guardado
        self.lbl_accidente_id.setVisible(False)
        
        # Resetear botones: mostrar Guardar, ocultar Actualizar y Anular
        self.btn_guardar_accidente.setVisible(True)
        self.btn_guardar_accidente.setEnabled(True)
        self.btn_actualizar_accidente.setVisible(False)
        self.btn_anular_accidente.setVisible(False)
        
        # Limpiar todos los tabs
        self.vehiculo_form.limpiar_formulario()
        self.victima_form.limpiar_formulario()
        self.conductor_form.limpiar_formulario()
        self.propietario_form.limpiar_formulario()
        self.medico_tratante_form.limpiar_formulario()
        self.remision_form.limpiar_formulario()
        self.remision_form.limpiar_tabla()
        self.detalle_form.limpiar_formulario()
    
    def _on_guardar_accidente(self):
        """Maneja el clic en guardar accidente."""
        datos = self.get_datos_accidente()
        self.guardar_accidente_signal.emit(datos)
    
    def _on_anular_accidente(self):
        """Maneja el clic en anular accidente."""
        if not self.accidente_id_actual:
            print("❌ No hay accidente cargado para anular")
            return
        
        # Confirmar anulación
        from PySide6.QtWidgets import QMessageBox
        respuesta = QMessageBox.question(
            self,
            "Confirmar Anulación",
            f"¿Está seguro de anular el accidente #{self.txt_consecutivo.text()}?\n\n"
            "El accidente no se eliminará, solo cambiará su estado a ANULADO.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if respuesta == QMessageBox.StandardButton.Yes:
            self.anular_accidente_signal.emit(self.accidente_id_actual)
    
    def get_datos_accidente(self) -> dict:
        """Obtiene los datos del formulario."""
        # Obtener dirección y descripción
        direccion_texto = self.txt_direccion.text().strip()
        descripcion_texto = self.txt_descripcion.text().strip()
        
        return {
            "prestador_id": self.combo_prestador.currentData(),
            "numero_consecutivo": self.txt_consecutivo.text(),
            "numero_factura": self.txt_factura.text(),
            "numero_rad_siras": self.txt_siras.text(),
            "naturaleza_evento_id": self.combo_naturaleza.currentData(),
            "descripcion_otro_evento": self.txt_otro_evento.text() or None,
            "fecha_evento": self.date_evento.date().toPython(),
            "hora_evento": self.time_evento.time().toPython(),
            "municipio_evento_id": self.combo_municipio.currentData(),
            "direccion_evento": direccion_texto,
            "descripcion": descripcion_texto or None,
            "zona": "U" if self.combo_zona.currentText() == "Urbana" else "R" if self.combo_zona.currentText() == "Rural" else None,
            "vehiculo_id": None,  # TODO: Obtener desde tab vehículo
            "estado_aseguramiento_id": self.combo_estado_aseg.currentData(),
        }
    
    def cargar_prestadores(self, prestadores: list):
        """Carga prestadores en el combo."""
        self.combo_prestador.clear()
        for p in prestadores:
            self.combo_prestador.addItem(p["razon_social"], p["id"])
    
    def cargar_naturalezas(self, naturalezas: list):
        """Carga naturalezas en el combo."""
        self.combo_naturaleza.clear()
        for n in naturalezas:
            self.combo_naturaleza.addItem(f"{n['codigo']} - {n['descripcion']}", n["id"])
    
    def cargar_municipios(self, municipios: list):
        """Carga municipios en el combo."""
        self.combo_municipio.clear()
        for m in municipios:
            self.combo_municipio.addItem(m["nombre"], m["id"])
    
    def cargar_estados_aseguramiento(self, estados: list):
        """Carga estados de aseguramiento en el combo."""
        self.combo_estado_aseg.clear()
        for e in estados:
            self.combo_estado_aseg.addItem(f"{e['codigo']} - {e['descripcion']}", e["id"])
    
    def mostrar_accidente_guardado(self, accidente_id: int, consecutivo: str):
        """Muestra el ID y consecutivo del accidente guardado en la interfaz."""
        self.accidente_id_actual = accidente_id
        self.lbl_accidente_id.setText(f"📌 Accidente ID: {accidente_id} | Consecutivo: {consecutivo}")
        self.lbl_accidente_id.setVisible(True)
        
        # Actualizar el campo consecutivo con el valor guardado (por si fue autogenerado)
        self.txt_consecutivo.setText(consecutivo)
        
        # Cambiar botones: ocultar Guardar, mostrar Actualizar y Anular
        self.btn_guardar_accidente.setVisible(False)
        self.btn_actualizar_accidente.setVisible(True)
        self.btn_anular_accidente.setVisible(True)
    
    def _on_buscar(self):
        """Maneja el clic en buscar accidente."""
        self.buscar_accidente_signal.emit()
    
    def _on_actualizar_accidente(self):
        """Maneja el clic en actualizar accidente."""
        datos = self.get_datos_accidente()
        datos["id"] = self.accidente_id_actual  # Agregar ID para actualización
        self.actualizar_accidente_signal.emit(datos)
    
    def cargar_accidente(self, accidente: dict):
        """Carga los datos de un accidente en el formulario."""
        self.accidente_id_actual = accidente.get("id")
        
        # Cargar datos básicos
        if accidente.get("prestador_id"):
            idx = self.combo_prestador.findData(accidente["prestador_id"])
            if idx >= 0:
                self.combo_prestador.setCurrentIndex(idx)
        
        self.txt_consecutivo.setText(accidente.get("numero_consecutivo", ""))
        self.txt_factura.setText(accidente.get("numero_factura", ""))
        self.txt_siras.setText(accidente.get("numero_rad_siras", "") or "")
        
        if accidente.get("naturaleza_evento_id"):
            idx = self.combo_naturaleza.findData(accidente["naturaleza_evento_id"])
            if idx >= 0:
                self.combo_naturaleza.setCurrentIndex(idx)
        
        self.txt_otro_evento.setText(accidente.get("descripcion_otro_evento", "") or "")
        
        if accidente.get("fecha_evento"):
            self.date_evento.setDate(QDate(accidente["fecha_evento"]))
        
        if accidente.get("hora_evento"):
            from datetime import time
            hora = accidente["hora_evento"]
            if isinstance(hora, time):
                self.time_evento.setTime(QTime(hora.hour, hora.minute, hora.second))
        
        if accidente.get("municipio_evento_id"):
            idx = self.combo_municipio.findData(accidente["municipio_evento_id"])
            if idx >= 0:
                self.combo_municipio.setCurrentIndex(idx)
        
        self.txt_direccion.setText(accidente.get("direccion_evento", "") or "")
        self.txt_descripcion.setText(accidente.get("descripcion", "") or "")
        
        zona = accidente.get("zona")
        if zona == "U":
            self.combo_zona.setCurrentIndex(1)  # Urbana
        elif zona == "R":
            self.combo_zona.setCurrentIndex(2)  # Rural
        else:
            self.combo_zona.setCurrentIndex(0)
        
        self.txt_placa.setText(accidente.get("placa_vehiculo", "") or "")
        
        if accidente.get("estado_aseguramiento_id"):
            idx = self.combo_estado_aseg.findData(accidente["estado_aseguramiento_id"])
            if idx >= 0:
                self.combo_estado_aseg.setCurrentIndex(idx)
        
        # Mostrar que el accidente está cargado
        self.mostrar_accidente_guardado(accidente["id"], accidente.get("numero_consecutivo", ""))
        self.btn_nuevo.setEnabled(True)
