"""
Presenter para el formulario de accidente (patrón MVP).
"""
from PySide6.QtCore import QObject

from app.ui.views import AccidenteForm
from app.config import get_db_session
from app.data.repositories import CatalogoRepository, PrestadorRepository
from app.domain.services import AccidenteService
from app.domain.dto import AccidenteDTO


class AccidentePresenter(QObject):
    """Presenter para el formulario de accidente."""
    
    def __init__(self, view: AccidenteForm):
        super().__init__()
        self.view = view
        self.accidente_id = None  # ID del accidente actual
        
        # Inicializar presenters
        from app.ui.presenters.victima_presenter import VictimaPresenter
        from app.ui.presenters.conductor_presenter import ConductorPresenter
        from app.ui.presenters.propietario_presenter import PropietarioPresenter
        
        self.victima_presenter = VictimaPresenter(self.view.victima_form)
        self.conductor_presenter = ConductorPresenter(self.view.conductor_form)
        self.propietario_presenter = PropietarioPresenter(self.view.propietario_form)
        
        # Establecer referencias cruzadas para copiar datos entre tabs
        self.victima_presenter.conductor_presenter = self.conductor_presenter
        self.victima_presenter.propietario_presenter = self.propietario_presenter
        
        # Conectar señales
        self._connect_signals()
        
        # Cargar catálogos iniciales
        self._cargar_catalogos()
    
    def _connect_signals(self):
        """Conecta las señales de la vista."""
        self.view.guardar_accidente_signal.connect(self.guardar_accidente)
        self.view.actualizar_accidente_signal.connect(self.actualizar_accidente)
        self.view.buscar_accidente_signal.connect(self.abrir_buscar_accidente)
    
    def _cargar_catalogos(self):
        """Carga los catálogos necesarios en los combos."""
        try:
            with get_db_session() as session:
                catalogo_repo = CatalogoRepository(session)
                prestador_repo = PrestadorRepository(session)
                
                # Cargar prestadores
                prestadores = prestador_repo.get_all()
                prestadores_data = [
                    {"id": p.id, "razon_social": p.razon_social}
                    for p in prestadores
                ]
                self.view.cargar_prestadores(prestadores_data)
                
                # Cargar naturalezas de evento
                naturalezas = catalogo_repo.get_naturalezas_evento()
                naturalezas_data = [
                    {"id": n.id, "codigo": n.codigo, "descripcion": n.descripcion}
                    for n in naturalezas
                ]
                self.view.cargar_naturalezas(naturalezas_data)
                
                # Cargar TODOS los municipios
                municipios = catalogo_repo.get_todos_municipios()
                municipios_data = [
                    {"id": m.id, "nombre": m.nombre}
                    for m in municipios
                ]
                self.view.cargar_municipios(municipios_data)
                
                # Cargar estados de aseguramiento
                estados = catalogo_repo.get_estados_aseguramiento()
                estados_data = [
                    {"id": e.id, "codigo": e.codigo, "descripcion": e.descripcion}
                    for e in estados
                ]
                self.view.cargar_estados_aseguramiento(estados_data)
        
        except Exception as e:
            print(f"Error cargando catálogos: {e}")
    
    def guardar_accidente(self, datos: dict):
        """Guarda el accidente en la base de datos."""
        try:
            # Validar datos obligatorios básicos
            if not datos.get("prestador_id"):
                self._mostrar_error("Debe seleccionar un prestador")
                return
            
            if not datos.get("numero_factura"):
                self._mostrar_error("El número de factura es obligatorio")
                return
            
            if not datos.get("numero_rad_siras"):
                self._mostrar_error("El radicado SIRAS es obligatorio")
                return
            
            # Validar que si la naturaleza es "Otro", se ingrese la descripción
            if datos.get("naturaleza_evento_id"):
                with get_db_session() as session:
                    from app.data.repositories.catalogo_repo import CatalogoRepository
                    catalogo_repo = CatalogoRepository(session)
                    naturaleza = catalogo_repo.get_naturaleza_evento_by_id(datos["naturaleza_evento_id"])
                    
                    # Si el código de naturaleza es "99" (Otro), la descripción es obligatoria
                    if naturaleza and naturaleza.codigo == "99":
                        if not datos.get("descripcion_otro_evento") or not datos.get("descripcion_otro_evento").strip():
                            self._mostrar_error("Debe ingresar la descripción cuando la naturaleza del evento es 'Otro'")
                            return
            
            # Crear DTO
            accidente_dto = AccidenteDTO(**datos)
            
            # Guardar en BD
            with get_db_session() as session:
                accidente_service = AccidenteService(session)
                accidente, errores = accidente_service.crear_accidente(accidente_dto)
                
                if errores:
                    self._mostrar_error("\n".join(errores))
                    return
                
                if accidente:
                    # Guardar ID del accidente actual
                    self.accidente_id = accidente.id
                    
                    # Actualizar la vista con el ID y consecutivo
                    self.view.mostrar_accidente_guardado(accidente.id, accidente.numero_consecutivo)
                    
                    # Pasar el ID del accidente a todos los presenters
                    self.victima_presenter.set_accidente_id(accidente.id)
                    self.conductor_presenter.set_accidente_id(accidente.id)
                    self.propietario_presenter.set_accidente_id(accidente.id)
                    
                    # Mostrar mensaje de éxito
                    self._mostrar_exito(
                        f"✅ Accidente guardado exitosamente\n\n"
                        f"ID: {accidente.id}\n"
                        f"Consecutivo: {accidente.numero_consecutivo}"
                    )
        
        except Exception as e:
            self._mostrar_error(f"Error al guardar accidente: {str(e)}")
    
    def _mostrar_error(self, mensaje: str):
        """Muestra un mensaje de error."""
        # Buscar la ventana principal
        parent = self.view.window()
        if hasattr(parent, "mostrar_mensaje"):
            parent.mostrar_mensaje("Error", mensaje, "error")
    
    def _mostrar_exito(self, mensaje: str):
        """Muestra un mensaje de éxito."""
        parent = self.view.window()
        if hasattr(parent, "mostrar_mensaje"):
            parent.mostrar_mensaje("Éxito", mensaje, "info")
    
    def actualizar_accidente(self, datos: dict):
        """Actualiza un accidente existente."""
        try:
            accidente_id = datos.get("id")
            if not accidente_id:
                self._mostrar_error("No hay un accidente seleccionado para actualizar")
                return
            
            # Validar datos obligatorios
            if not datos.get("prestador_id"):
                self._mostrar_error("Debe seleccionar un prestador")
                return
            
            if not datos.get("numero_factura"):
                self._mostrar_error("El número de factura es obligatorio")
                return
            
            # Validar que si la naturaleza es "Otro", se ingrese la descripción
            if datos.get("naturaleza_evento_id"):
                with get_db_session() as session:
                    from app.data.repositories.catalogo_repo import CatalogoRepository
                    catalogo_repo = CatalogoRepository(session)
                    naturaleza = catalogo_repo.get_naturaleza_evento_by_id(datos["naturaleza_evento_id"])
                    
                    # Si el código de naturaleza es "99" (Otro), la descripción es obligatoria
                    if naturaleza and naturaleza.codigo == "99":
                        if not datos.get("descripcion_otro_evento") or not datos.get("descripcion_otro_evento").strip():
                            self._mostrar_error("Debe ingresar la descripción cuando la naturaleza del evento es 'Otro'")
                            return
            
            # Actualizar en BD
            with get_db_session() as session:
                from app.data.repositories.accidente_repo import AccidenteRepository
                repo = AccidenteRepository(session)
                
                accidente = repo.get_by_id(accidente_id)
                if not accidente:
                    self._mostrar_error(f"No se encontró el accidente con ID {accidente_id}")
                    return
                
                # Actualizar campos
                accidente.prestador_id = datos["prestador_id"]
                accidente.numero_factura = datos["numero_factura"]
                accidente.numero_rad_siras = datos.get("numero_rad_siras")
                accidente.naturaleza_evento_id = datos.get("naturaleza_evento_id")
                accidente.descripcion_otro_evento = datos.get("descripcion_otro_evento")
                accidente.fecha_evento = datos.get("fecha_evento")
                accidente.hora_evento = datos.get("hora_evento")
                accidente.municipio_evento_id = datos.get("municipio_evento_id")
                accidente.direccion_evento = datos.get("direccion_evento")
                accidente.zona = datos.get("zona")
                accidente.estado_aseguramiento_id = datos.get("estado_aseguramiento_id")
                
                session.commit()
                
                self._mostrar_exito(f"✅ Accidente actualizado exitosamente\n\nID: {accidente.id}")
                
                print(f"✓ Accidente {accidente.id} actualizado")
        
        except Exception as e:
            print(f"❌ Error actualizando accidente: {e}")
            import traceback
            traceback.print_exc()
            self._mostrar_error(f"Error al actualizar accidente: {str(e)}")
    
    def abrir_buscar_accidente(self):
        """Abre el diálogo de búsqueda de accidentes."""
        from app.ui.views.buscar_accidente_dialog import BuscarAccidenteDialog
        from app.ui.presenters.buscar_accidente_presenter import BuscarAccidentePresenter
        
        dialog = BuscarAccidenteDialog(self.view)
        presenter = BuscarAccidentePresenter(dialog)
        
        # Conectar señal de selección
        dialog.accidente_seleccionado.connect(self.cargar_accidente_por_id)
        
        # Mostrar diálogo
        dialog.exec()
    
    def cargar_accidente_por_id(self, accidente_id: int):
        """Carga un accidente completo por su ID."""
        try:
            with get_db_session() as session:
                from app.data.repositories.accidente_repo import AccidenteRepository
                repo = AccidenteRepository(session)
                
                accidente = repo.get_by_id(accidente_id)
                if not accidente:
                    self._mostrar_error(f"No se encontró el accidente con ID {accidente_id}")
                    return
                
                # Preparar datos para la vista
                accidente_dict = {
                    "id": accidente.id,
                    "prestador_id": accidente.prestador_id,
                    "numero_consecutivo": accidente.numero_consecutivo,
                    "numero_factura": accidente.numero_factura,
                    "numero_rad_siras": accidente.numero_rad_siras,
                    "naturaleza_evento_id": accidente.naturaleza_evento_id,
                    "descripcion_otro_evento": accidente.descripcion_otro_evento,
                    "fecha_evento": accidente.fecha_evento,
                    "hora_evento": accidente.hora_evento,
                    "municipio_evento_id": accidente.municipio_evento_id,
                    "direccion_evento": accidente.direccion_evento,
                    "zona": accidente.zona,
                    "estado_aseguramiento_id": accidente.estado_aseguramiento_id,
                }
                
                # Cargar en la vista
                self.view.cargar_accidente(accidente_dict)
                
                # Guardar ID
                self.accidente_id = accidente.id
                
                # Pasar el ID a los presenters de tabs
                self.victima_presenter.set_accidente_id(accidente.id)
                self.conductor_presenter.set_accidente_id(accidente.id)
                self.propietario_presenter.set_accidente_id(accidente.id)
                
                print(f"✓ Accidente {accidente.id} cargado exitosamente")
        
        except Exception as e:
            print(f"❌ Error cargando accidente: {e}")
            import traceback
            traceback.print_exc()
            self._mostrar_error(f"Error al cargar accidente: {str(e)}")
