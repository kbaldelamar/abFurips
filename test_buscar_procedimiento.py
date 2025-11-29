"""
Script de prueba para verificar búsqueda de procedimientos.
"""
from app.config import get_db_session
from app.data.repositories.procedimiento_repo import ProcedimientoRepository

def test_buscar(termino: str):
    print(f"\n{'='*60}")
    print(f"Buscando: '{termino}'")
    print(f"{'='*60}")
    
    try:
        with get_db_session() as session:
            repo = ProcedimientoRepository(session)
            resultados = repo.buscar(termino)
            
            print(f"✓ Encontrados: {len(resultados)} procedimientos")
            
            for i, proc in enumerate(resultados, 1):
                print(f"\n[{i}] ID: {proc.id}")
                print(f"    Código: {proc.codigo}")
                print(f"    Descripción: {proc.descripcion}")
                print(f"    Código SOAT: {proc.codigo_soat}")
                print(f"    Valor: ${proc.valor:,}")
                print(f"    Estado: {proc.estado}")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Probar diferentes búsquedas
    test_buscar("39003")
    test_buscar("Honorarios")
    test_buscar("transporte")
    test_buscar("PR-39003")
    test_buscar("xyz")  # No debería encontrar nada
