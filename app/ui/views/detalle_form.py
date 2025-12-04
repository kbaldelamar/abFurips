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
    QGroupBox,
    QLabel,
    QLineEdit,
    QComboBox,
    QSpinBox,
    QMessageBox,
    QScrollArea,
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QIntValidator


class DetalleForm(QWidget):
    """Formulario para gestionar los detalles (FURIPS2)."""
    
    # Señales
    buscar_procedimiento_signal = Signal(str)  # término de búsqueda
    guardar_detalles_signal = Signal(list)  # lista de detalles a guardar
    
    def __init__(self):
        super().__init__()
        self.accidente_id = None
        self.detalles_temp = []  # Lista temporal de detalles
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura la interfaz."""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(8, 8, 8, 8)
        
        # Grupo: Agregar detalle (compacto)
        group_agregar = self._crear_grupo_agregar()
        main_layout.addWidget(group_agregar)
        
        # Grupo: Tabla de detalles (ocupa la mayor parte del espacio)
        group_tabla = self._crear_grupo_tabla()
        main_layout.addWidget(group_tabla, 3)  # Factor de stretch 3 = más espacio
        
        # Grupo: Totales (compacto)
        group_totales = self._crear_grupo_totales()
        main_layout.addWidget(group_totales)
        
        # Botones de acción
        botones_layout = self._crear_botones()
        main_layout.addLayout(botones_layout)
    
    def _crear_grupo_agregar(self) -> QGroupBox:
        """Crea el grupo para agregar nuevos detalles."""
        from PySide6.QtWidgets import QSizePolicy
        
        group = QGroupBox("➕ Agregar Detalle")
        layout = QHBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Tipo Servicio
        layout.addWidget(QLabel("Tipo:"))
        self.combo_tipo_servicio = QComboBox()
        self.combo_tipo_servicio.setMinimumWidth(200)
        layout.addWidget(self.combo_tipo_servicio)
        
        # Código
        layout.addWidget(QLabel("Código:"))
        self.txt_codigo_servicio = QLineEdit()
        self.txt_codigo_servicio.setPlaceholderText("Código + Enter")
        self.txt_codigo_servicio.setMaximumWidth(150)
        self.txt_codigo_servicio.returnPressed.connect(self._on_buscar_por_codigo)
        layout.addWidget(self.txt_codigo_servicio)
        
        # Procedimiento (buscable)
        layout.addWidget(QLabel("Procedimiento:"))
        self.combo_procedimiento = QComboBox()
        self.combo_procedimiento.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.combo_procedimiento.setEditable(True)  # Permitir escribir para buscar
        self.combo_procedimiento.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)  # No insertar nuevos
        self.combo_procedimiento.currentIndexChanged.connect(self._on_procedimiento_seleccionado)
        layout.addWidget(self.combo_procedimiento, 1)
        
        # Cantidad
        layout.addWidget(QLabel("Cant:"))
        self.spin_cantidad = QSpinBox()
        self.spin_cantidad.setMinimum(1)
        self.spin_cantidad.setMaximum(999999)
        self.spin_cantidad.setValue(1)
        self.spin_cantidad.setMaximumWidth(70)
        self.spin_cantidad.valueChanged.connect(self._calcular_valores)
        layout.addWidget(self.spin_cantidad)
        
        # Valor Unitario
        layout.addWidget(QLabel("V.Unit:"))
        self.txt_valor_unitario = QLineEdit("0")
        self.txt_valor_unitario.setValidator(QIntValidator(0, 999999999))
        self.txt_valor_unitario.setMaximumWidth(100)
        self.txt_valor_unitario.textChanged.connect(self._calcular_valores)
        layout.addWidget(self.txt_valor_unitario)
        
        # Valor Facturado
        layout.addWidget(QLabel("V.Fact:"))
        self.txt_valor_facturado = QLineEdit("0")
        self.txt_valor_facturado.setReadOnly(True)
        self.txt_valor_facturado.setStyleSheet("background-color: #e8e8e8;")
        self.txt_valor_facturado.setMaximumWidth(100)
        layout.addWidget(self.txt_valor_facturado)
        
        # Valor Reclamado
        layout.addWidget(QLabel("V.Recl:"))
        self.txt_valor_reclamado = QLineEdit("0")
        self.txt_valor_reclamado.setValidator(QIntValidator(0, 999999999))
        self.txt_valor_reclamado.setMaximumWidth(100)
        layout.addWidget(self.txt_valor_reclamado)
        
        # Botón Agregar
        self.btn_agregar = QPushButton("+ Agregar")
        self.btn_agregar.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        self.btn_agregar.clicked.connect(self._on_agregar)
        layout.addWidget(self.btn_agregar)
        
        # Campos ocultos para compatibilidad
        self.txt_descripcion = QLineEdit()
        self.txt_descripcion.setVisible(False)
        self.txt_buscar_procedimiento = QLineEdit()
        self.txt_buscar_procedimiento.setVisible(False)
        self.btn_buscar = QPushButton()
        self.btn_buscar.setVisible(False)
        
        group.setLayout(layout)
        return group
    
    def _crear_grupo_tabla(self) -> QGroupBox:
        """Crea el grupo con la tabla de detalles."""
        group = QGroupBox("📋 Detalles del Accidente")
        layout = QVBoxLayout()
        
        self.tabla_detalles = QTableWidget()
        self.tabla_detalles.setColumnCount(10)
        self.tabla_detalles.setHorizontalHeaderLabels([
            "Tipo Servicio", "Código", "Descripción", "Cantidad",
            "Valor Unit.", "Valor Fact.", "Valor Recl.", 
            "Proc ID", "Det ID", "Acciones"
        ])
        
        # Configurar columnas
        header = self.tabla_detalles.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(8, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(9, QHeaderView.ResizeToContents)
        
        # Ocultar columnas ID
        self.tabla_detalles.setColumnHidden(7, True)
        self.tabla_detalles.setColumnHidden(8, True)
        
        self.tabla_detalles.setAlternatingRowColors(True)
        self.tabla_detalles.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla_detalles.setMinimumHeight(400)  # Altura mínima para que sea más visible
        
        layout.addWidget(self.tabla_detalles)
        group.setLayout(layout)
        return group
    
    def _crear_grupo_totales(self) -> QGroupBox:
        """Crea el grupo de totales."""
        group = QGroupBox("💰 Totales")
        layout = QHBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(10, 5, 10, 5)
        
        layout.addWidget(QLabel("Total Facturado:"))
        self.lbl_total_facturado = QLabel("$ 0")
        self.lbl_total_facturado.setStyleSheet("font-size: 12pt; font-weight: bold; color: #1976D2;")
        layout.addWidget(self.lbl_total_facturado)
        
        layout.addSpacing(30)
        
        layout.addWidget(QLabel("Total Reclamado:"))
        self.lbl_total_reclamado = QLabel("$ 0")
        self.lbl_total_reclamado.setStyleSheet("font-size: 12pt; font-weight: bold; color: #388E3C;")
        layout.addWidget(self.lbl_total_reclamado)
        
        layout.addStretch()
        group.setLayout(layout)
        return group
    
    def _crear_botones(self) -> QHBoxLayout:
        """Crea los botones de acción."""
        layout = QHBoxLayout()
        
        self.btn_guardar_todo = QPushButton("💾 Guardar Todos los Detalles")
        self.btn_guardar_todo.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold; padding: 8px 20px;")
        self.btn_guardar_todo.clicked.connect(self._on_guardar_todo)
        layout.addWidget(self.btn_guardar_todo)
        
        self.btn_limpiar = QPushButton("🗑️ Limpiar Formulario")
        self.btn_limpiar.clicked.connect(self._on_limpiar)
        layout.addWidget(self.btn_limpiar)
        
        layout.addStretch()
        return layout
    
    # Eventos
    def _on_buscar_por_codigo(self):
        """Busca procedimiento por código cuando se presiona Enter."""
        codigo = self.txt_codigo_servicio.text().strip()
        print(f"🔍 Buscando por código: '{codigo}'")
        if codigo:
            self.buscar_procedimiento_signal.emit(codigo)
    
    def _on_buscar_procedimiento(self, texto: str):
        """Busca procedimientos mientras el usuario escribe."""
        print(f"📝 DetalleForm._on_buscar_procedimiento() - texto: '{texto}', len={len(texto)}")
        if len(texto) >= 3:
            print(f"✓ Emitiendo signal buscar_procedimiento_signal con: '{texto}'")
            self.buscar_procedimiento_signal.emit(texto)
        else:
            print(f"⚠️ Texto muy corto, no se emite signal")
    
    def _on_buscar_click(self):
        """Busca procedimientos al hacer clic."""
        print(f"🔘 DetalleForm._on_buscar_click() - Botón Buscar presionado")
        texto = self.txt_buscar_procedimiento.text().strip()
        print(f"📝 Texto en campo: '{texto}'")
        if texto:
            print(f"✓ Emitiendo signal buscar_procedimiento_signal con: '{texto}'")
            self.buscar_procedimiento_signal.emit(texto)
        else:
            print(f"⚠️ Campo vacío, no se emite signal")
    
    def _on_procedimiento_seleccionado(self, index: int):
        """Cuando se selecciona un procedimiento."""
        if index >= 0:
            data = self.combo_procedimiento.currentData()
            if data:
                self.txt_codigo_servicio.setText(data.get("codigo", ""))
                self.txt_descripcion.setText(data.get("descripcion", ""))
                self.txt_valor_unitario.setText(str(data.get("valor", 0)))
                self._calcular_valores()
    
    def _calcular_valores(self):
        """Calcula el valor facturado."""
        try:
            cantidad = self.spin_cantidad.value()
            valor_unitario = int(self.txt_valor_unitario.text() or "0")
            valor_facturado = cantidad * valor_unitario
            
            self.txt_valor_facturado.setText(str(valor_facturado))
            
            if not self.txt_valor_reclamado.text() or self.txt_valor_reclamado.text() == "0":
                self.txt_valor_reclamado.setText(str(valor_facturado))
        except:
            pass
    
    def _on_agregar(self):
        """Agrega el detalle a la tabla."""
        if self.combo_tipo_servicio.currentIndex() == 0:
            QMessageBox.warning(self, "Error", "Debe seleccionar un tipo de servicio")
            return
        
        if not self.txt_descripcion.text().strip() and self.combo_procedimiento.currentIndex() == 0:
            QMessageBox.warning(self, "Error", "Debe seleccionar un procedimiento o ingresar una descripción")
            return
        
        datos = {
            "tipo_servicio_id": self.combo_tipo_servicio.currentData(),
            "tipo_servicio_nombre": self.combo_tipo_servicio.currentText(),
            "procedimiento_id": self.combo_procedimiento.currentData().get("id") if self.combo_procedimiento.currentIndex() > 0 else None,
            "codigo_servicio": self.txt_codigo_servicio.text().strip() or None,
            "descripcion": self.txt_descripcion.text().strip() or None,
            "cantidad": self.spin_cantidad.value(),
            "valor_unitario": int(self.txt_valor_unitario.text() or "0"),
            "valor_facturado": int(self.txt_valor_facturado.text() or "0"),
            "valor_reclamado": int(self.txt_valor_reclamado.text() or "0"),
        }
        
        self._agregar_fila_tabla(datos)
        self._limpiar_campos_entrada()
        self._actualizar_totales()
    
    def _agregar_fila_tabla(self, datos: dict):
        """Agrega una fila a la tabla."""
        fila = self.tabla_detalles.rowCount()
        self.tabla_detalles.insertRow(fila)
        
        self.tabla_detalles.setItem(fila, 0, QTableWidgetItem(datos["tipo_servicio_nombre"]))
        self.tabla_detalles.setItem(fila, 1, QTableWidgetItem(datos["codigo_servicio"] or ""))
        self.tabla_detalles.setItem(fila, 2, QTableWidgetItem(datos["descripcion"] or ""))
        self.tabla_detalles.setItem(fila, 3, QTableWidgetItem(str(datos["cantidad"])))
        self.tabla_detalles.setItem(fila, 4, QTableWidgetItem(f"${datos['valor_unitario']:,}"))
        self.tabla_detalles.setItem(fila, 5, QTableWidgetItem(f"${datos['valor_facturado']:,}"))
        self.tabla_detalles.setItem(fila, 6, QTableWidgetItem(f"${datos['valor_reclamado']:,}"))
        self.tabla_detalles.setItem(fila, 7, QTableWidgetItem(str(datos.get("procedimiento_id") or "")))
        self.tabla_detalles.setItem(fila, 8, QTableWidgetItem(str(datos.get("detalle_id") or "")))
        
        btn_eliminar = QPushButton("🗑️")
        btn_eliminar.setStyleSheet("background-color: #f44336; color: white;")
        btn_eliminar.clicked.connect(self._on_eliminar_fila)
        self.tabla_detalles.setCellWidget(fila, 9, btn_eliminar)
        
        self.detalles_temp.append(datos)
    
    def _on_eliminar_fila(self):
        """Elimina una fila de la tabla."""
        # Identificar qué botón fue presionado
        boton = self.sender()
        if not boton:
            return
        
        # Encontrar la fila del botón
        fila = None
        for i in range(self.tabla_detalles.rowCount()):
            if self.tabla_detalles.cellWidget(i, 9) == boton:
                fila = i
                break
        
        if fila is None:
            return
        
        respuesta = QMessageBox.question(
            self, "Confirmar", "¿Desea eliminar este detalle?",
            QMessageBox.Yes | QMessageBox.No
        )
        if respuesta == QMessageBox.Yes:
            print(f"🗑️ Eliminando fila {fila}")
            self.tabla_detalles.removeRow(fila)
            if fila < len(self.detalles_temp):
                del self.detalles_temp[fila]
            self._actualizar_totales()
            print(f"✓ Fila eliminada. Filas restantes: {self.tabla_detalles.rowCount()}")
    
    def _actualizar_totales(self):
        """Actualiza los totales."""
        total_facturado = 0
        total_reclamado = 0
        
        for i in range(self.tabla_detalles.rowCount()):
            val_fact = self.tabla_detalles.item(i, 5).text().replace("$", "").replace(",", "")
            val_recl = self.tabla_detalles.item(i, 6).text().replace("$", "").replace(",", "")
            total_facturado += int(val_fact) if val_fact else 0
            total_reclamado += int(val_recl) if val_recl else 0
        
        self.lbl_total_facturado.setText(f"$ {total_facturado:,}")
        self.lbl_total_reclamado.setText(f"$ {total_reclamado:,}")
    
    def _limpiar_campos_entrada(self):
        """Limpia los campos de entrada."""
        self.txt_buscar_procedimiento.clear()
        self.combo_procedimiento.setCurrentIndex(0)
        self.txt_codigo_servicio.clear()
        self.txt_descripcion.clear()
        self.spin_cantidad.setValue(1)
        self.txt_valor_unitario.setText("0")
        self.txt_valor_facturado.setText("0")
        self.txt_valor_reclamado.setText("0")
    
    def _on_guardar_todo(self):
        """Guarda todos los detalles."""
        if self.tabla_detalles.rowCount() == 0:
            QMessageBox.warning(self, "Sin detalles", "No hay detalles para guardar")
            return
        
        detalles = []
        for i in range(self.tabla_detalles.rowCount()):
            detalle = {
                "tipo_servicio_id": self._get_tipo_servicio_id_from_row(i),
                "procedimiento_id": int(self.tabla_detalles.item(i, 7).text()) if self.tabla_detalles.item(i, 7).text() else None,
                "codigo_servicio": self.tabla_detalles.item(i, 1).text() or None,
                "descripcion": self.tabla_detalles.item(i, 2).text() or None,
                "cantidad": int(self.tabla_detalles.item(i, 3).text()),
                "valor_unitario": int(self.tabla_detalles.item(i, 4).text().replace("$", "").replace(",", "")),
                "valor_facturado": int(self.tabla_detalles.item(i, 5).text().replace("$", "").replace(",", "")),
                "valor_reclamado": int(self.tabla_detalles.item(i, 6).text().replace("$", "").replace(",", "")),
            }
            detalles.append(detalle)
        
        self.guardar_detalles_signal.emit(detalles)
    
    def _get_tipo_servicio_id_from_row(self, fila: int) -> int:
        """Obtiene el tipo_servicio_id de una fila."""
        if fila < len(self.detalles_temp):
            return self.detalles_temp[fila]["tipo_servicio_id"]
        return 1
    
    def _on_limpiar(self):
        """Limpia todo el formulario."""
        respuesta = QMessageBox.question(
            self, "Confirmar", "¿Desea limpiar todos los detalles? Esta acción no se puede deshacer.",
            QMessageBox.Yes | QMessageBox.No
        )
        if respuesta == QMessageBox.Yes:
            self.limpiar_formulario()
    
    # Métodos públicos
    def cargar_tipos_servicio(self, tipos: list):
        """Carga los tipos de servicio en el combo."""
        self.combo_tipo_servicio.clear()
        self.combo_tipo_servicio.addItem("-- Seleccione --", None)
        for tipo in tipos:
            self.combo_tipo_servicio.addItem(tipo["descripcion"], tipo["id"])
    
    def cargar_procedimientos(self, procedimientos: list):
        """Carga los procedimientos en el combo."""
        print(f"📦 DetalleForm.cargar_procedimientos() - Recibidos {len(procedimientos)} procedimientos")
        self.combo_procedimiento.clear()
        self.combo_procedimiento.addItem("-- Ninguno / Ingreso Manual --", None)
        for i, proc in enumerate(procedimientos):
            texto = f"{proc['codigo']} - {proc['descripcion']} (${proc['valor']:,})"
            self.combo_procedimiento.addItem(texto, proc)
            print(f"  [{i+1}] {texto}")
        print(f"✓ Combo cargado con {len(procedimientos)} items (+ 1 default)")
        
        # Si hay resultados, mostrar el dropdown automáticamente
        if len(procedimientos) > 1:
            print(f"📋 Mostrando dropdown automáticamente...")
            self.combo_procedimiento.showPopup()
    
    def cargar_detalles(self, detalles: list):
        """Carga detalles existentes del accidente."""
        self.tabla_detalles.setRowCount(0)
        self.detalles_temp.clear()
        
        for detalle in detalles:
            datos = {
                "tipo_servicio_id": detalle["tipo_servicio_id"],
                "tipo_servicio_nombre": detalle["tipo_servicio_nombre"],
                "procedimiento_id": detalle.get("procedimiento_id"),
                "codigo_servicio": detalle.get("codigo_servicio"),
                "descripcion": detalle.get("descripcion"),
                "cantidad": detalle["cantidad"],
                "valor_unitario": detalle["valor_unitario"],
                "valor_facturado": detalle["valor_facturado"],
                "valor_reclamado": detalle["valor_reclamado"],
                "detalle_id": detalle.get("id"),
            }
            self._agregar_fila_tabla(datos)
        
        self._actualizar_totales()
    
    def limpiar_formulario(self):
        """Limpia todo el formulario."""
        self.tabla_detalles.setRowCount(0)
        self.detalles_temp.clear()
        self._limpiar_campos_entrada()
        self.combo_tipo_servicio.setCurrentIndex(0)
        self._actualizar_totales()
    
    def mostrar_detalles_guardados(self):
        """Muestra mensaje de éxito."""
        QMessageBox.information(self, "Éxito", "Todos los detalles han sido guardados correctamente")
