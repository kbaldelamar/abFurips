"""
Presenter para remisiones (patrón MVP).
"""
from typing import Any, Dict, List
from PySide6.QtCore import QObject

from app.ui.views.remision_form import RemisionForm
from app.config import get_db_session
from app.data.repositories.remision_repo import RemisionRepository
from app.data.repositories.persona_config_repo import PersonaConfigRepository
from app.data.models.accidente_procesos import AccidenteRemision


class RemisionPresenter(QObject):
    """Presenter para remisiones."""
    
    def __init__(self, view: RemisionForm):
        super().__init__()
        self.view = view
        self.accidente_id = None
        
        # Conectar señales
        self._connect_signals()
        
        # Cargar profesionales
        self._cargar_profesionales()
    
    def _connect_signals(self):
        """Conecta las señales de la vista."""
        self.view.guardar_remision_signal.connect(self.guardar_remision)
        self.view.actualizar_remision_signal.connect(self.actualizar_remision)
        self.view.eliminar_remision_signal.connect(self.eliminar_remision)
    
    def _cargar_profesionales(self):
        """Carga solo médicos (es_medico=1) para profesional_remite."""
        try:
            with get_db_session() as session:
                config_repo = PersonaConfigRepository(session)
                medicos = config_repo.get_medicos_activos()
                
                profesionales = []
                for config in medicos:
                    profesionales.append({
                        "persona_id": config.persona.id,
                        "nombre_completo": config.persona.nombre_completo,
                        "especialidad": config.especialidad or ""
                    })
                
                self.view.cargar_profesionales(profesionales)
                print(f"✓ {len(profesionales)} médicos cargados")
        except Exception as e:
            print(f"❌ Error cargando médicos: {e}")
    
    def set_accidente_id(self, accidente_id: int):
        """Establece el accidente actual y carga remisiones."""
        self.accidente_id = accidente_id
        self._cargar_remisiones()
    
    def _cargar_remisiones(self):
        """Carga las remisiones existentes."""
        if not self.accidente_id:
            return
        
        try:
            with get_db_session() as session:
                remision_repo = RemisionRepository(session)
                remisiones = remision_repo.get_by_accidente(self.accidente_id)
                
                self.view.limpiar_tabla()
                
                for remision in remisiones:
                    datos = {
                        "id": remision.id,
                        "tipo_referencia": remision.tipo_referencia,
                        "fecha_remision": remision.fecha_remision,
                        "hora_salida": remision.hora_salida,
                        "codigo_hab_remitente": remision.codigo_hab_remitente,
                        "codigo_hab_recibe": remision.codigo_hab_recibe,
                        "cargo_remite": remision.cargo_remite,
                        "fecha_aceptacion": remision.fecha_aceptacion,
                        "hora_aceptacion": remision.hora_aceptacion,
                        "placa_ambulancia": remision.placa_ambulancia,
                        "persona_remite_id": remision.persona_remite_id,
                        "persona_recibe_id": remision.persona_recibe_id,
                    }
                    
                    # profesional_remite viene de persona (relación)
                    if remision.persona_remite:
                        datos["profesional_remite"] = remision.persona_remite.nombre_completo
                    else:
                        datos["profesional_remite"] = remision.profesional_remite or "N/A"
                    
                    # profesional_recibe es texto libre
                    datos["profesional_recibe"] = remision.profesional_recibe or "N/A"
                    
                    self.view.agregar_remision_tabla(datos)
                
                print(f"✓ {len(remisiones)} remisiones cargadas")
                
        except Exception as e:
            print(f"❌ Error cargando remisiones: {e}")
            import traceback
            traceback.print_exc()
    
    def guardar_remision(self, datos: Dict[str, Any]):
        """Guarda una nueva remisión."""
        if not self.accidente_id:
            print("❌ No hay accidente seleccionado")
            return
        
        if not datos.get("tipo_referencia"):
            print("❌ Debe seleccionar el tipo de referencia")
            return
        
        try:
            with get_db_session() as session:
                remision_repo = RemisionRepository(session)
                
                remision = AccidenteRemision(
                    accidente_id=self.accidente_id,
                    tipo_referencia=datos["tipo_referencia"],
                    fecha_remision=datos["fecha_remision"],
                    hora_salida=datos["hora_salida"],
                    codigo_hab_remitente=datos["codigo_hab_remitente"],
                    codigo_hab_recibe=datos["codigo_hab_recibe"],
                    profesional_remite=datos["profesional_remite"],
                    profesional_recibe=datos["profesional_recibe"],
                    cargo_remite=datos["cargo_remite"],
                    fecha_aceptacion=datos["fecha_aceptacion"],
                    hora_aceptacion=datos["hora_aceptacion"],
                    placa_ambulancia=datos["placa_ambulancia"],
                    persona_remite_id=datos.get("persona_remite_id"),
                    persona_recibe_id=datos.get("persona_recibe_id"),
                )
                
                remision = remision_repo.create(remision)
                session.commit()
                
                print(f"✅ Remisión guardada")
                
                # Recargar tabla
                self._cargar_remisiones()
                self.view.limpiar_formulario()
                
        except Exception as e:
            print(f"❌ Error guardando remisión: {e}")
            import traceback
            traceback.print_exc()
    
    def actualizar_remision(self, datos: Dict[str, Any]):
        """Actualiza una remisión existente."""
        if not datos.get("remision_id"):
            print("❌ No hay remisión para actualizar")
            return
        
        try:
            with get_db_session() as session:
                remision_repo = RemisionRepository(session)
                remision = remision_repo.get_by_id(datos["remision_id"])
                
                if not remision:
                    print("❌ Remisión no encontrada")
                    return
                
                remision.tipo_referencia = datos["tipo_referencia"]
                remision.fecha_remision = datos["fecha_remision"]
                remision.hora_salida = datos["hora_salida"]
                remision.codigo_hab_remitente = datos["codigo_hab_remitente"]
                remision.codigo_hab_recibe = datos["codigo_hab_recibe"]
                remision.profesional_remite = datos["profesional_remite"]
                remision.profesional_recibe = datos["profesional_recibe"]
                remision.cargo_remite = datos["cargo_remite"]
                remision.fecha_aceptacion = datos["fecha_aceptacion"]
                remision.hora_aceptacion = datos["hora_aceptacion"]
                remision.placa_ambulancia = datos["placa_ambulancia"]
                remision.persona_remite_id = datos.get("persona_remite_id")
                remision.persona_recibe_id = datos.get("persona_recibe_id")
                
                session.commit()
                
                print(f"✅ Remisión actualizada")
                self._cargar_remisiones()
                
        except Exception as e:
            print(f"❌ Error actualizando remisión: {e}")
            import traceback
            traceback.print_exc()
    
    def eliminar_remision(self, remision_id: int):
        """Elimina una remisión."""
        try:
            with get_db_session() as session:
                remision_repo = RemisionRepository(session)
                if remision_repo.anular(remision_id):
                    session.commit()
                    print(f"✅ Remisión eliminada")
                    self._cargar_remisiones()
        except Exception as e:
            print(f"❌ Error eliminando remisión: {e}")
    
    def limpiar(self):
        """Limpia el formulario."""
        self.view.limpiar_formulario()
        self.view.limpiar_tabla()
