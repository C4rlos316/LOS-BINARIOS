"""
Gestor de Base de Datos
Maneja todas las operaciones con SQLite
"""

import sqlite3
from typing import List, Dict, Tuple, Optional


class DatabaseManager:
    """
    Clase para gestionar todas las operaciones de base de datos.
    Implementa patrón Repository para abstraer el acceso a datos.
    """
    
    DB_PATH = 'kavak_memory.db'
    
    def __init__(self, db_path: str = None):
        """
        Inicializa el gestor de base de datos.
        Crea las tablas automáticamente si no existen.
        
        Args:
            db_path: Ruta a la base de datos (opcional)
        """
        self.db_path = db_path or self.DB_PATH
        self._initialize_database()
    
    def _get_connection(self) -> sqlite3.Connection:
        """
        Obtiene una conexión a la base de datos.
        
        Returns:
            sqlite3.Connection: Conexión a la BD
        """
        return sqlite3.connect(self.db_path)
    
    def _initialize_database(self):
        """
        Crea las tablas si no existen.
        Se ejecuta automáticamente al instanciar DatabaseManager.
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Crear tabla de usuarios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Crear tabla user_memory
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                context TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # Crear tabla prompt_rules con categorización de errores
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prompt_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rule_text TEXT NOT NULL,
                error_category TEXT DEFAULT 'general',
                validation_score REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    # ==================== USUARIOS ====================
    
    def create_user(self, user_id: str, username: str) -> bool:
        """
        Crea un nuevo usuario en la base de datos.
        
        Args:
            user_id: ID único del usuario
            username: Nombre del usuario
        
        Returns:
            bool: True si se creó exitosamente, False si ya existe
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                'INSERT INTO users (user_id, username) VALUES (?, ?)',
                (user_id, username)
            )
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            # Usuario ya existe
            return False
    
    def user_exists(self, user_id: str) -> bool:
        """
        Verifica si un usuario existe en la base de datos.
        
        Args:
            user_id: ID del usuario a verificar
        
        Returns:
            bool: True si existe, False si no
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT COUNT(*) FROM users WHERE user_id = ?',
            (user_id,)
        )
        count = cursor.fetchone()[0]
        
        conn.close()
        return count > 0
    
    def get_username(self, user_id: str) -> Optional[str]:
        """
        Obtiene el nombre de usuario.
        
        Args:
            user_id: ID del usuario
        
        Returns:
            str: Nombre del usuario o None si no existe
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT username FROM users WHERE user_id = ?',
            (user_id,)
        )
        result = cursor.fetchone()
        
        conn.close()
        return result[0] if result else None
    
    # ==================== REGLAS ====================
    
    def get_all_rules(self) -> str:
        """
        Obtiene todas las reglas de la base de datos.
        
        Returns:
            str: Todas las reglas unidas por saltos de línea
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT rule_text FROM prompt_rules')
        results = cursor.fetchall()
        
        conn.close()
        
        if results:
            return '\n'.join([row[0] for row in results])
        return ''
    
    def save_rule(self, rule_text: str, error_category: str = 'general', 
                  validation_score: float = 0.0) -> int:
        """
        Guarda una nueva regla en la base de datos.
        
        Args:
            rule_text: Texto de la regla
            error_category: Categoría del error
            validation_score: Score de validación (0.0-1.0)
        
        Returns:
            int: ID de la regla insertada
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            'INSERT INTO prompt_rules (rule_text, error_category, validation_score) VALUES (?, ?, ?)',
            (rule_text, error_category, validation_score)
        )
        
        rule_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return rule_id
    
    def get_rules_by_category(self, category: str) -> List[str]:
        """
        Obtiene reglas filtradas por categoría.
        
        Args:
            category: Categoría de error
        
        Returns:
            List[str]: Lista de reglas de esa categoría
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT rule_text FROM prompt_rules WHERE error_category = ?',
            (category,)
        )
        results = cursor.fetchall()
        
        conn.close()
        
        return [row[0] for row in results]
    
    # ==================== MEMORIA ====================
    
    def get_user_memory(self, user_id: str) -> str:
        """
        Obtiene TODA la memoria histórica del usuario.
        
        Args:
            user_id: ID del usuario
        
        Returns:
            str: Memoria formateada del usuario
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT context FROM user_memory WHERE user_id = ? ORDER BY id ASC',
            (user_id,)
        )
        results = cursor.fetchall()
        
        conn.close()
        
        if results:
            all_memories = '\n'.join([f"- {row[0]}" for row in results])
            return f"HISTORIAL DE MEMORIA DEL USUARIO:\n{all_memories}"
        return ''
    
    def save_user_memory(self, user_id: str, context: str) -> int:
        """
        Guarda una memoria del usuario.
        
        Args:
            user_id: ID del usuario
            context: Contexto a guardar
        
        Returns:
            int: ID de la memoria insertada
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            'INSERT INTO user_memory (user_id, context) VALUES (?, ?)',
            (user_id, context)
        )
        
        memory_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return memory_id
    
    # ==================== MÉTRICAS ====================
    
    def get_system_stats(self) -> Dict[str, any]:
        """
        Obtiene estadísticas globales del sistema.
        
        Returns:
            Dict: Diccionario con estadísticas
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Contar reglas
        cursor.execute('SELECT COUNT(*) FROM prompt_rules')
        total_rules = cursor.fetchone()[0]
        
        # Contar usuarios registrados
        cursor.execute('SELECT COUNT(*) FROM users')
        total_users = cursor.fetchone()[0]
        
        # Contar memorias
        cursor.execute('SELECT COUNT(*) FROM user_memory')
        total_memories = cursor.fetchone()[0]
        
        # Distribución de errores
        cursor.execute('''
            SELECT error_category, COUNT(*) as count 
            FROM prompt_rules 
            WHERE error_category IS NOT NULL
            GROUP BY error_category
        ''')
        error_distribution = dict(cursor.fetchall())
        
        # Score promedio de validación
        cursor.execute('SELECT AVG(validation_score) FROM prompt_rules WHERE validation_score > 0')
        avg_validation = cursor.fetchone()[0] or 0.0
        
        conn.close()
        
        return {
            'total_rules': total_rules,
            'total_users': total_users,
            'total_memories': total_memories,
            'error_distribution': error_distribution,
            'avg_validation_score': avg_validation
        }
    
    # ==================== UTILIDADES ====================
    
    def clear_all_rules(self):
        """Limpia todas las reglas de la base de datos."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM prompt_rules')
        conn.commit()
        conn.close()
        print("✓ Todas las reglas han sido eliminadas")
    
    def clear_all_memories(self):
        """Limpia todas las memorias de la base de datos."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM user_memory')
        conn.commit()
        conn.close()
        print("✓ Todas las memorias han sido eliminadas")
    
    def reset_database(self):
        """
        Resetea completamente la base de datos a estado inicial (0).
        Elimina todas las reglas y memorias.
        """
        print("\n⚠️  RESETEO COMPLETO DE LA BASE DE DATOS")
        print("="*60)
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Contar antes de borrar
        cursor.execute('SELECT COUNT(*) FROM prompt_rules')
        rules_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM user_memory')
        memories_count = cursor.fetchone()[0]
        
        print(f"Reglas a eliminar: {rules_count}")
        print(f"Memorias a eliminar: {memories_count}")
        
        # Borrar todo
        cursor.execute('DELETE FROM prompt_rules')
        cursor.execute('DELETE FROM user_memory')
        cursor.execute('DELETE FROM users')
        
        # Resetear autoincrement
        cursor.execute('DELETE FROM sqlite_sequence WHERE name="prompt_rules"')
        cursor.execute('DELETE FROM sqlite_sequence WHERE name="user_memory"')
        cursor.execute('DELETE FROM sqlite_sequence WHERE name="users"')
        
        conn.commit()
        conn.close()
        
        print("\n✅ Base de datos reseteada completamente a 0")
        print("="*60)
