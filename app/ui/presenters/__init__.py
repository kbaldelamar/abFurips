"""Presenters de la aplicación."""
from app.ui.presenters.main_presenter import MainPresenter
from app.ui.presenters.accidente_presenter import AccidentePresenter
from app.ui.presenters.detalle_presenter import DetallePresenter
from app.ui.presenters.medico_tratante_presenter import MedicoTratantePresenter
from app.ui.presenters.remision_presenter import RemisionPresenter

__all__ = [
    "MainPresenter",
    "AccidentePresenter",
    "DetallePresenter",
    "MedicoTratantePresenter",
    "RemisionPresenter",
]
