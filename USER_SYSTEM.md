# 👤 Sistema de Identificación de Usuarios

## 🎯 Objetivo

Permitir que cada usuario tenga su propia sesión personalizada, con memoria y contexto únicos, tanto en el frontend web como en la consola.

---

## 🔑 Cómo Funciona

### **Generación de ID de Usuario**

Cada usuario tiene un ID único con el formato:
```
nombre_hash8caracteres

Ejemplos:
- juan_a1b2c3d4
- maria_x9y8z7w6
- carlos_m5n4o3p2
```

**Componentes:**
- **Nombre**: El nombre que ingresa el usuario
- **Hash**: 8 caracteres únicos generados con MD5 del nombre + timestamp

---

## 🌐 Frontend Web (Streamlit)

### **Pantalla de Login**

Al abrir la aplicación web, verás:

```
┌─────────────────────────────────────────┐
│  🚗 Bienvenido a Kavak                 │
│  Identifícate para comenzar            │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  👤 Identificación de Usuario          │
│                                         │
│  [🔑 Iniciar Sesión] [✨ Nuevo Usuario]│
│                                         │
│  ┌─ Iniciar Sesión ─────────────────┐ │
│  │ ID de Usuario:                   │ │
│  │ [juan_a1b2c3d4____________]      │ │
│  │ [🚀 Continuar]                   │ │
│  └──────────────────────────────────┘ │
│                                         │
│  ┌─ Nuevo Usuario ───────────────────┐│
│  │ Tu Nombre:                        ││
│  │ [Juan Pérez_______________]      ││
│  │ [✨ Crear Usuario]               ││
│  └──────────────────────────────────┘│
└─────────────────────────────────────────┘
```

### **Opciones:**

#### **1. Iniciar Sesión (Usuario Existente)**
- Ingresa tu ID de usuario anterior
- Click en "Continuar"
- El sistema carga tu historial y memoria

#### **2. Nuevo Usuario**
- Ingresa tu nombre
- Click en "Crear Usuario"
- El sistema genera un ID único
- **IMPORTANTE**: Guarda tu ID para futuras sesiones

### **Información del Usuario en Sidebar**

Una vez identificado, verás en el sidebar:

```
┌──────────────────┐
│ 👤 Usuario Actual│
├──────────────────┤
│ Nombre           │
│ Juan             │
│                  │
│ ID de Usuario:   │
│ juan_a1b2c3d4    │
│                  │
│ [🚪 Cerrar Sesión]│
└──────────────────┘
```

### **Cerrar Sesión**

- Click en "🚪 Cerrar Sesión"
- Vuelve a la pantalla de login
- Puedes iniciar sesión con otro usuario

---

## 💻 Consola (Terminal)

### **Proceso de Identificación**

Al ejecutar `python main.py`:

```
============================================================
🚗 BIENVENIDO AL ASISTENTE VIRTUAL DE KAVAK 🚗
============================================================

============================================================
IDENTIFICACIÓN DE USUARIO
============================================================

1. ¿Eres un usuario nuevo o existente?
   [1] Usuario nuevo (crear ID)
   [2] Usuario existente (usar ID anterior)

Selecciona una opción (1 o 2): _
```

### **Opción 1: Usuario Nuevo**

```
Selecciona una opción (1 o 2): 1

Ingresa tu nombre: Juan Pérez

✅ Usuario creado exitosamente!
📝 Tu ID de usuario es: Juan_a1b2c3d4
⚠️  IMPORTANTE: Guarda este ID para futuras sesiones

Presiona Enter para continuar...
```

### **Opción 2: Usuario Existente**

```
Selecciona una opción (1 o 2): 2

Ingresa tu ID de usuario: Juan_a1b2c3d4

✅ Sesión iniciada para usuario: Juan_a1b2c3d4
```

---

## 🔄 Sincronización Frontend ↔ Backend

### **Flujo Completo:**

```
1. Usuario se identifica (web o consola)
   ↓
2. user_id se pasa a DatabaseManager
   ↓
3. DatabaseManager carga memoria del usuario
   ↓
4. MainAgent construye prompt con memoria personalizada
   ↓
5. Usuario chatea con contexto personalizado
   ↓
6. Feedback se guarda asociado al user_id
   ↓
7. Próxima sesión: memoria se recupera automáticamente
```

### **Ejemplo Práctico:**

**Sesión 1 (Usuario: juan_a1b2c3d4):**
```
Usuario: ¿Qué garantías tienen?
Bot: [Respuesta sobre garantías]
Usuario: 👍 (feedback positivo)
→ Sistema guarda: "Usuario preguntó sobre garantías"
```

**Sesión 2 (Mismo usuario: juan_a1b2c3d4):**
```
Usuario: ¿Y qué más incluye?
Bot: Además de la garantía mecánica que te mencioné antes...
     [El bot RECUERDA la conversación anterior]
```

**Sesión 1 (Usuario diferente: maria_x9y8z7w6):**
```
Usuario: ¿Qué más incluye?
Bot: ¿A qué te refieres? Puedo ayudarte con...
     [El bot NO tiene contexto de juan]
```

---

