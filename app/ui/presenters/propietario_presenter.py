"""
Presenter para gestión del propietario.
"""
from typing import Optional, Dict, Any

from app.ui.views.propietario_form import PropietarioForm
from app.data.repositories.persona_repo import PersonaRepository
from app.data.repositories.propietario_repo import PropietarioRepository
from app.data.repositories.catalogo_repo import CatalogoRepository
from app.config.db import get_db_session
from app.data.models import AccidentePropietario


class PropietarioPresenter:
    """Presenter para el formulario de propietario."""
    
    def __init__(self, view: PropietarioForm):
        self.view = view
        self.accidente_id: Optional[int] = None
        self.vehiculos_cargados_callback = None  # Callback para notificar cuando se carga un propietario
        self.propietario_guardado_callback = None  # Callback para notificar cuando se guarda un propietario
        
        # Conectar señales
        self._conectar_signals()
        
        # Cargar catálogos
        self._cargar_catalogos()
    
    def set_vehiculos_cargados_callback(self, callback):
        """Establece el callback para cargar vehículos cuando se selecciona propietario."""
        self.vehiculos_cargados_callback = callback
    
    def set_propietario_guardado_callback(self, callback):
        """Establece el callback para notificar cuando se guarda un propietario."""
        self.propietario_guardado_callback = callback
    
    def _conectar_signals(self):
        """Conecta las señales de la vista."""
        self.view.buscar_persona_signal.connect(self.buscar_persona)
        self.view.guardar_propietario_signal.connect(self.guardar_propietario)
        self.view.actualizar_propietario_signal.connect(self.actualizar_propietario)
        self.view.anular_propietario_signal.connect(self.anular_propietario)
    
    def _cargar_catalogos(self):
        """Carga los catálogos necesarios."""
        try:
            with get_db_session() as session:
                catalogo_repo = CatalogoRepository(session)
                
                # Tipos de identificación
                tipos = catalogo_repo.get_tipos_identificacion()
                self.view.cargar_tipos_identificacion(
                    [{"id": t.id, "descripcion": t.descripcion} for t in tipos]
                )
                
                # Sexos
                sexos = catalogo_repo.get_sexos()
                self.view.cargar_sexos(
                    [{"id": s.id, "descripcion": s.descripcion} for s in sexos]
                )
                
                # Municipios
                municipios = catalogo_repo.get_todos_municipios()
                self.view.cargar_municipios(
                    [{"id": m.id, "nombre": m.nombre} for m in municipios]
                )
        except Exception as e:
            print(f"Error cargando catálogos: {e}")
    
    def set_accidente_id(self, accidente_id: int):
        """Establece el ID del accidente actual."""
        self.accidente_id = accidente_id
        self.cargar_propietario_existente()
    
    def buscar_persona(self, tipo_id: str, numero: str):
        """Busca una persona por documento con validación de uso previo."""
        if not tipo_id or not numero:
            return
        
        try:
            with get_db_session() as session:
                persona_repo = PersonaRepository(session)
                persona = persona_repo.get_by_documento(int(tipo_id), numero)
                
                if persona:
                    # SEGURIDAD: Verificar si esta persona ya es propietario en otro accidente activo
                    from app.data.repositories.propietario_repo import PropietarioRepository
                    from sqlalchemy import and_
                    from app.data.models.accidente import AccidentePropietario
                    
                    propietario_repo = PropietarioRepository(session)
                    otros_propietarios = session.query(AccidentePropietario).filter(
                        and_(
                            AccidentePropietario.persona_id == persona.id,
                            AccidentePropietario.accidente_id != self.accidente_id,
                            AccidentePropietario.estado == 1
                        )
                    ).first()
                    
                    if otros_propietarios:
                        from PySide6.QtWidgets import QMessageBox
                        nombre = f"{persona.primer_nombre} {persona.primer_apellido}"
                        respuesta = QMessageBox.information(
                            self.view,
                            "ℹ️ Persona ya registrada",
                            f"<b>La persona {nombre}</b><br>"
                            f"Documento: {numero}<br><br>"
                            f"Ya está registrada como <b>propietario en otro accidente</b><br>"
                            f"(Accidente ID: {otros_propietarios.accidente_id})<br><br>"
                            f"Se cargará la información para este accidente.",
                            QMessageBox.Ok
                        )
                    
                    self.view.cargar_persona({
                        "id": persona.id,
                        "primer_nombre": persona.primer_nombre,
                        "segundo_nombre": persona.segundo_nombre,
                        "primer_apellido": persona.primer_apellido,
                        "segundo_apellido": persona.segundo_apellido,
                        "fecha_nacimiento": persona.fecha_nacimiento,
                        "sexo_id": persona.sexo_id,
                        "direccion": persona.direccion,
                        "telefono": persona.telefono,
                        "municipio_residencia_id": persona.municipio_residencia_id,
                    })
                    
                    self.view.lbl_persona_encontrada.setText(f"✓ Persona encontrada en BD (ID: {persona.id})")
                    self.view.lbl_persona_encontrada.setStyleSheet("color: green; font-weight: bold;")
                    
                    # Notificar para cargar vehículos en tab Vehículo
                    if self.vehiculos_cargados_callback:
                        self.vehiculos_cargados_callback(persona.id)
                else:
                    self.view.lbl_persona_encontrada.setText("⚠️ Persona no encontrada. Se creará nueva.")
                    self.view.persona_id_actual = None
        except Exception as e:
            print(f"Error buscando persona: {e}")
            import traceback
            traceback.print_exc()
            self.view.lbl_persona_encontrada.setText(f"❌ Error: {str(e)}")
    
    def guardar_propietario(self, datos: Dict[str, Any]):
        """Guarda el propietario."""
        if not self.accidente_id:
            print("Error: No hay accidente seleccionado")
            return
        # Validaciones
        if not datos.get("numero_identificacion"):
            print("Error: Debe ingresar número de identificación")
            return

        if not datos.get("primer_nombre") or not datos.get("primer_apellido"):
            print("Error: Debe ingresar nombre y apellido")
            return

        try:
            with get_db_session() as session:
                persona_repo = PersonaRepository(session)
                propietario_repo = PropietarioRepository(session)

                # Verificar si ya existe un propietario para este accidente
                propietarios_existentes = propietario_repo.get_by_accidente(self.accidente_id)
                if propietarios_existentes and not datos.get("propietario_id"):
                    print("❌ Ya existe un propietario registrado para este accidente")
                    return

                # 1. Crear/actualizar persona
                datos_persona = {
                    "tipo_identificacion_id": datos.get("tipo_identificacion_id"),
                    "numero_identificacion": datos["numero_identificacion"],
                    "primer_nombre": datos["primer_nombre"],
                    "segundo_nombre": datos.get("segundo_nombre"),
                    "primer_apellido": datos["primer_apellido"],
                    "segundo_apellido": datos.get("segundo_apellido"),
                    "fecha_nacimiento": datos.get("fecha_nacimiento"),
                    "sexo_id": datos.get("sexo_id"),
                    "direccion": datos.get("direccion") or "N/A",
                    "telefono": datos.get("telefono") or "N/A",
                    "municipio_residencia_id": datos.get("municipio_residencia_id") or 1,
                }

                persona = persona_repo.obtener_o_crear(
                    datos_persona.get("tipo_identificacion_id"),
                    datos_persona.get("numero_identificacion"),
                    datos_persona
                )
                session.flush()

                # 2. Crear/actualizar propietario
                if datos.get("propietario_id"):
                    # Actualizar existente
                    propietario = propietario_repo.get_by_id(datos["propietario_id"])
                    if propietario:
                        propietario.persona_id = persona.id
                        session.flush()
                else:
                    # Crear nuevo
                    propietario = AccidentePropietario(
                        accidente_id=self.accidente_id,
                        persona_id=persona.id,
                    )
                    propietario = propietario_repo.create(propietario)
                    session.flush()

                session.commit()

                nombre_completo = f"{persona.primer_nombre} {persona.primer_apellido}"
                print(f"✓ Propietario guardado: {nombre_completo}")

                self.view.mostrar_propietario_guardado(propietario.id, nombre_completo)

                # Notificar al vehículo que el propietario fue guardado
                if self.propietario_guardado_callback:
                    self.propietario_guardado_callback()

        except Exception as e:
            print(f"❌ Error guardando propietario: {e}")
            import traceback
            traceback.print_exc()
    def actualizar_propietario(self, datos: Dict[str, Any]):
        """Actualiza un propietario existente."""
        if not self.accidente_id:
            print("Error: No hay accidente seleccionado")
            return
        
        if not datos.get("propietario_id"):
            print("❌ Error: No hay propietario cargado para actualizar")
            return
        
        # Validaciones
        if not datos.get("numero_identificacion"):
            print("❌ Error: Debe ingresar número de identificación")
            return
        
        if not datos.get("primer_nombre") or not datos.get("primer_apellido"):
            print("❌ Error: Debe ingresar nombre y apellido")
            return
        
        try:
            with get_db_session() as session:
                persona_repo = PersonaRepository(session)
                propietario_repo = PropietarioRepository(session)
                
                # 1. Actualizar persona
                datos_persona = {
                    "tipo_identificacion_id": datos["tipo_identificacion_id"],
                    "numero_identificacion": datos["numero_identificacion"],
                    "primer_nombre": datos["primer_nombre"],
                    "segundo_nombre": datos["segundo_nombre"],
                    "primer_apellido": datos["primer_apellido"],
                    "segundo_apellido": datos["segundo_apellido"],
                    "fecha_nacimiento": datos["fecha_nacimiento"],
                    "sexo_id": datos["sexo_id"],
                    "direccion": datos.get("direccion") or "N/A",
                    "telefono": datos.get("telefono") or "N/A",
                    "municipio_residencia_id": datos.get("municipio_residencia_id") or 1,
                }
                
                persona = persona_repo.obtener_o_crear(
                    datos["tipo_identificacion_id"],
                    datos["numero_identificacion"],
                    datos_persona
                )
                session.flush()
                
                # 2. Actualizar propietario
                propietario = propietario_repo.get_by_id(datos["propietario_id"])
                if not propietario:
                    print("❌ Error: Propietario no encontrado")
                    return
                
                propietario.persona_id = persona.id
                session.flush()
                session.commit()
                
                nombre_completo = f"{persona.primer_nombre} {persona.primer_apellido}"
                print(f"✓ Propietario actualizado: {nombre_completo}")
                
                self.view.mostrar_propietario_guardado(propietario.id, nombre_completo)
                
                # Notificar al vehículo que el propietario fue guardado
                if self.propietario_guardado_callback:
                    self.propietario_guardado_callback()
                
        except Exception as e:
            print(f"❌ Error actualizando propietario: {e}")
            import traceback
            traceback.print_exc()
    
    def anular_propietario(self, propietario_id: int):
        """Anula un propietario (soft delete - cambia estado a 0)."""
        try:
            with get_db_session() as session:
                propietario_repo = PropietarioRepository(session)
                
                if propietario_repo.anular(propietario_id):
                    session.commit()
                    print(f"✓ Propietario {propietario_id} anulado correctamente")
                    
                    from PySide6.QtWidgets import QMessageBox
                    QMessageBox.information(
                        self.view,
                        "Anulación Exitosa",
                        "El propietario ha sido anulado correctamente.\n"
                        "Puede registrar un nuevo propietario para este accidente."
                    )
                    
                    # Limpiar formulario para permitir nuevo registro
                    self.view.limpiar_formulario()
                else:
                    print(f"❌ No se pudo anular el propietario ID {propietario_id}")
        
        except Exception as e:
            print(f"❌ Error anulando propietario: {e}")
            import traceback
            traceback.print_exc()
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(
                self.view,
                "Error",
                f"Error al anular propietario: {str(e)}"
            )
    
    def cargar_propietario_existente(self):
        """Carga el propietario existente si hay uno."""
        if not self.accidente_id:
            return
        
        try:
            with get_db_session() as session:
                propietario_repo = PropietarioRepository(session)
                propietarios = propietario_repo.get_by_accidente(self.accidente_id)

                if propietarios:
                    propietario = propietarios[0]  # Solo debe haber uno
                    persona = propietario.persona

                    self.view.cargar_propietario_existente({
                        "id": propietario.id,
                        "persona": {
                            "id": persona.id,
                            "tipo_identificacion_id": persona.tipo_identificacion_id,
                            "numero_identificacion": persona.numero_identificacion,
                            "primer_nombre": persona.primer_nombre,
                            "segundo_nombre": persona.segundo_nombre,
                            "primer_apellido": persona.primer_apellido,
                            "segundo_apellido": persona.segundo_apellido,
                            "fecha_nacimiento": persona.fecha_nacimiento,
                            "sexo_id": persona.sexo_id,
                            "direccion": persona.direccion,
                            "telefono": persona.telefono,
                            "municipio_residencia_id": persona.municipio_residencia_id,
                        }
                    })
                # Si no hay propietarios activos, no cargar ninguno (no mostrar anulados)
                    
        except Exception as e:
            print(f"❌ Error cargando propietario: {e}")
    
    def cargar_propietario_existente_desde_persona(self, persona):
        """Carga un propietario desde un objeto Persona (llamado desde vehículo)."""
        try:
            self.view.cargar_persona({
                "id": persona.id,
                "primer_nombre": persona.primer_nombre,
                "segundo_nombre": persona.segundo_nombre,
                "primer_apellido": persona.primer_apellido,
                "segundo_apellido": persona.segundo_apellido,
                "fecha_nacimiento": persona.fecha_nacimiento,
                "sexo_id": persona.sexo_id,
                "direccion": persona.direccion,
                "telefono": persona.telefono,
                "municipio_residencia_id": persona.municipio_residencia_id,
            })
            
            # También cargar en los campos de documento
            self.view.combo_tipo_id.setCurrentIndex(
                self.view.combo_tipo_id.findData(persona.tipo_identificacion_id)
            )
            self.view.txt_numero_id.setText(persona.numero_identificacion)
            
        except Exception as e:
            print(f"❌ Error cargando propietario desde persona: {e}")
