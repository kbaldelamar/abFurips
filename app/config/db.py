"""
Configuración de conexiones a bases de datos.
Crea engines y session factories para:
- BD principal furips (RW)
- BD externa (RO)
"""
from contextlib import contextmanager
from typing import Generator, Optional

from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session

from app.config.settings import get_settings

# Variables globales para lazy initialization
_engine_app: Optional[Engine] = None
_engine_ext: Optional[Engine] = None
_SessionApp = None
_SessionExt = None


def _init_engines():
    """Inicializa los engines (lazy)."""
    global _engine_app, _engine_ext, _SessionApp, _SessionExt
    
    if _engine_app is None:
        settings = get_settings()
        
        # Engine principal
        _engine_app = create_engine(
            settings.DB_URL,
            pool_size=settings.DB_POOL_SIZE,
            pool_recycle=settings.DB_POOL_RECYCLE,
            pool_pre_ping=True,
            echo=settings.DB_ECHO,
        )
        _SessionApp = sessionmaker(
            bind=_engine_app,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
        )
        
        # Engine externo (opcional)
        if settings.DB_EXT_URL:
            _engine_ext = create_engine(
                settings.DB_EXT_URL,
                pool_size=settings.DB_EXT_POOL_SIZE,
                pool_recycle=settings.DB_EXT_POOL_RECYCLE,
                pool_pre_ping=True,
                echo=settings.DB_EXT_ECHO,
            )
            _SessionExt = sessionmaker(
                bind=_engine_ext,
                autocommit=False,
                autoflush=False,
                expire_on_commit=False,
            )
            
            # Forzar READ-ONLY
            @event.listens_for(_SessionExt, "before_flush")
            def receive_before_flush(session, flush_context, instances):
                """Previene escrituras en la BD externa."""
                if session.new or session.dirty or session.deleted:
                    raise RuntimeError(
                        "La sesión externa es READ-ONLY. "
                        "No se permiten operaciones de escritura."
                    )


def get_engine_app() -> Engine:
    """Retorna el engine principal."""
    if _engine_app is None:
        _init_engines()
    return _engine_app


def get_session_app_factory():
    """Retorna la session factory principal."""
    if _SessionApp is None:
        _init_engines()
    return _SessionApp


def get_engine_ext() -> Optional[Engine]:
    """Retorna el engine externo."""
    if _engine_app is None:  # Inicializar si no se ha hecho
        _init_engines()
    return _engine_ext


def get_session_ext_factory():
    """Retorna la session factory externa."""
    if _engine_app is None:  # Inicializar si no se ha hecho
        _init_engines()
    return _SessionExt


# ============================================================================
# CONTEXT MANAGERS PARA SESIONES
# ============================================================================
@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    Context manager para sesión principal (furips RW).
    
    Usage:
        with get_db_session() as session:
            # usar session
            pass
    """
    SessionFactory = get_session_app_factory()
    session = SessionFactory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@contextmanager
def get_ext_session() -> Generator[Session, None, None]:
    """
    Context manager para sesión externa (RO).
    
    Usage:
        with get_ext_session() as session:
            # solo consultas SELECT
            pass
    """
    SessionFactory = get_session_ext_factory()
    if SessionFactory is None:
        raise RuntimeError(
            "La base de datos externa no está configurada. "
            "Configure DB_EXT_URL en .env"
        )
    
    session = SessionFactory()
    try:
        yield session
    finally:
        session.close()


# ============================================================================
# FUNCIONES DE UTILIDAD
# ============================================================================
def init_db():
    """Inicializa las tablas en la BD principal (solo desarrollo)."""
    from app.data.models.base import Base
    Base.metadata.create_all(bind=get_engine_app())


def check_db_connection() -> bool:
    """Verifica la conexión a la BD principal."""
    try:
        engine = get_engine_app()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"Error al conectar con la BD: {e}")
        return False


def check_ext_connection() -> bool:
    """Verifica la conexión a la BD externa."""
    engine = get_engine_ext()
    if engine is None:
        return False
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"Error al conectar con la BD externa: {e}")
        return False


# ============================================================================
# EXPORTS PARA COMPATIBILIDAD
# ============================================================================
engine_app = property(lambda self: get_engine_app())
SessionApp = property(lambda self: get_session_app_factory())
engine_ext = property(lambda self: get_engine_ext())
SessionExt = property(lambda self: get_session_ext_factory())