## 🗄️ Base de Datos

### **Tabla: user_memory**

```sql
CREATE TABLE user_memory (
    id INTEGER PRIMARY KEY,
    user_id TEXT NOT NULL,        -- Ej: "juan_a1b2c3d4"
    context TEXT NOT NULL          -- Ej: "Usuario preguntó sobre garantías"
);
```

### **Ejemplo de Datos:**

| id | user_id | context |
|----|---------|---------|
| 1 | juan_a1b2c3d4 | Usuario preguntó sobre garantías de autos |
| 2 | juan_a1b2c3d4 | Usuario interesado en financiamiento |
| 3 | maria_x9y8z7w6 | Usuario buscando Jetta azul 2020 |
| 4 | carlos_m5n4o3p2 | Usuario preguntó sobre venta de auto |

### **Consulta de Memoria:**

```python
# Backend automáticamente hace:
db_manager.get_user_memory("juan_a1b2c3d4")

# Retorna:
"""
HISTORIAL DE MEMORIA DEL USUARIO:
- Usuario preguntó sobre garantías de autos
- Usuario interesado en financiamiento
"""
```

---

## 🎯 Beneficios del Sistema

### **1. Personalización**
- Cada usuario tiene su propio contexto
- El bot recuerda conversaciones anteriores
- Respuestas más relevantes

### **2. Privacidad**
- Usuarios separados no ven datos de otros
- Cada sesión es independiente

### **3. Continuidad**
- Puedes cerrar y volver después
- Tu historial se mantiene
- Experiencia consistente

### **4. Métricas Precisas**
- Seguimiento por usuario
- Análisis de comportamiento individual
- Mejora personalizada

---

## 🔧 Implementación Técnica

### **Frontend (app.py):**

```python
# 1. Verificar si usuario está identificado
if st.session_state.user_id is None:
    # Mostrar pantalla de login
    user_id = render_login_screen()
    
    if user_id:
        st.session_state.user_id = user_id
        rebuild_system_prompt()  # Carga memoria del usuario
        st.rerun()
    
    return  # No mostrar chat hasta identificación

# 2. Usuario identificado - cargar su memoria
memory = db_manager.get_user_memory(st.session_state.user_id)
```

### **Backend (main.py):**

```python
# 1. Solicitar identificación
opcion = input("¿Usuario nuevo (1) o existente (2)? ")

if opcion == "1":
    nombre = input("Nombre: ")
    user_id = generar_id_unico(nombre)
else:
    user_id = input("ID de usuario: ")

# 2. Cargar memoria del usuario
memory = db_manager.get_user_memory(user_id)
```

### **Database (database.py):**

```python
def get_user_memory(self, user_id: str) -> str:
    """Obtiene TODA la memoria del usuario."""
    cursor.execute(
        'SELECT context FROM user_memory WHERE user_id = ?',
        (user_id,)
    )
    # Retorna memoria formateada
```

---

## 📊 Ejemplo de Flujo Completo

### **Día 1 - Usuario Nuevo:**

```
1. Abre app web
2. Click en "Nuevo Usuario"
3. Ingresa: "Juan Pérez"
4. Sistema genera: "Juan_a1b2c3d4"
5. Guarda ID en papel/archivo
6. Chatea sobre garantías
7. Da feedback 👍
8. Sistema guarda memoria
9. Cierra navegador
```

### **Día 2 - Usuario Regresa:**

```
1. Abre app web
2. Click en "Iniciar Sesión"
3. Ingresa: "Juan_a1b2c3d4"
4. Sistema carga memoria:
   - "Usuario preguntó sobre garantías"
5. Chatea sobre financiamiento
6. Bot recuerda contexto anterior
7. Da feedback 👎
8. Sistema aprende y mejora
```

### **Día 3 - Otro Usuario:**

```
1. Abre app web
2. Click en "Nuevo Usuario"
3. Ingresa: "María López"
4. Sistema genera: "María_x9y8z7w6"
5. Chatea desde cero
6. NO ve datos de Juan
7. Tiene su propia memoria
```

---

## 🚀 Comandos Rápidos

### **Frontend Web:**
```bash
streamlit run app.py
```

### **Consola:**
```bash
python main.py
```

### **Ver usuarios en BD:**
```bash
python
>>> from backend.utils.database import DatabaseManager
>>> db = DatabaseManager()
>>> stats = db.get_system_stats()
>>> print(f"Usuarios: {stats['total_users']}")
```

---

## ✅ Checklist de Funcionalidades

- ✅ Login en frontend web
- ✅ Registro de nuevos usuarios
- ✅ Generación de ID único
- ✅ Identificación en consola
- ✅ Sincronización user_id frontend ↔ backend
- ✅ Carga de memoria por usuario
- ✅ Guardado de memoria por usuario
- ✅ Separación de sesiones
- ✅ Botón de cerrar sesión
- ✅ Visualización de usuario actual
- ✅ Personalización de bienvenida

---

## 🎉 ¡Sistema Completo!

Ahora cada usuario tiene su propia identidad y contexto, tanto en web como en consola. El sistema es completamente funcional y sincronizado. 🚀
