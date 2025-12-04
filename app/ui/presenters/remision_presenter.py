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
from app.data.repositories.prestador_repo import PrestadorRepository


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
        # Cargar prestadores para el combo en el formulario de remisión
        self._cargar_prestadores()
    
    def _connect_signals(self):
        """Conecta las señales de la vista."""
        self.view.guardar_remision_signal.connect(self.guardar_remision)
        self.view.actualizar_remision_signal.connect(self.actualizar_remision)
        self.view.eliminar_remision_signal.connect(self.eliminar_remision)
        self.view.anular_remision_signal.connect(self.anular_remision)
    
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

    def _cargar_prestadores(self):
        """Carga la lista de prestadores de salud para el combo de prestador."""
        try:
            with get_db_session() as session:
                prest_repo = PrestadorRepository(session)
                prestadores = prest_repo.get_all(limit=200)

                lista = []
                for p in prestadores:
                    lista.append({
                        "id": p.id,
                        "razon_social": getattr(p, "razon_social", None) or getattr(p, "nombre", None) or f"Prestador {p.id}",
                    })

                self.view.cargar_prestadores(lista)
                print(f"✓ {len(lista)} prestadores cargados")
        except Exception as e:
            print(f"❌ Error cargando prestadores: {e}")
    
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
                # Mostrar estados para depuración y normalizar valores
                estados = [getattr(r, 'estado', None) for r in remisiones]
                print(f"[RemisionPresenter] Remisiones encontradas estados: {estados}")

                def _is_activo(estado_value):
                    if estado_value is None:
                        return False
                    try:
                        s = str(estado_value).strip().lower()
                    except Exception:
                        return False
                    return s in ("activo", "1", "true", "t", "si", "s", "yes")

                # Filtrar solo las remisiones consideradas activas según varias representaciones
                remisiones_activas = [r for r in remisiones if _is_activo(getattr(r, 'estado', None))]
                # Solo mostramos la primera remisión activa (solo se permite 1 por accidente)
                if remisiones_activas:
                    remision = remisiones_activas[0]
                    datos = {
                        "id": remision.id,
                        "accidente_id": remision.accidente_id,
                        "tipo_referencia": remision.tipo_referencia,
                        "fecha_remision": remision.fecha_remision,
                        "hora_salida": remision.hora_salida,
                        "fecha_aceptacion": remision.fecha_aceptacion,
                        "hora_aceptacion": remision.hora_aceptacion,
                        "ipsRecibe": getattr(remision, "ipsRecibe", None),
                        "codigo_hab_recibe": remision.codigo_hab_recibe,
                        "profesional_recibe": remision.profesional_recibe or "",
                        "cargo_Recibe": getattr(remision, "cargo_Recibe", None),
                        "placa_ambulancia": remision.placa_ambulancia,
                        "estado": remision.estado,
                        "persona_remite_id": getattr(remision, "persona_remite_id", None),
                        "creado_en": remision.creado_en,
                        "actualizado_en": remision.actualizado_en,
                        "prestadorId": getattr(remision, "prestadorId", None),
                    }
                    self.view.set_datos_remision(datos)
                    self.view.mostrar_estado_remision(True)
                else:
                    self.view.limpiar_formulario()
                    self.view.mostrar_estado_remision(False)
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

                existentes = remision_repo.get_by_accidente(self.accidente_id)
                # Solo consideramos remisiones activas como 'existentes' para evitar reactivar/actualizar inactivas
                existentes_activas = [r for r in existentes if getattr(r, 'estado', 'activo') == 'activo']
                if existentes_activas:
                    # Si ya existe una remisión activa, actualizamos la primera (no creamos otra)
                    remision = existentes_activas[0]
                    remision.tipo_referencia = datos["tipo_referencia"]
                    remision.fecha_remision = datos["fecha_remision"]
                    remision.hora_salida = datos["hora_salida"]
                    remision.fecha_aceptacion = datos["fecha_aceptacion"]
                    remision.hora_aceptacion = datos["hora_aceptacion"]
                    ips = datos.get("ipsRecibe")
                    if ips is None:
                        ips = getattr(remision, "ipsRecibe", "") or ""
                    remision.ipsRecibe = ips
                    remision.codigo_hab_recibe = datos.get("codigo_hab_recibe")
                    remision.profesional_recibe = datos["profesional_recibe"]
                    remision.cargo_Recibe = datos.get("cargo_Recibe")
                    remision.placa_ambulancia = datos["placa_ambulancia"]
                    remision.estado = datos.get("estado", "activo")
                    remision.persona_remite_id = datos.get("persona_remite_id")
                    remision.prestadorId = datos.get("prestadorId")

                    remision_repo.update(remision)
                    session.commit()
                    print("✅ Remisión existente actualizada (solo 1 por accidente)")
                else:
                    # Asegurar valor no nulo para ipsRecibe al crear
                    ips_val = datos.get("ipsRecibe") or ""
                    remision = AccidenteRemision(
                        accidente_id=self.accidente_id,
                        tipo_referencia=datos["tipo_referencia"],
                        fecha_remision=datos["fecha_remision"],
                        hora_salida=datos["hora_salida"],
                        fecha_aceptacion=datos["fecha_aceptacion"],
                        hora_aceptacion=datos["hora_aceptacion"],
                        ipsRecibe=ips_val,
                        codigo_hab_recibe=datos.get("codigo_hab_recibe"),
                        profesional_recibe=datos["profesional_recibe"],
                        cargo_Recibe=datos.get("cargo_Recibe"),
                        placa_ambulancia=datos["placa_ambulancia"],
                        estado=datos.get("estado", "activo"),
                        persona_remite_id=datos.get("persona_remite_id"),
                        prestadorId=datos.get("prestadorId"),
                    )

                    remision = remision_repo.create(remision)
                    session.commit()
                    print("✅ Remisión guardada")

                # Recargar tabla
                self._cargar_remisiones()
                self.view.mostrar_estado_remision(True)

        except Exception as e:
            print(f"❌ Error guardando/actualizando remisión: {e}")
            import traceback
            traceback.print_exc()

    def anular_remision(self, remision_id: int):
        """Anula (desactiva) una remisión cambiando su estado a 'inactivo'."""
        try:
            with get_db_session() as session:
                remision_repo = RemisionRepository(session)
                remision = remision_repo.get_by_id(remision_id)
                if remision and getattr(remision, 'estado', 'activo') == 'activo':
                    remision.estado = 'inactivo'
                    session.commit()
                    print(f"✅ Remisión {remision_id} anulada (estado inactivo)")
                    # Limpiar formulario inmediatamente y recargar remisiones
                    try:
                        self.view.limpiar_formulario()
                        self.view.mostrar_estado_remision(False)
                    except Exception:
                        pass
                    self._cargar_remisiones()
                else:
                    print(f"❌ Remisión {remision_id} no encontrada o ya inactiva")
        except Exception as e:
            print(f"❌ Error anulando remisión: {e}")
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
                remision.fecha_aceptacion = datos["fecha_aceptacion"]
                remision.hora_aceptacion = datos["hora_aceptacion"]
                # Mantener valor actual si el formulario no envía ipsRecibe
                ips = datos.get("ipsRecibe")
                if ips is None:
                    ips = getattr(remision, "ipsRecibe", "") or ""
                remision.ipsRecibe = ips
                remision.codigo_hab_recibe = datos.get("codigo_hab_recibe")
                remision.profesional_recibe = datos["profesional_recibe"]
                remision.cargo_Recibe = datos.get("cargo_Recibe")
                remision.placa_ambulancia = datos["placa_ambulancia"]
                remision.estado = datos.get("estado", remision.estado)
                remision.persona_remite_id = datos.get("persona_remite_id", remision.persona_remite_id)
                remision.prestadorId = datos.get("prestadorId", remision.prestadorId)

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
            import traceback
            traceback.print_exc()
    
    def limpiar(self):
        """Limpia el formulario."""
        self.view.limpiar_formulario()
        self.view.limpiar_tabla()
