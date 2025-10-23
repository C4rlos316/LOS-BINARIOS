import sqlite3


def setup_database():
    """
    Crea el archivo kavak_memory.db y las tablas necesarias.
    Este script debe ejecutarse antes de usar console_agent.py
    """
    # Conectar a la base de datos (se crea si no existe)
    conn = sqlite3.connect('kavak_memory.db')
    cursor = conn.cursor()
    
    # Crear tabla user_memory
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            context TEXT NOT NULL
        )
    ''')
    
    # Crear tabla prompt_rules
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prompt_rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rule_text TEXT NOT NULL
        )
    ''')
    
    # Guardar cambios y cerrar conexión
    conn.commit()
    conn.close()
    
    print("✅ Base de datos 'kavak_memory.db' configurada correctamente.")
    print("   Tablas creadas: 'user_memory' y 'prompt_rules'")


if __name__ == "__main__":
    setup_database()
