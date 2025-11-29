"""
Presenter para médico tratante (patrón MVP).
"""
from typing import Any, Dict
from PySide6.QtCore import QObject

from app.ui.views.medico_tratante_form import MedicoTratanteForm
from app.config import get_db_session
from app.data.repositories.medico_tratante_repo import MedicoTratanteRepository
from app.data.repositories.persona_config_repo import PersonaConfigRepository
from app.data.repositories.victima_repo import VictimaRepository
from app.data.models.accidente_procesos import AccidenteMedicoTratante


class MedicoTratantePresenter(QObject):
    """Presenter para médico tratante."""
    
    def __init__(self, view: MedicoTratanteForm):
        super().__init__()
        self.view = view
        self.accidente_id = None
        self.victima_id = None
        
        # Conectar señales
        self._connect_signals()
        
        # Cargar médicos
        self._cargar_medicos()
    
    def _connect_signals(self):
        """Conecta las señales de la vista."""
        self.view.guardar_medico_signal.connect(self.guardar_medico)
        self.view.actualizar_medico_signal.connect(self.actualizar_medico)
        self.view.anular_medico_signal.connect(self.anular_medico)
    
    def _cargar_medicos(self):
        """Carga los médicos disponibles."""
        try:
            with get_db_session() as session:
                config_repo = PersonaConfigRepository(session)
                configs = config_repo.get_medicos_activos()
                
                medicos = []
                for config in configs:
                    if config.persona:
                        medicos.append({
                            "persona_id": config.persona_id,
                            "nombre_completo": config.persona.nombre_completo,
                            "registro_medico": config.registro_medico or "N/A",
                            "especialidad": config.especialidad or "N/A"
                        })
                
                self.view.cargar_medicos(medicos)
                print(f"✓ {len(medicos)} médicos cargados")
        except Exception as e:
            print(f"❌ Error cargando médicos: {e}")
    
    def set_accidente_victima(self, accidente_id: int, victima_id: int, victima_nombre: str):
        """Establece el accidente y víctima actual."""
        self.accidente_id = accidente_id
        self.victima_id = victima_id
        self.view.set_victima_info(victima_nombre)
        self._cargar_medico_existente()
    
    def _cargar_medico_existente(self):
        """Carga el médico tratante existente si hay uno."""
        if not self.victima_id:
            return
        
        try:
            with get_db_session() as session:
                medico_repo = MedicoTratanteRepository(session)
                medico = medico_repo.get_by_victima(self.victima_id)
                
                if medico:
                    self.view.cargar_medico_existente({
                        "id": medico.id,
                        "persona_id": medico.persona_id,
                        "fecha_ingreso": medico.fecha_ingreso,
                        "hora_ingreso": medico.hora_ingreso,
                        "fecha_egreso": medico.fecha_egreso,
                        "hora_egreso": medico.hora_egreso,
                        "diagnostico_ingreso": medico.diagnostico_ingreso,
                        "diagnostico_ingreso_sec1": medico.diagnostico_ingreso_sec1,
                        "diagnostico_ingreso_sec2": medico.diagnostico_ingreso_sec2,
                        "diagnostico_egreso": medico.diagnostico_egreso,
                        "diagnostico_egreso_sec1": medico.diagnostico_egreso_sec1,
                        "diagnostico_egreso_sec2": medico.diagnostico_egreso_sec2,
                        "servicio_uci": medico.servicio_uci,
                        "dias_uci": medico.dias_uci,
                    })
        except Exception as e:
            print(f"❌ Error cargando médico existente: {e}")
    
    def guardar_medico(self, datos: Dict[str, Any]):
        """Guarda un nuevo médico tratante."""
        if not self.accidente_id or not self.victima_id:
            print("❌ No hay accidente o víctima seleccionada")
            return
        
        if not datos.get("persona_id"):
            print("❌ Debe seleccionar un médico")
            return
        
        try:
            with get_db_session() as session:
                medico_repo = MedicoTratanteRepository(session)
                
                # Verificar si ya existe
                existente = medico_repo.get_by_victima(self.victima_id)
                if existente:
                    print("❌ Ya existe un médico tratante para esta víctima")
                    return
                
                medico = AccidenteMedicoTratante(
                    accidente_id=self.accidente_id,
                    accidente_victima_id=self.victima_id,
                    persona_id=datos["persona_id"],
                    fecha_ingreso=datos["fecha_ingreso"],
                    hora_ingreso=datos["hora_ingreso"],
                    fecha_egreso=datos["fecha_egreso"],
                    hora_egreso=datos["hora_egreso"],
                    diagnostico_ingreso=datos["diagnostico_ingreso"],
                    diagnostico_ingreso_sec1=datos["diagnostico_ingreso_sec1"],
                    diagnostico_ingreso_sec2=datos["diagnostico_ingreso_sec2"],
                    diagnostico_egreso=datos["diagnostico_egreso"],
                    diagnostico_egreso_sec1=datos["diagnostico_egreso_sec1"],
                    diagnostico_egreso_sec2=datos["diagnostico_egreso_sec2"],
                    servicio_uci=datos["servicio_uci"],
                    dias_uci=datos["dias_uci"],
                )
                
                medico = medico_repo.create(medico)
                session.commit()
                
                print(f"✅ Médico tratante guardado")
                self.view.mostrar_guardado("Médico tratante registrado correctamente")
                self._cargar_medico_existente()
                
        except Exception as e:
            print(f"❌ Error guardando médico: {e}")
            import traceback
            traceback.print_exc()
    
    def actualizar_medico(self, datos: Dict[str, Any]):
        """Actualiza el médico tratante existente."""
        if not datos.get("medico_id"):
            print("❌ No hay médico para actualizar")
            return
        
        try:
            with get_db_session() as session:
                medico_repo = MedicoTratanteRepository(session)
                medico = medico_repo.get_by_id(datos["medico_id"])
                
                if not medico:
                    print("❌ Médico no encontrado")
                    return
                
                medico.fecha_ingreso = datos["fecha_ingreso"]
                medico.hora_ingreso = datos["hora_ingreso"]
                medico.fecha_egreso = datos["fecha_egreso"]
                medico.hora_egreso = datos["hora_egreso"]
                medico.diagnostico_ingreso = datos["diagnostico_ingreso"]
                medico.diagnostico_ingreso_sec1 = datos["diagnostico_ingreso_sec1"]
                medico.diagnostico_ingreso_sec2 = datos["diagnostico_ingreso_sec2"]
                medico.diagnostico_egreso = datos["diagnostico_egreso"]
                medico.diagnostico_egreso_sec1 = datos["diagnostico_egreso_sec1"]
                medico.diagnostico_egreso_sec2 = datos["diagnostico_egreso_sec2"]
                medico.servicio_uci = datos["servicio_uci"]
                medico.dias_uci = datos["dias_uci"]
                
                session.commit()
                
                print(f"✅ Médico tratante actualizado")
                self.view.mostrar_guardado("Médico tratante actualizado correctamente")
                
        except Exception as e:
            print(f"❌ Error actualizando médico: {e}")
            import traceback
            traceback.print_exc()
    
    def anular_medico(self, medico_id: int):
        """Anula el médico tratante."""
        try:
            with get_db_session() as session:
                medico_repo = MedicoTratanteRepository(session)
                if medico_repo.anular(medico_id):
                    session.commit()
                    print(f"✅ Médico tratante anulado")
                    self.view.limpiar_formulario()
        except Exception as e:
            print(f"❌ Error anulando médico: {e}")
