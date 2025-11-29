"""
Presenter para gestión del conductor.
"""
from typing import Optional, Dict, Any

from app.ui.views.conductor_form import ConductorForm
from app.data.repositories.persona_repo import PersonaRepository
from app.data.repositories.conductor_repo import ConductorRepository
from app.data.repositories.catalogo_repo import CatalogoRepository
from app.config.db import get_db_session
from app.data.models import AccidenteConductor


class ConductorPresenter:
    """Presenter para el formulario de conductor."""
    
    def __init__(self, view: ConductorForm):
        self.view = view
        self.accidente_id: Optional[int] = None
        
        # Conectar señales
        self._conectar_signals()
        
        # Cargar catálogos
        self._cargar_catalogos()
    
    def _conectar_signals(self):
        """Conecta las señales de la vista."""
        self.view.buscar_persona_signal.connect(self.buscar_persona)
        self.view.guardar_conductor_signal.connect(self.guardar_conductor)
        self.view.actualizar_conductor_signal.connect(self.actualizar_conductor)
        self.view.anular_conductor_signal.connect(self.anular_conductor)
    
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
        self.cargar_conductor_existente()
    
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
                        "direccion": persona.direccion,
                        "telefono": persona.telefono,
                        "municipio_residencia_id": persona.municipio_residencia_id,
                    })
                else:
                    self.view.lbl_persona_encontrada.setText("⚠️ Persona no encontrada. Se creará nueva.")
                    self.view.persona_id_actual = None
        except Exception as e:
            print(f"Error buscando persona: {e}")
            self.view.lbl_persona_encontrada.setText(f"❌ Error: {str(e)}")
    
    def guardar_conductor(self, datos: Dict[str, Any]):
        """Guarda el conductor."""
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
                conductor_repo = ConductorRepository(session)
                
                # Verificar si ya existe un conductor para este accidente
                conductores_existentes = conductor_repo.get_by_accidente(self.accidente_id)
                if conductores_existentes and not datos.get("conductor_id"):
                    print("❌ Ya existe un conductor registrado para este accidente")
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
                
                # 2. Crear/actualizar conductor
                if datos.get("conductor_id"):
                    # Actualizar existente
                    conductor = conductor_repo.get_by_id(datos["conductor_id"])
                    if conductor:
                        conductor.persona_id = persona.id
                        session.flush()
                else:
                    # Crear nuevo
                    conductor = AccidenteConductor(
                        accidente_id=self.accidente_id,
                        persona_id=persona.id,
                    )
                    conductor = conductor_repo.create(conductor)
                    session.flush()
                
                session.commit()
                
                nombre_completo = f"{persona.primer_nombre} {persona.primer_apellido}"
                print(f"✓ Conductor guardado: {nombre_completo}")
                
                self.view.mostrar_conductor_guardado(conductor.id, nombre_completo)
                
        except Exception as e:
            print(f"❌ Error guardando conductor: {e}")
            import traceback
            traceback.print_exc()
    
    def actualizar_conductor(self, datos: Dict[str, Any]):
        """Actualiza un conductor existente."""
        if not self.accidente_id:
            print("Error: No hay accidente seleccionado")
            return
        
        if not datos.get("conductor_id"):
            print("❌ Error: No hay conductor cargado para actualizar")
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
                conductor_repo = ConductorRepository(session)
                
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
                
                # 2. Actualizar conductor
                conductor = conductor_repo.get_by_id(datos["conductor_id"])
                if not conductor:
                    print("❌ Error: Conductor no encontrado")
                    return
                
                conductor.persona_id = persona.id
                session.flush()
                session.commit()
                
                nombre_completo = f"{persona.primer_nombre} {persona.primer_apellido}"
                print(f"✓ Conductor actualizado: {nombre_completo}")
                
                self.view.mostrar_conductor_guardado(conductor.id, nombre_completo)
                
        except Exception as e:
            print(f"❌ Error actualizando conductor: {e}")
            import traceback
            traceback.print_exc()
    
    def anular_conductor(self, conductor_id: int):
        """Anula un conductor (soft delete - cambia estado a 0)."""
        try:
            with get_db_session() as session:
                conductor_repo = ConductorRepository(session)
                
                if conductor_repo.anular(conductor_id):
                    session.commit()
                    print(f"✓ Conductor {conductor_id} anulado correctamente")
                    
                    from PySide6.QtWidgets import QMessageBox
                    QMessageBox.information(
                        self.view,
                        "Anulación Exitosa",
                        "El conductor ha sido anulado correctamente.\n"
                        "Puede registrar un nuevo conductor para este accidente."
                    )
                    
                    # Limpiar formulario para permitir nuevo registro
                    self.view.limpiar_formulario()
                else:
                    print(f"❌ No se pudo anular el conductor ID {conductor_id}")
        
        except Exception as e:
            print(f"❌ Error anulando conductor: {e}")
            import traceback
            traceback.print_exc()
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(
                self.view,
                "Error",
                f"Error al anular conductor: {str(e)}"
            )
    
    def cargar_conductor_existente(self):
        """Carga el conductor existente si hay uno."""
        if not self.accidente_id:
            return
        
        try:
            with get_db_session() as session:
                conductor_repo = ConductorRepository(session)
                conductores = conductor_repo.get_by_accidente(self.accidente_id)
                
                if conductores:
                    conductor = conductores[0]  # Solo debe haber uno
                    persona = conductor.persona
                    
                    self.view.cargar_conductor_existente({
                        "id": conductor.id,
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
                    
        except Exception as e:
            print(f"❌ Error cargando conductor: {e}")
