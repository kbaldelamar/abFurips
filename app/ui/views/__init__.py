"""Vistas de la aplicación."""
from app.ui.views.main_window import MainWindow
from app.ui.views.accidente_form import AccidenteForm
from app.ui.views.detalle_form import DetalleForm
from app.ui.views.medico_tratante_form import MedicoTratanteForm
from app.ui.views.remision_form import RemisionForm

__all__ = [
    "MainWindow",
    "AccidenteForm",
    "DetalleForm",
    "MedicoTratanteForm",
    "RemisionForm",
]
