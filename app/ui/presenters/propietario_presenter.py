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
        
        # Conectar señales
        self._conectar_signals()
        
        # Cargar catálogos
        self._cargar_catalogos()
    
    def _conectar_signals(self):
        """Conecta las señales de la vista."""
        self.view.buscar_persona_signal.connect(self.buscar_persona)
        self.view.guardar_propietario_signal.connect(self.guardar_propietario)
        self.view.actualizar_propietario_signal.connect(self.actualizar_propietario)
    
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
        except Exception as e:
            print(f"Error cargando catálogos: {e}")
    
    def set_accidente_id(self, accidente_id: int):
        """Establece el ID del accidente actual."""
        self.accidente_id = accidente_id
        self.cargar_propietario_existente()
    
    def buscar_persona(self, tipo_id: str, numero: str):
        """Busca una persona por documento."""
        if not tipo_id or not numero:
            return
        
        try:
            with get_db_session() as session:
                persona_repo = PersonaRepository(session)
                persona = persona_repo.get_by_documento(int(tipo_id), numero)
                
                if persona:
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
                
        except Exception as e:
            print(f"❌ Error actualizando propietario: {e}")
            import traceback
            traceback.print_exc()
    
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
                        }
                    })
                    
        except Exception as e:
            print(f"❌ Error cargando propietario: {e}")
