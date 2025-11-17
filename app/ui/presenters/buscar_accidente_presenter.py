"""
Presenter para búsqueda de accidentes.
"""
from typing import Dict, Any, List
from app.data.repositories.accidente_repo import AccidenteRepository
from app.config.db import get_db_session


class BuscarAccidentePresenter:
    """Presenter para búsqueda de accidentes."""
    
    def __init__(self, view):
        self.view = view
        self.view.presenter = self
    
    def buscar_accidentes(self, filtros: Dict[str, Any]):
        """Busca accidentes según filtros."""
        try:
            with get_db_session() as session:
                repo = AccidenteRepository(session)
                resultados = repo.buscar_accidentes_con_victima(filtros)
                
                # Convertir a diccionarios para la vista
                accidentes_dict = []
                for acc in resultados:
                    accidentes_dict.append({
                        "id": acc.id,
                        "consecutivo": acc.numero_consecutivo,
                        "factura": acc.numero_factura,
                        "fecha_evento": acc.fecha_evento,
                        "hora_evento": acc.hora_evento.strftime("%H:%M") if acc.hora_evento else "",
                        "tipo_identificacion": acc.tipo_identificacion if hasattr(acc, 'tipo_identificacion') else "",
                        "numero_identificacion": acc.numero_identificacion if hasattr(acc, 'numero_identificacion') else "",
                        "primer_nombre": acc.primer_nombre if hasattr(acc, 'primer_nombre') else "",
                        "primer_apellido": acc.primer_apellido if hasattr(acc, 'primer_apellido') else "",
                        "segundo_apellido": acc.segundo_apellido if hasattr(acc, 'segundo_apellido') else "",
                    })
                
                self.view.cargar_resultados(accidentes_dict)
                
                if not accidentes_dict:
                    print("ℹ️ No se encontraron accidentes con los filtros especificados")
                else:
                    print(f"✓ Se encontraron {len(accidentes_dict)} accidente(s)")
                
        except Exception as e:
            print(f"❌ Error buscando accidentes: {e}")
            import traceback
            traceback.print_exc()
