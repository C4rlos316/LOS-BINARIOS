# 🎨 Guía del Frontend Web - Kavak Chatbot

## 🚀 Cómo Ejecutar la Aplicación Web

### **Opción 1: Comando Simple**

```bash
streamlit run app.py
```

### **Opción 2: Con Puerto Específico**

```bash
streamlit run app.py --server.port 8501
```

La aplicación se abrirá automáticamente en tu navegador en:
```
http://localhost:8501
```

---

## 🎨 Características del Diseño

### **Colores de Kavak**
- 🟠 **Naranja Principal**: `#FF6B35` - Color corporativo de Kavak
- 🔵 **Azul Oscuro**: `#0F3460` - Para mensajes del usuario
- ⚫ **Negro Suave**: `#1A1A2E` - Textos principales
- ⚪ **Gris Claro**: `#F7F7F7` - Fondo general
- 🟢 **Verde**: `#16DB93` - Feedback positivo

### **Elementos Visuales**

#### **1. Header Moderno**
- Gradiente naranja vibrante
- Sombras suaves
- Título grande y legible
- Subtítulo descriptivo

#### **2. Chat Burbujas**
- **Usuario**: Burbujas azules a la derecha
- **Bot**: Burbujas naranjas a la izquierda
- Animaciones de entrada suaves
- Sombras para profundidad

#### **3. Botones de Feedback**
- 👍 Pulgar arriba (respuesta útil)
- 👎 Pulgar abajo (respuesta no útil)
- Centrados debajo de cada respuesta
- Hover con efecto de escala

#### **4. Sidebar Informativo**
- Métricas en tiempo real
- Nivel de madurez del sistema
- Información de uso
- Badges de estado

---

## 🎯 Funcionalidades

### **1. Chat Interactivo**
```
Usuario escribe → Bot responde → Usuario da feedback
```

### **2. Feedback con Pulgares**

**Pulgar Arriba (👍):**
- Guarda la conversación como memoria
- El sistema recuerda el contexto del usuario
- Mensaje de confirmación verde

**Pulgar Abajo (👎):**
- Activa el Agente Optimizador
- Categoriza el error
- Genera y valida una nueva regla
- Actualiza el sistema automáticamente
- Mensaje de confirmación naranja

### **3. Métricas en Tiempo Real**

En el sidebar verás:
- 🧠 **Reglas Aprendidas**: Total de reglas generadas
- 👥 **Usuarios Activos**: Usuarios únicos
- 💾 **Memorias Guardadas**: Contextos guardados
- 🎯 **Nivel de Madurez**: 0-100 con barra de progreso

### **4. Mensaje de Bienvenida**

Al iniciar, muestra:
- Saludo personalizado
- Iconos de servicios (🚗💰💳🛡️)
- Descripción de capacidades
- Invitación a comenzar

---

## 📱 Estructura de la UI

```
┌─────────────────────────────────────────────────────────┐
│  🚗 Asistente Virtual de Kavak                         │
│  Tu compañero inteligente para comprar y vender autos  │
└─────────────────────────────────────────────────────────┘

┌──────────────┐  ┌────────────────────────────────────┐
│              │  │                                    │
│  SIDEBAR     │  │  ÁREA DE CHAT                     │
│              │  │                                    │
│  📊 Métricas │  │  [Mensaje Usuario]    👤          │
│  🧠 Reglas:3 │  │                                    │
│  👥 Users: 2 │  │  🚗 [Mensaje Bot]                 │
│  💾 Mems: 4  │  │     👍 👎                         │
│              │  │                                    │
│  🎯 Madurez  │  │  [Mensaje Usuario]    👤          │
│  ████░░ 38%  │  │                                    │
│              │  │  🚗 [Mensaje Bot]                 │
│  ℹ️ Info     │  │     👍 👎                         │
│              │  │                                    │
└──────────────┘  └────────────────────────────────────┘

                  ┌────────────────────────────────────┐
                  │ [Escribe tu pregunta...] [Enviar]│
                  └────────────────────────────────────┘
```

---

## 🎨 Personalización de Estilos

Los estilos están en `frontend/ui/styles.py`:

