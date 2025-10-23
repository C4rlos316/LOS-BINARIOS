"""
Script para resetear la base de datos a estado inicial (0)
Elimina todas las reglas y memorias aprendidas
"""

from backend.utils.database import DatabaseManager


def main():
    """
    Resetea la base de datos completamente.
    """
    print("\n" + "="*60)
    print("SCRIPT DE RESETEO DE BASE DE DATOS")
    print("="*60)
    print("\n⚠️  ADVERTENCIA: Esta acción eliminará:")
    print("   - Todas las reglas aprendidas")
    print("   - Todas las memorias de usuarios")
    print("   - El sistema volverá a estado inicial (0)")
    
    # Pedir confirmación
    confirmacion = input("\n¿Estás seguro? Escribe 'RESETEAR' para confirmar: ").strip()
    
    if confirmacion == 'RESETEAR':
        # Crear instancia del gestor (crea BD automáticamente si no existe)
        db_manager = DatabaseManager()
        
        # Resetear
        db_manager.reset_database()
        
        print("\n✅ Proceso completado exitosamente")
        print("\nAhora puedes ejecutar:")
        print("   python main.py")
        print("\nEl sistema iniciará desde cero con Madurez: 0/100")
    else:
        print("\n❌ Reseteo cancelado. No se realizaron cambios.")


if __name__ == "__main__":
    main()
