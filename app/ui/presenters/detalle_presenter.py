"""
Presenter para el formulario de detalle (patrón MVP).
"""
from typing import Any, Dict, List
from PySide6.QtCore import QObject

from app.ui.views import DetalleForm
from app.config import get_db_session
from app.data.repositories import DetalleRepository, CatalogoRepository
from app.data.repositories.procedimiento_repo import ProcedimientoRepository
from app.data.models.accidente_detalle import AccidenteDetalle


class DetallePresenter(QObject):
    """Presenter para el formulario de detalle."""
    
    def __init__(self, view: DetalleForm):
        super().__init__()
        self.view = view
        self.accidente_id = None
        
        # Conectar señales
        self._connect_signals()
        
        # Cargar catálogos iniciales
        self._cargar_catalogos()
    
    def _connect_signals(self):
        """Conecta las señales de la vista."""
        self.view.buscar_procedimiento_signal.connect(self.buscar_procedimientos)
        self.view.guardar_detalles_signal.connect(self.guardar_detalles)
    
    def _cargar_catalogos(self):
        """Carga los catálogos necesarios."""
        try:
            with get_db_session() as session:
                catalogo_repo = CatalogoRepository(session)
                
                # Tipos de servicio
                tipos = catalogo_repo.get_tipos_servicio()
                self.view.cargar_tipos_servicio(
                    [{"id": t.id, "descripcion": t.descripcion} for t in tipos]
                )
                
                # Cargar TODOS los procedimientos en el combo al inicio
                print("📦 Cargando todos los procedimientos...")
                procedimiento_repo = ProcedimientoRepository(session)
                todos_procedimientos = procedimiento_repo.get_todos_activos()
                print(f"✓ {len(todos_procedimientos)} procedimientos encontrados en BD")
                
                resultado = [{
                    "id": p.id,
                    "codigo": p.codigo,
                    "descripcion": p.descripcion,
                    "codigo_soat": p.codigo_soat,
                    "valor": p.valor,
                } for p in todos_procedimientos]
                
                self.view.cargar_procedimientos(resultado)
                print(f"✓ Combo de procedimientos cargado con {len(resultado)} items")
        except Exception as e:
            print(f"Error cargando catálogos: {e}")
            import traceback
            traceback.print_exc()
    
    def set_accidente_id(self, accidente_id: int):
        """Establece el ID del accidente actual y carga los detalles."""
        self.accidente_id = accidente_id
        self._cargar_detalles()
    
    def buscar_procedimientos(self, termino: str):
        """Busca procedimientos por código o descripción."""
        print(f"🔍 DetallePresenter.buscar_procedimientos() llamado con término: '{termino}'")
        
        if not termino or len(termino) < 2:
            print(f"⚠️ Término muy corto o vacío, ignorando búsqueda")
            return
        
        try:
            with get_db_session() as session:
                procedimiento_repo = ProcedimientoRepository(session)
                procedimientos = procedimiento_repo.buscar(termino)
                
                print(f"📊 Resultado de la búsqueda en BD: {len(procedimientos)} procedimientos")
                
                resultado = [{
                    "id": p.id,
                    "codigo": p.codigo,
                    "descripcion": p.descripcion,
                    "codigo_soat": p.codigo_soat,
                    "valor": p.valor,
                } for p in procedimientos]
                
                # Si solo hay un resultado, auto-completar directamente
                if len(resultado) == 1:
                    print(f"✨ Solo 1 resultado, auto-completando campos...")
                    proc = resultado[0]
                    self.view.txt_codigo_servicio.setText(proc["codigo"])
                    self.view.txt_descripcion.setText(proc["descripcion"])
                    self.view.txt_valor_unitario.setText(str(proc["valor"]))
                    self.view._calcular_valores()
                    # También cargar en combo para referencia
                    self.view.cargar_procedimientos(resultado)
                    self.view.combo_procedimiento.setCurrentIndex(1)  # Seleccionar el único resultado
                    print(f"✓ Campos completados con: {proc['codigo']} - {proc['descripcion']}")
                else:
                    # Varios resultados, cargar en combo
                    print(f"📋 Cargando {len(resultado)} procedimientos en combo...")
                    self.view.cargar_procedimientos(resultado)
                    print(f"✓ Combo cargado")
                
                if not resultado:
                    print(f"ℹ️ No se encontraron procedimientos para: {termino}")
                else:
                    print(f"✅ {len(resultado)} procedimientos encontrados")
        
        except Exception as e:
            print(f"❌ Error buscando procedimientos: {e}")
            import traceback
            traceback.print_exc()
    
    def _cargar_detalles(self):
        """Carga los detalles del accidente."""
        if not self.accidente_id:
            print("⚠️ DetallePresenter: No hay accidente_id para cargar detalles")
            return
        
        try:
            print(f"🔍 DetallePresenter: Buscando detalles para accidente_id={self.accidente_id}")
            with get_db_session() as session:
                detalle_repo = DetalleRepository(session)
                detalles = detalle_repo.get_by_accidente(self.accidente_id)
                
                if detalles:
                    print(f"✓ DetallePresenter: {len(detalles)} detalles encontrados")
                    detalles_dict = []
                    for d in detalles:
                        detalles_dict.append({
                            "id": d.id,
                            "tipo_servicio_id": d.tipo_servicio_id,
                            "tipo_servicio_nombre": d.tipo_servicio.descripcion if d.tipo_servicio else "",
                            "procedimiento_id": d.procedimiento_id,
                            "codigo_servicio": d.codigo_servicio,
                            "descripcion": d.descripcion,
                            "cantidad": d.cantidad,
                            "valor_unitario": d.valor_unitario,
                            "valor_facturado": d.valor_facturado,
                            "valor_reclamado": d.valor_reclamado,
                        })
                    
                    self.view.cargar_detalles(detalles_dict)
                else:
                    print(f"ℹ️ DetallePresenter: No hay detalles registrados para accidente_id={self.accidente_id}")
        
        except Exception as e:
            print(f"❌ Error cargando detalles: {e}")
            import traceback
            traceback.print_exc()
    
    def guardar_detalles(self, detalles: List[Dict[str, Any]]):
        """Guarda todos los detalles del accidente."""
        if not self.accidente_id:
            print("Error: No hay accidente seleccionado")
            return
        
        if not detalles:
            print("Error: No hay detalles para guardar")
            return
        
        try:
            with get_db_session() as session:
                detalle_repo = DetalleRepository(session)
                
                # 1. Eliminar detalles existentes
                print(f"🗑️ Eliminando detalles existentes...")
                count_eliminados = detalle_repo.delete_by_accidente(self.accidente_id)
                print(f"  ✓ {count_eliminados} detalles eliminados")
                
                # 2. Crear nuevos detalles
                print(f"💾 Guardando {len(detalles)} nuevos detalles...")
                nuevos_detalles = []
                for datos in detalles:
                    detalle = AccidenteDetalle(
                        accidente_id=self.accidente_id,
                        tipo_servicio_id=datos["tipo_servicio_id"],
                        procedimiento_id=datos.get("procedimiento_id"),
                        codigo_servicio=datos.get("codigo_servicio"),
                        descripcion=datos.get("descripcion"),
                        cantidad=datos["cantidad"],
                        valor_unitario=datos["valor_unitario"],
                        valor_facturado=datos["valor_facturado"],
                        valor_reclamado=datos["valor_reclamado"],
                        estado=1
                    )
                    nuevos_detalles.append(detalle)
                
                # Guardar en lote
                detalle_repo.create_bulk(nuevos_detalles)
                session.commit()
                
                print(f"✅ {len(nuevos_detalles)} detalles guardados correctamente")
                
                # Recargar detalles
                self._cargar_detalles()
                
                # Mostrar mensaje de éxito
                self.view.mostrar_detalles_guardados()
        
        except Exception as e:
            print(f"❌ Error guardando detalles: {e}")
            import traceback
            traceback.print_exc()
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(
                self.view,
                "Error",
                f"Error al guardar detalles: {str(e)}"
            )