```python
# Cambiar colores
KAVAK_ORANGE = "#FF6B35"  # Color principal
KAVAK_DARK = "#1A1A2E"    # Texto oscuro
KAVAK_BLUE = "#0F3460"    # Mensajes usuario

# Modificar en get_custom_css()
```

---

## 🔧 Componentes Reutilizables

Ubicados en `frontend/ui/components.py`:

### **Funciones Disponibles:**

```python
render_header()                    # Header principal
render_user_message(text)          # Burbuja de usuario
render_bot_message(text)           # Burbuja de bot
render_feedback_buttons(index)     # Botones 👍👎
render_metrics_sidebar(stats)      # Métricas en sidebar
render_info_sidebar()              # Info adicional
render_welcome_message()           # Mensaje inicial
render_thinking_animation()        # Animación de carga
```

---

## 🎯 Flujo de Usuario

### **Escenario 1: Pregunta Exitosa**

```
1. Usuario escribe: "¿Qué garantías tienen?"
2. Bot responde con detalles específicos
3. Usuario da 👍
4. Sistema guarda memoria
5. Mensaje: "✅ Memoria guardada"
```

### **Escenario 2: Respuesta Mejorable**

```
1. Usuario escribe: "¿Cuánto cuesta un auto?"
2. Bot responde vagamente
3. Usuario da 👎
4. Sistema analiza error
5. Genera nueva regla
6. Valida regla
7. Guarda en BD
8. Mensaje: "✅ Sistema aprendió nueva regla"
9. Próximas respuestas serán mejores
```

---

## 🎨 Animaciones

### **Entrada de Mensajes**
- Usuario: Desliza desde la derecha
- Bot: Desliza desde la izquierda
- Duración: 0.3s
- Efecto: ease-out

### **Hover en Botones**
- Escala: 1.05x
- Transición: 0.3s
- Sombra aumentada

### **Pensando...**
- Puntos suspensivos parpadeantes
- Animación infinita

---

## 📊 Métricas Visuales

### **Nivel de Madurez**

```
0-19:   🆕 Sistema Nuevo
20-49:  🌱 Sistema Inicial
50-79:  📈 En Crecimiento
80-100: 🏆 Sistema Maduro
```

### **Cálculo:**
```
Madurez = (Reglas × 10) + (Memorias × 2)
Máximo: 100
```

---

## 🚀 Comandos Útiles

### **Iniciar aplicación:**
```bash
streamlit run app.py
```

### **Limpiar caché:**
```bash
streamlit cache clear
```

### **Ver en red local:**
```bash
streamlit run app.py --server.address 0.0.0.0
```

### **Modo desarrollo (auto-reload):**
```bash
streamlit run app.py --server.runOnSave true
```

---

## 🎯 Mejores Prácticas de UX

### **✅ Implementadas:**

1. **Feedback Inmediato**
   - Mensajes de confirmación
   - Animaciones suaves
   - Estados visuales claros

2. **Navegación Intuitiva**
   - Input siempre visible
   - Botón de enviar destacado
   - Limpiar conversación fácil

3. **Información Clara**
   - Métricas en tiempo real
   - Guía de uso en sidebar
   - Mensajes de bienvenida

4. **Diseño Responsivo**
   - Columnas adaptables
   - Texto legible
   - Espaciado adecuado

5. **Accesibilidad**
   - Contraste alto
   - Fuentes legibles
   - Tooltips en botones

---

## 🐛 Troubleshooting

### **Error: "ModuleNotFoundError: No module named 'streamlit'"**
```bash
pip install streamlit
```

### **Puerto ya en uso:**
```bash
streamlit run app.py --server.port 8502
```

### **Estilos no se aplican:**
1. Limpiar caché: `streamlit cache clear`
2. Recargar página: `Ctrl + R`

### **BD no se crea:**
- El sistema crea la BD automáticamente
- Verifica que `backend/utils/database.py` esté correcto

---

## 📞 Soporte

Para problemas o preguntas:
- Revisa `ESTRUCTURA.md` para arquitectura
- Revisa `README_METRICAS.md` para métricas
- Contacta al equipo **LOS BINARIOS**

---

## 🎉 ¡Listo para Usar!

```bash
streamlit run app.py
```

**Tu chatbot moderno, colorido e intuitivo está listo.** 🚀
