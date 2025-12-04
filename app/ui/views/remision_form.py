"""
Formulario para gestión de remisiones.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QGridLayout,
    QLineEdit, QComboBox, QDateEdit, QTimeEdit, QPushButton, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
)
from PySide6.QtCore import Signal, QDate, QTime, Qt
from PySide6.QtWidgets import QMessageBox



class RemisionForm(QWidget):
    """Formulario para gestión de remisiones."""

    def set_datos_remision(self, datos: dict):
        """Carga los datos de una remisión en el formulario."""
        # Combos: buscar por valor
        if "tipo_referencia" in datos:
            idx = self.combo_tipo.findData(datos["tipo_referencia"])
            self.combo_tipo.setCurrentIndex(idx if idx != -1 else 0)
        if "prestadorId" in datos:
            idx = self.combo_prestador.findData(datos["prestadorId"])
            self.combo_prestador.setCurrentIndex(idx if idx != -1 else 0)
        if "persona_remite_id" in datos:
            idx = self.combo_profesional_remite.findData(datos["persona_remite_id"])
            self.combo_profesional_remite.setCurrentIndex(idx if idx != -1 else 0)

        # Fechas y horas
        if datos.get("fecha_remision"):
            self.date_remision.setDate(QDate(datos["fecha_remision"].year, datos["fecha_remision"].month, datos["fecha_remision"].day))
        if datos.get("hora_salida"):
            self.time_salida.setTime(QTime(datos["hora_salida"].hour, datos["hora_salida"].minute))
        if datos.get("fecha_aceptacion"):
            self.date_aceptacion.setDate(QDate(datos["fecha_aceptacion"].year, datos["fecha_aceptacion"].month, datos["fecha_aceptacion"].day))
        if datos.get("hora_aceptacion"):
            self.time_aceptacion.setTime(QTime(datos["hora_aceptacion"].hour, datos["hora_aceptacion"].minute))

        # Textos
        self.txt_placa.setText(datos.get("placa_ambulancia") or "")
        self.txt_cod_hab_recibe.setText(datos.get("codigo_hab_recibe") or "")
        self.txt_profesional_recibe.setText(datos.get("profesional_recibe") or "")
        self.txt_cargo_remite.setText(datos.get("cargo_remite") or "")
        # Guardar el id de la remisión cargada para acciones como Anula
        self.remision_id_actual = datos.get("id") if datos.get("id") else None
        # Mostrar el ID de la remisión si está presente
        if "id" in datos and datos["id"]:
            self.lbl_estado_remision.setText(f"✔️ Remisión guardada (ID: {datos['id']})")
            self.lbl_estado_remision.setStyleSheet("color: green; font-weight: bold;")

    # Señales
    guardar_remision_signal = Signal(dict)
    actualizar_remision_signal = Signal(dict)
    eliminar_remision_signal = Signal(int)
    anular_remision_signal = Signal(int)

    def __init__(self):
        super().__init__()
        self.remision_id_actual = None
        self.especialidades_medicos = {}  # Diccionario para guardar especialidades por persona_id
        self._setup_ui()
        # Conectar señal del combo para auto-completar cargo
        # El combo ya existe tras _setup_ui
        try:
            self.combo_profesional_remite.currentIndexChanged.connect(self._on_medico_seleccionado)
        except Exception:
            # En caso improbable de que el combo no exista aún, se ignora
            pass

    def _emitir_anular_remision(self):
        if not self.remision_id_actual:
            return

        # Preguntar confirmación al usuario
        resp = QMessageBox.question(
            self,
            "Confirmar anulación",
            "¿Está seguro que desea anular esta remisión? Esta acción no se podrá deshacer.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if resp == QMessageBox.StandardButton.Yes:
            self.anular_remision_signal.emit(self.remision_id_actual)

    def mostrar_estado_remision(self, guardada: bool):
        """Muestra un mensaje visual si la remisión está guardada."""
        if guardada:
            self.lbl_estado_remision.setText("✔️ Remisión guardada correctamente.")
            self.lbl_estado_remision.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.lbl_estado_remision.setText("")
            self.lbl_estado_remision.setStyleSheet("")
    
    def _setup_ui(self):
        """Configura la interfaz."""
        main_layout = QVBoxLayout(self)
        # Exponer el layout como atributo para que otros métodos (ej. añadir botones)
        # puedan agregar widgets dinámicamente.
        self.main_layout = main_layout
        main_layout.setSpacing(5)
        main_layout.setContentsMargins(5, 5, 5, 5)

        # Grupo: Tipo de Referencia
        group_tipo = self._create_tipo_group()
        main_layout.addWidget(group_tipo)

        # Grupo: Datos de Remisión
        group_remision = self._create_remision_group()
        main_layout.addWidget(group_remision)

        # Indicador de estado de remisión (se agregará en el siguiente paso)
        self.lbl_estado_remision = QLabel("")
        self.lbl_estado_remision.setStyleSheet("color: green; font-weight: bold;")
        main_layout.addWidget(self.lbl_estado_remision)

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
        # Allow the combo to shrink on narrow windows to avoid forcing overlap
        self.combo_tipo.setMinimumWidth(200)
        grid.addWidget(self.combo_tipo, 0, 1)

        # Añadir Prestador aquí para ganar espacio en la sección de datos
        grid.addWidget(QLabel("Prestador:"), 0, 2)
        self.combo_prestador = QComboBox()
        # Keep prestador reasonably sized but allow shrinkage
        self.combo_prestador.setMinimumWidth(200)
        self.combo_prestador.addItem("-- Seleccione --", None)
        grid.addWidget(self.combo_prestador, 0, 3)

        group.setLayout(grid)
        return group
    
    # NOTE: _create_remision_group is implemented below using horizontal
    # rows to avoid overlapping widgets on narrow windows. The older,
    # grid-based implementation was removed to prevent duplicate
    # definitions and layout conflicts.
    
    # Eliminada la tabla de remisiones, ya que solo se permite una remisión por accidente.
    
    def _create_buttons(self) -> QHBoxLayout:
        """Crea los botones de acción."""
        layout = QHBoxLayout()
        layout.setSpacing(10)
        
        self.btn_agregar = QPushButton("➕ Agregar Remisión")
        self.btn_agregar.setMinimumWidth(150)
        self.btn_agregar.clicked.connect(self._on_agregar)
        layout.addWidget(self.btn_agregar)
        
        # Botón Anular junto a Agregar
        self.btn_anular = QPushButton("Anular")
        self.btn_anular.setMinimumWidth(120)
        self.btn_anular.setStyleSheet("background-color: #e57373; color: white; font-weight: bold;")
        self.btn_anular.clicked.connect(self._emitir_anular_remision)
        layout.addWidget(self.btn_anular)
        
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
            # El código de habilitación del remitente se eliminó del formulario
            "profesional_remite": self.combo_profesional_remite.currentText() if self.combo_profesional_remite.currentIndex() > 0 else None,
            "cargo_remite": self.txt_cargo_remite.text().strip() or None,
            "fecha_aceptacion": self.date_aceptacion.date().toPython(),
            "hora_aceptacion": self.time_aceptacion.time().toPython(),
            "codigo_hab_recibe": self.txt_cod_hab_recibe.text().strip() or None,
            "profesional_recibe": self.txt_profesional_recibe.text().strip() or None,
            "placa_ambulancia": self.txt_placa.text().strip() or None,
            "persona_remite_id": self.combo_profesional_remite.currentData(),
            "persona_recibe_id": None,  # Ya no es combo, no hay ID
            "prestadorId": self.combo_prestador.currentData(),
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

    def cargar_prestadores(self, prestadores: list):
        """Carga la lista de prestadores en el combo de prestador."""
        self.combo_prestador.clear()
        self.combo_prestador.addItem("-- Seleccione --", None)
        for p in prestadores:
            # Se espera que cada prestador sea dict con keys 'id' y 'razon_social'
            texto = f"{p.get('razon_social') or p.get('nombre', '')}"
            self.combo_prestador.addItem(texto, p.get('id'))
    
    # Eliminada la función de agregar remisión a la tabla.
    
    def limpiar_formulario(self):
        """Limpia los campos del formulario."""
        self.remision_id_actual = None
        self.combo_tipo.setCurrentIndex(0)
        self.date_remision.setDate(QDate.currentDate())
        self.time_salida.setTime(QTime.currentTime())
        # Código de habilitación del remitente eliminado del formulario
        self.combo_profesional_remite.setCurrentIndex(0)
        self.txt_cargo_remite.clear()
        self.date_aceptacion.setDate(QDate.currentDate())
        self.time_aceptacion.setTime(QTime.currentTime())
        self.txt_cod_hab_recibe.clear()
        self.txt_profesional_recibe.clear()
        self.txt_placa.clear()
        if hasattr(self, 'combo_prestador'):
            self.combo_prestador.setCurrentIndex(0)
        # También ocultar/limpiar el indicador visual de remisión guardada
        try:
            self.mostrar_estado_remision(False)
        except Exception:
            # Si por alguna razón la vista no tiene el método, limpiar el label directamente
            try:
                self.lbl_estado_remision.setText("")
            except Exception:
                pass
    
    def _on_medico_seleccionado(self, index: int):
        """Auto-completa el campo cargo cuando se selecciona un médico."""
        if index > 0:  # Si no es "-- Seleccione --"
            persona_id = self.combo_profesional_remite.currentData()
            if persona_id and persona_id in self.especialidades_medicos:
                especialidad = self.especialidades_medicos[persona_id]
                self.txt_cargo_remite.setText(especialidad)
        else:
            self.txt_cargo_remite.clear()
    
    # Eliminada la función de limpiar la tabla de remisiones.

    def _create_remision_group(self) -> QGroupBox:
        """Crea el grupo de datos de remisión usando filas horizontales.

        Esto evita el solapamiento en pantallas estrechas y facilita
        distribuir el espacio de forma predecible.
        """
        group = QGroupBox("📄 Datos de la Remisión")
        vbox = QVBoxLayout()
        vbox.setSpacing(6)

        # Fila 0: Fechas (Fecha Remisión | Hora Salida | Fecha Aceptación | Hora Aceptación)
        row0 = QHBoxLayout()
        row0.addWidget(QLabel("Fecha Remisión:"))
        self.date_remision = QDateEdit()
        self.date_remision.setCalendarPopup(True)
        self.date_remision.setDisplayFormat("dd/MM/yyyy")
        self.date_remision.setDate(QDate.currentDate())
        row0.addWidget(self.date_remision)

        row0.addSpacing(8)
        row0.addWidget(QLabel("Hora Salida:"))
        self.time_salida = QTimeEdit()
        self.time_salida.setDisplayFormat("HH:mm")
        self.time_salida.setTime(QTime.currentTime())
        self.time_salida.setMaximumWidth(90)
        row0.addWidget(self.time_salida)

        row0.addSpacing(8)
        row0.addWidget(QLabel("Fecha Aceptación:"))
        self.date_aceptacion = QDateEdit()
        self.date_aceptacion.setCalendarPopup(True)
        self.date_aceptacion.setDisplayFormat("dd/MM/yyyy")
        self.date_aceptacion.setDate(QDate.currentDate())
        row0.addWidget(self.date_aceptacion)

        row0.addSpacing(8)
        row0.addWidget(QLabel("Hora Aceptación:"))
        self.time_aceptacion = QTimeEdit()
        self.time_aceptacion.setDisplayFormat("HH:mm")
        self.time_aceptacion.setTime(QTime.currentTime())
        self.time_aceptacion.setMaximumWidth(90)
        row0.addWidget(self.time_aceptacion)

        vbox.addLayout(row0)

        # Fila 1: Placa Ambulancia | Profesional Remite | Prestador
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Placa Ambulancia:"))
        self.txt_placa = QLineEdit()
        # Placa tiene 7 caracteres máximo y campo compacto
        self.txt_placa.setMaxLength(7)
        self.txt_placa.setMaximumWidth(110)
        row1.addWidget(self.txt_placa)

        # Profesional Remite
        row1.addSpacing(10)
        row1.addWidget(QLabel("Profesional Remite:"))
        self.combo_profesional_remite = QComboBox()
        self.combo_profesional_remite.setMinimumWidth(220)
        row1.addWidget(self.combo_profesional_remite)

        # Añadir un stretch extra para ocupar el espacio vacío a la derecha
        row1.addStretch(2)

        vbox.addLayout(row1)

        # Fila 2: Cód. Hab. Recibe | Profesional Recibe | Cargo
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Cód. Hab. Recibe:"))
        self.txt_cod_hab_recibe = QLineEdit()
        self.txt_cod_hab_recibe.setMaxLength(12)
        self.txt_cod_hab_recibe.setMaximumWidth(180)
        row2.addWidget(self.txt_cod_hab_recibe)

        row2.addSpacing(12)
        row2.addWidget(QLabel("Profesional Recibe:"))
        self.txt_profesional_recibe = QLineEdit()
        self.txt_profesional_recibe.setMaxLength(60)
        self.txt_profesional_recibe.setPlaceholderText("Nombre del profesional que recibe...")
        self.txt_profesional_recibe.setMinimumWidth(240)
        row2.addWidget(self.txt_profesional_recibe)

        row2.addSpacing(12)
        row2.addWidget(QLabel("Cargo:"))
        # Reuse existing name to avoid changing presenter logic
        self.txt_cargo_remite = QLineEdit()
        self.txt_cargo_remite.setMaxLength(30)
        self.txt_cargo_remite.setMaximumWidth(200)
        row2.addWidget(self.txt_cargo_remite)

        vbox.addLayout(row2)

        group.setLayout(vbox)
        return group