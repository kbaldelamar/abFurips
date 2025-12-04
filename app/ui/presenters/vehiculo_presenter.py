"""
Presenter para gestión del vehículo.
"""
from typing import Optional, Dict, Any

from app.ui.views.vehiculo_form import VehiculoForm
from app.data.repositories.vehiculo_repo import VehiculoRepository
from app.data.repositories.catalogo_repo import CatalogoRepository
from app.config.db import get_db_session
from app.data.models.vehiculo import Vehiculo


class VehiculoPresenter:
    """Presenter para el formulario de vehículo."""
    
    def __init__(self, view: VehiculoForm):
        self.view = view
        self.accidente_id: Optional[int] = None
        self.propietario_cargado_callback = None  # Callback para notificar cuando se carga propietario
        
        # Conectar señales
        self._conectar_signals()
        
        # Cargar catálogos
        self._cargar_catalogos()
    
    def set_propietario_cargado_callback(self, callback):
        """Establece el callback para notificar cuando se carga un propietario desde vehículo."""
        self.propietario_cargado_callback = callback
    
    def _conectar_signals(self):
        """Conecta las señales de la vista."""
        self.view.buscar_vehiculo_signal.connect(self.buscar_vehiculo)
        self.view.guardar_vehiculo_signal.connect(self.guardar_vehiculo)
        self.view.actualizar_vehiculo_signal.connect(self.actualizar_vehiculo)
        self.view.anular_vehiculo_signal.connect(self.anular_vehiculo)
    
    def _cargar_catalogos(self):
        """Carga los catálogos necesarios."""
        try:
            with get_db_session() as session:
                catalogo_repo = CatalogoRepository(session)
                
                # Tipos de vehículo
                tipos = catalogo_repo.get_tipos_vehiculo()
                self.view.cargar_tipos_vehiculo(
                    [{"id": t.id, "descripcion": t.descripcion} for t in tipos]
                )
                
                # Estados de aseguramiento
                estados = catalogo_repo.get_estados_aseguramiento()
                self.view.cargar_estados_aseguramiento(
                    [{"id": e.id, "descripcion": e.descripcion} for e in estados]
                )
        except Exception as e:
            print(f"Error cargando catálogos: {e}")
    
    def set_accidente_id(self, accidente_id: int):
        """Establece el ID del accidente actual."""
        self.accidente_id = accidente_id
        self.cargar_vehiculo_existente()
    
    def notificar_propietario_guardado(self):
        """Notifica que se guardó/actualizó un propietario - permite guardar vehículo."""
        # Limpiar todas las marcas de validación
        if hasattr(self.view, 'vehiculo_cambiar_propietario'):
            self.view.vehiculo_cambiar_propietario = False
        if hasattr(self.view, 'vehiculo_propietario_bd'):
            self.view.vehiculo_propietario_bd = None
        
        # Marcar que el propietario fue actualizado recientemente
        self.view.propietario_recien_actualizado = True
        
        # Habilitar el botón de guardar
        self.view.btn_guardar.setEnabled(True)
        self.view.lbl_vehiculo_encontrado.setText("✅ Propietario actualizado. Puede guardar el vehículo")
        self.view.lbl_vehiculo_encontrado.setStyleSheet("color: green; font-weight: bold;")
        print("✅ VehiculoPresenter: Propietario actualizado, botón Guardar habilitado")
    
    def buscar_vehiculo(self, placa: str):
        """Busca un vehículo por placa y valida conflicto de propietarios."""
        if not placa:
            return
        
        try:
            with get_db_session() as session:
                vehiculo_repo = VehiculoRepository(session)
                vehiculo = vehiculo_repo.get_by_placa(placa)
                
                if vehiculo:
                    # SEGURIDAD: Verificar si ya tiene propietario diferente al actual
                    from app.data.repositories.propietario_repo import PropietarioRepository
                    propietario_repo = PropietarioRepository(session)
                    propietarios_actuales = propietario_repo.get_by_accidente(self.accidente_id)
                    propietario_actual_id = propietarios_actuales[0].persona_id if propietarios_actuales else None
                    
                    if vehiculo.propietario_id and propietario_actual_id and vehiculo.propietario_id != propietario_actual_id:
                        # CONFLICTO: Vehículo existente tiene otro propietario
                        from app.data.repositories.persona_repo import PersonaRepository
                        persona_repo = PersonaRepository(session)
                        
                        persona_vehiculo = persona_repo.get_by_id(vehiculo.propietario_id)
                        persona_actual = persona_repo.get_by_id(propietario_actual_id)
                        
                        nombre_vehiculo = f"{persona_vehiculo.primer_nombre} {persona_vehiculo.primer_apellido}" if persona_vehiculo else "Desconocido"
                        doc_vehiculo = persona_vehiculo.numero_identificacion if persona_vehiculo else "N/A"
                        nombre_actual = f"{persona_actual.primer_nombre} {persona_actual.primer_apellido}" if persona_actual else "Desconocido"
                        doc_actual = persona_actual.numero_identificacion if persona_actual else "N/A"
                        
                        from PySide6.QtWidgets import QMessageBox
                        
                        # Mensaje detallado con opciones claras
                        msg = QMessageBox(self.view)
                        msg.setIcon(QMessageBox.Warning)
                        msg.setWindowTitle("⚠️ Conflicto de Propietarios")
                        msg.setText(f"<b style='font-size: 11pt;'>El vehículo con placa '{placa}' ya existe en la base de datos</b>")
                        msg.setInformativeText(
                            f"<br><b style='color: #1976D2;'>📋 Propietario registrado en BD:</b><br>"
                            f"&nbsp;&nbsp;&nbsp;• Nombre: <b>{nombre_vehiculo}</b><br>"
                            f"&nbsp;&nbsp;&nbsp;• Documento: {doc_vehiculo}<br><br>"
                            f"<b style='color: #D32F2F;'>📋 Propietario actual del accidente:</b><br>"
                            f"&nbsp;&nbsp;&nbsp;• Nombre: <b>{nombre_actual}</b><br>"
                            f"&nbsp;&nbsp;&nbsp;• Documento: {doc_actual}<br><br>"
                            f"<b style='color: red; font-size: 10pt;'>⚠️ ¿Qué desea hacer?</b>"
                        )
                        
                        btn_mantener = msg.addButton("Mantener propietario BD", QMessageBox.AcceptRole)
                        btn_cambiar = msg.addButton("Cambiar propietario", QMessageBox.ActionRole)
                        btn_cancelar = msg.addButton("Cancelar", QMessageBox.RejectRole)
                        
                        msg.setDetailedText(
                            "OPCIÓN 1: Mantener propietario BD\n"
                            f"  → El vehículo se asociará al accidente\n"
                            f"  → El propietario seguirá siendo: {nombre_vehiculo}\n"
                            f"  → El propietario actual ({nombre_actual}) NO cambiará\n\n"
                            "OPCIÓN 2: Cambiar propietario\n"
                            f"  → Primero debe GUARDAR en el tab Propietario\n"
                            f"  → Luego se actualizará el vehículo en BD\n"
                            f"  → El nuevo propietario será: {nombre_actual}\n\n"
                            "OPCIÓN 3: Cancelar\n"
                            "  → No se hará ningún cambio"
                        )
                        
                        msg.exec()
                        clicked_button = msg.clickedButton()
                        
                        if clicked_button == btn_cancelar:
                            self.view.lbl_vehiculo_encontrado.setText("❌ Búsqueda cancelada por el usuario")
                            self.view.lbl_vehiculo_encontrado.setStyleSheet("color: red; font-weight: bold;")
                            self.view.txt_placa.clear()
                            return
                        
                        elif clicked_button == btn_cambiar:
                            # Opción: Cambiar propietario del vehículo
                            # Marcar que se quiere cambiar el propietario
                            self.view.vehiculo_cambiar_propietario = True
                            self.view.vehiculo_propietario_bd = vehiculo.propietario_id
                            
                            # Cargar datos del vehículo
                            self.view.cargar_vehiculo({
                                "id": vehiculo.id,
                                "placa": vehiculo.placa,
                                "marca": vehiculo.marca,
                                "tipo_vehiculo_id": vehiculo.tipo_vehiculo_id,
                                "aseguradora_codigo": vehiculo.aseguradora_codigo,
                                "numero_poliza": vehiculo.numero_poliza,
                                "vigencia_inicio": vehiculo.vigencia_inicio,
                                "vigencia_fin": vehiculo.vigencia_fin,
                                "estado_aseguramiento_id": vehiculo.estado_aseguramiento_id,
                            })
                            
                            # Verificar si el propietario actual ya está guardado en este accidente
                            if propietarios_actuales:
                                # YA HAY un propietario guardado en este accidente
                                from PySide6.QtWidgets import QMessageBox
                                QMessageBox.information(
                                    self.view,
                                    "📝 Cambio de Propietario",
                                    f"<b>Cambio de propietario confirmado:</b><br><br>"
                                    f"Propietario en BD: <b>{nombre_vehiculo}</b> (Doc: {doc_vehiculo})<br>"
                                    f"Nuevo propietario: <b>{nombre_actual}</b> (Doc: {doc_actual})<br><br>"
                                    f"✓ Puede guardar el vehículo ahora.<br>"
                                    f"⚠️ El vehículo se actualizará con el nuevo propietario en BD."
                                )
                                
                                # Marcar que se autorizó el cambio de propietario (omite validación estricta)
                                self.view.propietario_recien_actualizado = True
                                
                                self.view.lbl_vehiculo_encontrado.setText("✅ Listo para guardar. El propietario del vehículo será actualizado")
                                self.view.lbl_vehiculo_encontrado.setStyleSheet("color: green; font-weight: bold;")
                                self.view.btn_guardar.setEnabled(True)  # Habilitar porque propietario ya existe
                            else:
                                # NO hay propietario guardado aún, debe guardarlo primero
                                from PySide6.QtWidgets import QMessageBox
                                QMessageBox.information(
                                    self.view,
                                    "📝 Cambio de Propietario",
                                    f"<b>Para cambiar el propietario del vehículo:</b><br><br>"
                                    f"1. Vaya al tab <b>Propietario</b><br>"
                                    f"2. Busque y guarde: <b>{nombre_actual}</b><br>"
                                    f"3. Regrese al tab Vehículo<br>"
                                    f"4. Guarde el vehículo<br><br>"
                                    f"⚠️ El vehículo en BD se actualizará con el nuevo propietario."
                                )
                                
                                self.view.lbl_vehiculo_encontrado.setText("⚠️ Primero guarde el propietario, luego el vehículo")
                                self.view.lbl_vehiculo_encontrado.setStyleSheet("color: orange; font-weight: bold;")
                                self.view.btn_guardar.setEnabled(False)  # Deshabilitar hasta que se guarde propietario
                            return
                        
                        # Si llegamos aquí: btn_mantener (mantener propietario de BD)
                        # Continuar con carga normal
                    
                    # Cargar vehículo existente
                    self.view.cargar_vehiculo({
                        "id": vehiculo.id,
                        "placa": vehiculo.placa,
                        "marca": vehiculo.marca,
                        "tipo_vehiculo_id": vehiculo.tipo_vehiculo_id,
                        "aseguradora_codigo": vehiculo.aseguradora_codigo,
                        "numero_poliza": vehiculo.numero_poliza,
                        "vigencia_inicio": vehiculo.vigencia_inicio,
                        "vigencia_fin": vehiculo.vigencia_fin,
                        "estado_aseguramiento_id": vehiculo.estado_aseguramiento_id,
                    })
                    
                    self.view.lbl_vehiculo_encontrado.setText(f"✓ Vehículo encontrado en BD (ID: {vehiculo.id})")
                    self.view.lbl_vehiculo_encontrado.setStyleSheet("color: green; font-weight: bold;")
                    
                    # Si el vehículo tiene propietario, notificar para cargar en tab Propietario
                    if vehiculo.propietario_id and self.propietario_cargado_callback:
                        self.propietario_cargado_callback(vehiculo.propietario_id)
                else:
                    self.view.lbl_vehiculo_encontrado.setText("⚠️ Vehículo no encontrado. Se creará nuevo.")
                    self.view.vehiculo_id_actual = None
        except Exception as e:
            print(f"Error buscando vehículo: {e}")
            import traceback
            traceback.print_exc()
            self.view.lbl_vehiculo_encontrado.setText(f"❌ Error: {str(e)}")
    
    def guardar_vehiculo(self, datos: Dict[str, Any]):
        """Guarda un vehículo con validación de cambio de propietario."""
        if not self.accidente_id:
            print("Error: No hay accidente seleccionado")
            return
        
        # Validaciones
        if not datos.get("estado_aseguramiento_id"):
            print("❌ Error: Debe seleccionar el estado de aseguramiento")
            return
        
        # SEGURIDAD CRÍTICA: Si el vehículo ya existe en BD, verificar que su propietario esté en el accidente
        # EXCEPCIÓN: Si el propietario fue recién actualizado, omitir validación
        propietario_actualizado = hasattr(self.view, 'propietario_recien_actualizado') and self.view.propietario_recien_actualizado
        
        if datos.get("vehiculo_id") and not propietario_actualizado:
            from PySide6.QtWidgets import QMessageBox
            from app.data.repositories.propietario_repo import PropietarioRepository
            from app.data.repositories.persona_repo import PersonaRepository
            
            try:
                with get_db_session() as session:
                    vehiculo_repo = VehiculoRepository(session)
                    vehiculo = vehiculo_repo.get_by_id(datos["vehiculo_id"])
                    
                    if vehiculo and vehiculo.propietario_id:
                        # Verificar si el propietario del vehículo está guardado en este accidente
                        propietario_repo = PropietarioRepository(session)
                        propietarios = propietario_repo.get_by_accidente(self.accidente_id)
                        
                        if propietarios:
                            propietario_accidente_id = propietarios[0].persona_id
                            
                            if vehiculo.propietario_id != propietario_accidente_id:
                                # El propietario del vehículo es diferente al del accidente
                                persona_repo = PersonaRepository(session)
                                persona_vehiculo = persona_repo.get_by_id(vehiculo.propietario_id)
                                persona_accidente = persona_repo.get_by_id(propietario_accidente_id)
                                
                                nombre_vehiculo = f"{persona_vehiculo.primer_nombre} {persona_vehiculo.primer_apellido}" if persona_vehiculo else "Desconocido"
                                nombre_accidente = f"{persona_accidente.primer_nombre} {persona_accidente.primer_apellido}" if persona_accidente else "Desconocido"
                                
                                QMessageBox.warning(
                                    self.view,
                                    "⚠️ Propietarios no coinciden",
                                    f"<b>No puede guardar el vehículo</b><br><br>"
                                    f"Propietario del vehículo en BD: <b>{nombre_vehiculo}</b><br>"
                                    f"Propietario guardado en el accidente: <b>{nombre_accidente}</b><br><br>"
                                    f"<b>Debe actualizar el propietario del accidente:</b><br>"
                                    f"1. Vaya al tab <b>Propietario</b><br>"
                                    f"2. Verifique que los datos sean de <b>{nombre_vehiculo}</b><br>"
                                    f"3. Haga clic en <b>Actualizar Propietario</b><br>"
                                    f"4. Regrese al tab Vehículo y guarde"
                                )
                                return
                        else:
                            # No hay propietario guardado en el accidente
                            persona_repo = PersonaRepository(session)
                            persona_vehiculo = persona_repo.get_by_id(vehiculo.propietario_id)
                            nombre_vehiculo = f"{persona_vehiculo.primer_nombre} {persona_vehiculo.primer_apellido}" if persona_vehiculo else "Desconocido"
                            
                            QMessageBox.warning(
                                self.view,
                                "⚠️ Propietario no guardado",
                                f"<b>Debe guardar el propietario primero</b><br><br>"
                                f"El vehículo pertenece a: <b>{nombre_vehiculo}</b><br><br>"
                                f"Pasos:<br>"
                                f"1. Vaya al tab <b>Propietario</b><br>"
                                f"2. Busque por documento o complete los datos<br>"
                                f"3. Clic en <b>Guardar Propietario</b><br>"
                                f"4. Regrese al tab Vehículo<br>"
                                f"5. Guarde el vehículo"
                            )
                            return
            except Exception as e:
                print(f"Error validando propietario del vehículo: {e}")
                import traceback
                traceback.print_exc()
                return
        
        # SEGURIDAD: Si se marcó cambio de propietario, verificar que esté guardado
        if hasattr(self.view, 'vehiculo_cambiar_propietario') and self.view.vehiculo_cambiar_propietario:
            from PySide6.QtWidgets import QMessageBox
            from app.data.repositories.propietario_repo import PropietarioRepository
            
            try:
                with get_db_session() as session:
                    propietario_repo = PropietarioRepository(session)
                    propietarios = propietario_repo.get_by_accidente(self.accidente_id)
                    
                    if not propietarios:
                        QMessageBox.warning(
                            self.view,
                            "⚠️ Propietario no guardado",
                            "<b>Debe guardar el propietario primero</b><br><br>"
                            "Pasos:<br>"
                            "1. Vaya al tab <b>Propietario</b><br>"
                            "2. Complete los datos<br>"
                            "3. Clic en <b>Guardar Propietario</b><br>"
                            "4. Regrese al tab Vehículo<br>"
                            "5. Guarde el vehículo"
                        )
                        return
                    
                    # Verificar que el propietario guardado es diferente al del vehículo en BD
                    propietario_guardado_id = propietarios[0].persona_id
                    vehiculo_propietario_bd = self.view.vehiculo_propietario_bd
                    
                    if propietario_guardado_id == vehiculo_propietario_bd:
                        QMessageBox.warning(
                            self.view,
                            "⚠️ Propietario no cambió",
                            "<b>El propietario guardado es el mismo que está en BD</b><br><br>"
                            "Si desea cambiar el propietario:<br>"
                            "1. Vaya al tab Propietario<br>"
                            "2. Busque o ingrese otro propietario<br>"
                            "3. Guárdelo<br>"
                            "4. Regrese y guarde el vehículo"
                        )
                        return
                    
                    # Todo correcto: limpiar marcas y continuar con guardado
                    self.view.vehiculo_cambiar_propietario = False
                    self.view.vehiculo_propietario_bd = None
                    self.view.btn_guardar.setEnabled(True)
                    
            except Exception as e:
                print(f"Error validando propietario: {e}")
                return
        
        try:
            with get_db_session() as session:
                vehiculo_repo = VehiculoRepository(session)
                
                # Verificar si ya existe un vehículo para este accidente
                vehiculo_existente = vehiculo_repo.get_by_accidente(self.accidente_id)
                if vehiculo_existente and not datos.get("vehiculo_id"):
                    print("❌ Ya existe un vehículo registrado para este accidente")
                    return
                
                # CASO 1: Vehículo encontrado por búsqueda (ya existe en BD)
                if datos.get("vehiculo_id"):
                    vehiculo_id = datos["vehiculo_id"]
                    vehiculo = vehiculo_repo.get_by_id(vehiculo_id)
                    
                    if not vehiculo:
                        print(f"❌ ERROR: Vehículo ID {vehiculo_id} no encontrado")
                        return
                    
                    # Si hay propietario en el accidente, actualizar el vehículo
                    from app.data.repositories.propietario_repo import PropietarioRepository
                    propietario_repo = PropietarioRepository(session)
                    propietarios = propietario_repo.get_by_accidente(self.accidente_id)
                    propietario_actual_id = propietarios[0].persona_id if propietarios else None
                    
                    if propietario_actual_id and vehiculo.propietario_id != propietario_actual_id:
                        propietario_anterior = vehiculo.propietario_id
                        vehiculo.propietario_id = propietario_actual_id
                        session.flush()
                        print(f"  🔄 Propietario del vehículo actualizado: {propietario_anterior} → {propietario_actual_id}")
                    
                    print(f"  ✓ Usando vehículo existente ID={vehiculo.id}, propietario_id={vehiculo.propietario_id}")
                
                # CASO 2: Crear nuevo vehículo
                else:
                    # Obtener propietario del accidente si existe
                    from app.data.repositories.propietario_repo import PropietarioRepository
                    propietario_repo = PropietarioRepository(session)
                    propietarios = propietario_repo.get_by_accidente(self.accidente_id)
                    propietario_id = propietarios[0].persona_id if propietarios else None
                    
                    # Crear vehículo
                    vehiculo = Vehiculo(
                        placa=datos["placa"],
                        marca=datos["marca"],
                        tipo_vehiculo_id=datos["tipo_vehiculo_id"],
                        aseguradora_codigo=datos["aseguradora_codigo"],
                        numero_poliza=datos["numero_poliza"],
                        vigencia_inicio=datos["vigencia_inicio"],
                        vigencia_fin=datos["vigencia_fin"],
                        estado_aseguramiento_id=datos["estado_aseguramiento_id"],
                        propietario_id=propietario_id,
                        estado=1
                    )
                    
                    vehiculo = vehiculo_repo.create(vehiculo)
                    session.flush()
                    print(f"  ✓ Vehículo creado con ID={vehiculo.id}, propietario_id={propietario_id}")
                
                # Asociar vehículo al accidente (CRÍTICO)
                from app.data.repositories.accidente_repo import AccidenteRepository
                accidente_repo = AccidenteRepository(session)
                accidente = accidente_repo.get_by_id(self.accidente_id)
                
                if not accidente:
                    session.rollback()
                    print(f"  ❌ ERROR: Accidente ID {self.accidente_id} no encontrado")
                    return
                
                print(f"  📌 ANTES: Accidente.vehiculo_id = {accidente.vehiculo_id}")
                accidente.vehiculo_id = vehiculo.id
                session.flush()
                print(f"  📌 DESPUÉS: Accidente.vehiculo_id = {accidente.vehiculo_id}")
                
                # Verificar la asociación antes de commit
                session.refresh(accidente)
                if accidente.vehiculo_id != vehiculo.id:
                    session.rollback()
                    print(f"  ❌ ERROR: No se pudo asociar vehiculo_id al accidente")
                    return
                
                session.commit()
                print(f"  ✅ COMMIT exitoso - Vehículo {vehiculo.id} asociado a Accidente {self.accidente_id}")
                
                placa = vehiculo.placa or "N/A"
                print(f"✓ Vehículo guardado: {placa}")
                
                # Limpiar la marca de propietario recién actualizado
                if hasattr(self.view, 'propietario_recien_actualizado'):
                    self.view.propietario_recien_actualizado = False
                
                # Mostrar mensaje de éxito con información de asociación
                self.view.lbl_estado.setText(f"✅ Vehículo guardado exitosamente (ID: {vehiculo.id}, Placa: {placa})")
                self.view.lbl_estado.setStyleSheet(
                    "background: #C8E6C9; color: #2E7D32; padding: 8px; border-radius: 4px; "
                    "font-weight: bold; border: 2px solid #4CAF50;"
                )
                self.view.lbl_estado.setVisible(True)
                
                self.view.mostrar_vehiculo_guardado(vehiculo.id, placa)
                
        except Exception as e:
            print(f"❌ Error guardando vehículo: {e}")
            import traceback
            traceback.print_exc()
    
    def actualizar_vehiculo(self, datos: Dict[str, Any]):
        """Actualiza un vehículo existente."""
        if not self.accidente_id:
            print("Error: No hay accidente seleccionado")
            return
        
        if not datos.get("vehiculo_id"):
            print("❌ Error: No hay vehículo cargado para actualizar")
            return
        
        # Validaciones
        if not datos.get("estado_aseguramiento_id"):
            print("❌ Error: Debe seleccionar el estado de aseguramiento")
            return
        
        try:
            with get_db_session() as session:
                vehiculo_repo = VehiculoRepository(session)
                
                vehiculo = vehiculo_repo.get_by_id(datos["vehiculo_id"])
                if not vehiculo:
                    print("❌ Error: Vehículo no encontrado")
                    return
                
                # Obtener propietario del accidente si existe
                from app.data.repositories.propietario_repo import PropietarioRepository
                propietario_repo = PropietarioRepository(session)
                propietarios = propietario_repo.get_by_accidente(self.accidente_id)
                if propietarios:
                    vehiculo.propietario_id = propietarios[0].persona_id
                
                # Actualizar datos
                vehiculo.placa = datos["placa"]
                vehiculo.marca = datos["marca"]
                vehiculo.tipo_vehiculo_id = datos["tipo_vehiculo_id"]
                vehiculo.aseguradora_codigo = datos["aseguradora_codigo"]
                vehiculo.numero_poliza = datos["numero_poliza"]
                vehiculo.vigencia_inicio = datos["vigencia_inicio"]
                vehiculo.vigencia_fin = datos["vigencia_fin"]
                vehiculo.estado_aseguramiento_id = datos["estado_aseguramiento_id"]
                
                session.flush()
                
                # Verificar que el accidente tenga asociado este vehículo
                from app.data.repositories.accidente_repo import AccidenteRepository
                accidente_repo = AccidenteRepository(session)
                accidente = accidente_repo.get_by_id(self.accidente_id)
                
                if accidente and accidente.vehiculo_id != vehiculo.id:
                    print(f"  ⚠️ Asociando vehículo {vehiculo.id} al accidente {self.accidente_id}")
                    accidente.vehiculo_id = vehiculo.id
                    session.flush()
                
                session.commit()
                
                placa = vehiculo.placa or "N/A"
                print(f"✓ Vehículo actualizado: {placa}")
                
                self.view.mostrar_vehiculo_guardado(vehiculo.id, placa)
                
        except Exception as e:
            print(f"❌ Error actualizando vehículo: {e}")
            import traceback
            traceback.print_exc()
    
    def anular_vehiculo(self, vehiculo_id: int):
        """Anula un vehículo (soft delete - cambia estado a 0) y quita asociación del accidente."""
        try:
            with get_db_session() as session:
                vehiculo_repo = VehiculoRepository(session)
                
                if vehiculo_repo.anular(vehiculo_id):
                    # CRÍTICO: Quitar el vehiculo_id del accidente para romper la asociación
                    if self.accidente_id:
                        from app.data.repositories.accidente_repo import AccidenteRepository
                        accidente_repo = AccidenteRepository(session)
                        accidente = accidente_repo.get_by_id(self.accidente_id)
                        
                        if accidente and accidente.vehiculo_id == vehiculo_id:
                            print(f"  📌 ANTES de anular: Accidente.vehiculo_id = {accidente.vehiculo_id}")
                            accidente.vehiculo_id = None
                            session.flush()
                            print(f"  📌 DESPUÉS de anular: Accidente.vehiculo_id = {accidente.vehiculo_id}")
                        else:
                            print(f"  ⚠️ Accidente no tiene este vehículo asociado o no se encontró")
                    
                    session.commit()
                    print(f"✓ Vehículo {vehiculo_id} anulado y desasociado del accidente correctamente")
                    
                    from PySide6.QtWidgets import QMessageBox
                    QMessageBox.information(
                        self.view,
                        "Anulación Exitosa",
                        "El vehículo ha sido anulado correctamente.\n"
                        "La asociación con el accidente se ha eliminado.\n"
                        "Puede registrar un nuevo vehículo para este accidente."
                    )
                    
                    # Limpiar formulario para permitir nuevo registro
                    self.view.limpiar_formulario()
                else:
                    print(f"❌ No se pudo anular el vehículo ID {vehiculo_id}")
        
        except Exception as e:
            print(f"❌ Error anulando vehículo: {e}")
            import traceback
            traceback.print_exc()
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(
                self.view,
                "Error",
                f"Error al anular vehículo: {str(e)}"
            )
    
    def cargar_vehiculo_existente(self):
        """Carga el vehículo existente si hay uno."""
        if not self.accidente_id:
            print("⚠️ VehiculoPresenter: No hay accidente_id para cargar vehículo")
            return
        
        try:
            print(f"🔍 VehiculoPresenter: Buscando vehículo para accidente_id={self.accidente_id}")
            with get_db_session() as session:
                vehiculo_repo = VehiculoRepository(session)
                vehiculo = vehiculo_repo.get_by_accidente(self.accidente_id)
                
                if vehiculo:
                    print(f"✓ VehiculoPresenter: Vehículo encontrado - Placa: {vehiculo.placa}, ID: {vehiculo.id}")
                    self.view.cargar_vehiculo_existente({
                        "id": vehiculo.id,
                        "placa": vehiculo.placa,
                        "marca": vehiculo.marca,
                        "tipo_vehiculo_id": vehiculo.tipo_vehiculo_id,
                        "aseguradora_codigo": vehiculo.aseguradora_codigo,
                        "numero_poliza": vehiculo.numero_poliza,
                        "vigencia_inicio": vehiculo.vigencia_inicio,
                        "vigencia_fin": vehiculo.vigencia_fin,
                        "estado_aseguramiento_id": vehiculo.estado_aseguramiento_id,
                    })
                else:
                    print(f"ℹ️ VehiculoPresenter: No hay vehículo registrado para accidente_id={self.accidente_id}")
                    # Mostrar mensaje informativo en el formulario
                    self.view.lbl_vehiculo_encontrado.setText("ℹ️ No hay vehículo registrado. Puede crear uno nuevo.")
                    self.view.lbl_vehiculo_encontrado.setStyleSheet("color: #0066CC; font-weight: bold; font-size: 9pt;")
                    
        except Exception as e:
            print(f"❌ Error cargando vehículo: {e}")
            import traceback
            traceback.print_exc()
    
    def cargar_vehiculos_por_propietario(self, propietario_id: int):
        """Carga vehículos de un propietario. Si tiene varios, muestra modal de selección."""
        if not propietario_id:
            return
        
        try:
            with get_db_session() as session:
                vehiculo_repo = VehiculoRepository(session)
                vehiculos = vehiculo_repo.get_by_propietario(propietario_id)
                
                if not vehiculos:
                    print(f"ℹ️ El propietario no tiene vehículos registrados")
                    return
                
                if len(vehiculos) == 1:
                    # Solo un vehículo, cargar automáticamente
                    vehiculo = vehiculos[0]
                    self.view.cargar_vehiculo({
                        "id": vehiculo.id,
                        "placa": vehiculo.placa,
                        "marca": vehiculo.marca,
                        "tipo_vehiculo_id": vehiculo.tipo_vehiculo_id,
                        "aseguradora_codigo": vehiculo.aseguradora_codigo,
                        "numero_poliza": vehiculo.numero_poliza,
                        "vigencia_inicio": vehiculo.vigencia_inicio,
                        "vigencia_fin": vehiculo.vigencia_fin,
                        "estado_aseguramiento_id": vehiculo.estado_aseguramiento_id,
                    })
                    print(f"✓ Vehículo {vehiculo.placa} cargado automáticamente")
                else:
                    # Varios vehículos, mostrar modal de selección
                    from app.ui.views.seleccionar_vehiculo_dialog import SeleccionarVehiculoDialog
                    
                    vehiculos_data = []
                    for v in vehiculos:
                        vehiculos_data.append({
                            "id": v.id,
                            "placa": v.placa,
                            "marca": v.marca,
                            "tipo_vehiculo": v.tipo_vehiculo.descripcion if v.tipo_vehiculo else "",
                            "aseguradora_codigo": v.aseguradora_codigo,
                            "numero_poliza": v.numero_poliza,
                            "vigencia_inicio": v.vigencia_inicio,
                            "vigencia_fin": v.vigencia_fin,
                            "tipo_vehiculo_id": v.tipo_vehiculo_id,
                            "estado_aseguramiento_id": v.estado_aseguramiento_id,
                        })
                    
                    dialog = SeleccionarVehiculoDialog(vehiculos_data, self.view)
                    if dialog.exec():
                        vehiculo_seleccionado = dialog.get_vehiculo_seleccionado()
                        if vehiculo_seleccionado:
                            self.view.cargar_vehiculo(vehiculo_seleccionado)
                            print(f"✓ Vehículo {vehiculo_seleccionado['placa']} seleccionado")
        
        except Exception as e:
            print(f"❌ Error cargando vehículos del propietario: {e}")
            import traceback
            traceback.print_exc()
