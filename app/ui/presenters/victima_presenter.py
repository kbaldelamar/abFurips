"""
Presenter para gestión de víctimas.
"""
from typing import Optional, List, Dict, Any
from datetime import date

from app.ui.views.victima_form import VictimaForm
from app.data.repositories.persona_repo import PersonaRepository
from app.data.repositories.victima_repo import VictimaRepository
from app.data.repositories.conductor_repo import ConductorRepository
from app.data.repositories.propietario_repo import PropietarioRepository
from app.data.repositories.catalogo_repo import CatalogoRepository
from app.config.db import get_db_session
from app.data.models import AccidenteVictima, AccidenteConductor, AccidentePropietario


class VictimaPresenter:
    """Presenter para el formulario de víctimas."""
    
    def __init__(self, view: VictimaForm):
        self.view = view
        self.accidente_id: Optional[int] = None
        self.victimas_actuales: List[Dict[str, Any]] = []
        self.conductor_presenter = None  # Se establece desde AccidentePresenter
        self.propietario_presenter = None  # Se establece desde AccidentePresenter
        
        # Conectar señales
        self._conectar_signals()
        
        # Cargar catálogos
        self._cargar_catalogos()
    
    def _conectar_signals(self):
        """Conecta las señales de la vista."""
        self.view.buscar_persona_signal.connect(self.buscar_persona)
        self.view.guardar_victima_signal.connect(self.guardar_victima)
        self.view.actualizar_victima_signal.connect(self.actualizar_victima)
    
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
        self.cargar_victima_existente()
    
    def buscar_persona(self, tipo_id: str, numero: str):
        """Busca una persona por documento."""
        if not tipo_id or not numero:
            return
        
        try:
            with get_db_session() as session:
                persona_repo = PersonaRepository(session)
                persona = persona_repo.get_by_documento(int(tipo_id), numero)
                
                if persona:
                    # Cargar datos en el formulario
                    self.view.cargar_persona({
                        "id": persona.id,
                        "primer_nombre": persona.primer_nombre,
                        "segundo_nombre": persona.segundo_nombre,
                        "primer_apellido": persona.primer_apellido,
                        "segundo_apellido": persona.segundo_apellido,
                        "fecha_nacimiento": persona.fecha_nacimiento,
                        "sexo_id": persona.sexo_id,
                    })
                else:
                    self.view.lbl_persona_encontrada.setText("⚠️ Persona no encontrada. Se creará nueva.")
                    self.view.persona_id_actual = None
        except Exception as e:
            print(f"Error buscando persona: {e}")
            self.view.lbl_persona_encontrada.setText(f"❌ Error: {str(e)}")
    
    def guardar_victima(self, datos: Dict[str, Any]):
        """Guarda una víctima."""
        if not self.accidente_id:
            print("Error: No hay accidente seleccionado")
            return
        
        # Validaciones - TODOS los datos de persona son obligatorios
        if not datos.get("tipo_identificacion_id"):
            print("❌ Error: Debe seleccionar el tipo de identificación")
            return
        
        if not datos.get("numero_identificacion"):
            print("❌ Error: Debe ingresar número de identificación")
            return
        
        if not datos.get("primer_nombre") or not datos.get("primer_apellido"):
            print("❌ Error: Debe ingresar primer nombre y primer apellido")
            return
        
        if not datos.get("fecha_nacimiento"):
            print("❌ Error: Debe ingresar fecha de nacimiento")
            return
        
        if not datos.get("sexo_id"):
            print("❌ Error: Debe seleccionar el sexo")
            return
        
        # Validaciones de víctima - condicion y diagnostico principal obligatorios
        if not datos.get("condicion"):
            print("❌ Error: Debe seleccionar la condición de la víctima")
            return
        
        if not datos.get("diagnostico_principal"):
            print("❌ Error: Debe ingresar el diagnóstico principal")
            return
        
        try:
            with get_db_session() as session:
                persona_repo = PersonaRepository(session)
                victima_repo = VictimaRepository(session)
                
                # Verificar si ya existe una víctima para este accidente
                victimas_existentes = victima_repo.get_by_accidente(self.accidente_id)
                if victimas_existentes and not datos.get("victima_id"):
                    print("❌ Ya existe una víctima registrada para este accidente")
                    return
                
                # 1. Crear/actualizar persona
                datos_persona = {
                    "tipo_identificacion_id": datos["tipo_identificacion_id"],
                    "numero_identificacion": datos["numero_identificacion"],
                    "primer_nombre": datos["primer_nombre"],
                    "segundo_nombre": datos["segundo_nombre"],
                    "primer_apellido": datos["primer_apellido"],
                    "segundo_apellido": datos["segundo_apellido"],
                    "fecha_nacimiento": datos["fecha_nacimiento"],
                    "sexo_id": datos["sexo_id"],
                    "direccion": "N/A",  # Campo obligatorio en BD
                    "telefono": "N/A",  # Campo obligatorio en BD
                    "municipio_residencia_id": None,
                }
                
                persona = persona_repo.obtener_o_crear(
                    datos["tipo_identificacion_id"],
                    datos["numero_identificacion"],
                    datos_persona
                )
                session.flush()
                
                # 2. Crear/actualizar víctima
                if datos.get("victima_id"):
                    # Actualizar existente
                    victima = victima_repo.get_by_id(datos["victima_id"])
                    if victima:
                        victima.persona_id = persona.id
                        victima.condicion_codigo = datos["condicion"]
                        victima.diagnostico_ingreso = datos["diagnostico_principal"]
                        victima.diagnostico_ingreso_sec1 = datos["diagnostico_relacionado_1"]
                        victima.diagnostico_ingreso_sec2 = datos["diagnostico_relacionado_2"]
                        # diagnostico_relacionado_3 no tiene campo en BD
                        victima.servicio_uci = 1 if datos["ingreso_uci"] else 0
                        # Calcular días en UCI si hay fechas
                        if datos["fecha_ingreso_uci"] and datos["fecha_egreso_uci"]:
                            dias = (datos["fecha_egreso_uci"] - datos["fecha_ingreso_uci"]).days
                            victima.dias_uci = dias if dias >= 0 else 0
                        else:
                            victima.dias_uci = None
                        session.flush()
                else:
                    # Crear nueva
                    dias_uci = None
                    if datos["fecha_ingreso_uci"] and datos["fecha_egreso_uci"]:
                        dias = (datos["fecha_egreso_uci"] - datos["fecha_ingreso_uci"]).days
                        dias_uci = dias if dias >= 0 else 0
                    
                    victima = AccidenteVictima(
                        accidente_id=self.accidente_id,
                        persona_id=persona.id,
                        condicion_codigo=datos["condicion"],
                        diagnostico_ingreso=datos["diagnostico_principal"],
                        diagnostico_ingreso_sec1=datos["diagnostico_relacionado_1"],
                        diagnostico_ingreso_sec2=datos["diagnostico_relacionado_2"],
                        servicio_uci=1 if datos["ingreso_uci"] else 0,
                        dias_uci=dias_uci,
                    )
                    victima = victima_repo.create(victima)
                    session.flush()
                
                # 3. Copiar a conductor si está marcado
                if datos.get("es_conductor"):
                    conductor_repo = ConductorRepository(session)
                    conductores_existentes = conductor_repo.get_by_accidente(self.accidente_id)
                    
                    if not conductores_existentes:
                        conductor = AccidenteConductor(
                            accidente_id=self.accidente_id,
                            persona_id=persona.id,
                        )
                        conductor_repo.create(conductor)
                        session.flush()
                        print(f"✓ Conductor también guardado: {persona.primer_nombre} {persona.primer_apellido}")
                    else:
                        print(f"⚠️ Ya existe un conductor registrado para este accidente")
                
                # 4. Copiar a propietario si está marcado
                if datos.get("es_propietario"):
                    propietario_repo = PropietarioRepository(session)
                    propietarios_existentes = propietario_repo.get_by_accidente(self.accidente_id)
                    
                    if not propietarios_existentes:
                        propietario = AccidentePropietario(
                            accidente_id=self.accidente_id,
                            persona_id=persona.id,
                        )
                        propietario_repo.create(propietario)
                        session.flush()
                        print(f"✓ Propietario también guardado: {persona.primer_nombre} {persona.primer_apellido}")
                    else:
                        print(f"⚠️ Ya existe un propietario registrado para este accidente")
                
                session.commit()
                
                nombre_completo = f"{persona.primer_nombre} {persona.primer_apellido}"
                mensaje = f"✓ Víctima guardada: {nombre_completo}"
                if datos.get("es_conductor"):
                    mensaje += " (también como Conductor)"
                if datos.get("es_propietario"):
                    mensaje += " (también como Propietario)"
                print(mensaje)
                
                self.view.mostrar_victima_guardada(victima.id, nombre_completo)
                
                # 5. Recargar los otros tabs si se copiaron los datos
                if datos.get("es_conductor") and self.conductor_presenter:
                    self.conductor_presenter.cargar_conductor_existente()
                if datos.get("es_propietario") and self.propietario_presenter:
                    self.propietario_presenter.cargar_propietario_existente()
                
        except Exception as e:
            print(f"❌ Error guardando víctima: {e}")
            import traceback
            traceback.print_exc()
    
    def actualizar_victima(self, datos: Dict[str, Any]):
        """Actualiza una víctima existente."""
        if not self.accidente_id:
            print("Error: No hay accidente seleccionado")
            return
        
        if not datos.get("victima_id"):
            print("❌ Error: No hay víctima cargada para actualizar")
            return
        
        # Validaciones - TODOS los datos de persona son obligatorios
        if not datos.get("tipo_identificacion_id"):
            print("❌ Error: Debe seleccionar el tipo de identificación")
            return
        
        if not datos.get("numero_identificacion"):
            print("❌ Error: Debe ingresar número de identificación")
            return
        
        if not datos.get("primer_nombre") or not datos.get("primer_apellido"):
            print("❌ Error: Debe ingresar primer nombre y primer apellido")
            return
        
        if not datos.get("fecha_nacimiento"):
            print("❌ Error: Debe ingresar fecha de nacimiento")
            return
        
        if not datos.get("sexo_id"):
            print("❌ Error: Debe seleccionar el sexo")
            return
        
        # Validaciones de víctima - condicion y diagnostico principal obligatorios
        if not datos.get("condicion"):
            print("❌ Error: Debe seleccionar la condición de la víctima")
            return
        
        if not datos.get("diagnostico_principal"):
            print("❌ Error: Debe ingresar el diagnóstico principal")
            return
        
        try:
            with get_db_session() as session:
                persona_repo = PersonaRepository(session)
                victima_repo = VictimaRepository(session)
                
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
                    "direccion": "N/A",  # Campo obligatorio en BD
                    "telefono": "N/A",  # Campo obligatorio en BD
                    "municipio_residencia_id": None,
                }
                
                persona = persona_repo.obtener_o_crear(
                    datos["tipo_identificacion_id"],
                    datos["numero_identificacion"],
                    datos_persona
                )
                session.flush()
                
                # 2. Actualizar víctima
                victima = victima_repo.get_by_id(datos["victima_id"])
                if not victima:
                    print("❌ Error: Víctima no encontrada")
                    return
                
                victima.persona_id = persona.id
                victima.condicion_codigo = datos["condicion"]
                victima.diagnostico_ingreso = datos["diagnostico_principal"]
                victima.diagnostico_ingreso_sec1 = datos["diagnostico_relacionado_1"]
                victima.diagnostico_ingreso_sec2 = datos["diagnostico_relacionado_2"]
                victima.servicio_uci = 1 if datos["ingreso_uci"] else 0
                
                # Calcular días en UCI si hay fechas
                if datos["fecha_ingreso_uci"] and datos["fecha_egreso_uci"]:
                    dias = (datos["fecha_egreso_uci"] - datos["fecha_ingreso_uci"]).days
                    victima.dias_uci = dias if dias >= 0 else 0
                else:
                    victima.dias_uci = None
                
                session.flush()
                session.commit()
                
                nombre_completo = f"{persona.primer_nombre} {persona.primer_apellido}"
                print(f"✓ Víctima actualizada: {nombre_completo}")
                
                self.view.mostrar_victima_guardada(victima.id, nombre_completo)
                
        except Exception as e:
            print(f"❌ Error actualizando víctima: {e}")
            import traceback
            traceback.print_exc()
    
    def cargar_victima_existente(self):
        """Carga la víctima existente si hay una."""
        if not self.accidente_id:
            return
        
        try:
            with get_db_session() as session:
                victima_repo = VictimaRepository(session)
                victimas = victima_repo.get_by_accidente(self.accidente_id)
                
                if victimas:
                    victima = victimas[0]  # Solo debe haber una
                    persona = victima.persona
                    
                    self.view.cargar_victima_existente({
                        "id": victima.id,
                        "condicion": victima.condicion_codigo,
                        "diagnostico_principal": victima.diagnostico_ingreso,
                        "diagnostico_relacionado_1": victima.diagnostico_ingreso_sec1,
                        "diagnostico_relacionado_2": victima.diagnostico_ingreso_sec2,
                        "diagnostico_relacionado_3": None,  # No existe en BD
                        "ingreso_uci": victima.servicio_uci == 1 if victima.servicio_uci is not None else False,
                        "fecha_ingreso_uci": None,  # No se almacena en BD, solo dias_uci
                        "fecha_egreso_uci": None,  # No se almacena en BD, solo dias_uci
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
                        }
                    })
                    
        except Exception as e:
            print(f"❌ Error cargando víctima: {e}")
