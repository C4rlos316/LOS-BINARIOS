# 🎓 Sistema de Agentes Maestros

## 🎯 Concepto Central

El **MainAgent** es un estudiante que empieza sabiendo CASI NADA.

Los **OptimizerAgent** y **SummarizerAgent** son los MAESTROS que lo entrenan.

---

## 👶 MainAgent - El Estudiante

### **Conocimiento Inicial: MÍNIMO**

```python
PROMPT_BASE = """Eres un asistente virtual de Kavak.

Kavak es una plataforma de compra y venta de autos seminuevos.

Tu trabajo es ayudar a los usuarios con sus preguntas sobre autos.

Sé amigable y haz preguntas para entender mejor lo que necesitan."""
```

**Total: 5 líneas**

**Sabe:**
- ✅ Que es de Kavak
- ✅ Que Kavak vende/compra autos
- ✅ Que debe ser amigable
- ✅ Que debe hacer preguntas

**NO sabe:**
- ❌ Qué preguntas hacer
- ❌ Qué datos dar
- ❌ Cómo estructurar respuestas
- ❌ Información específica de Kavak
- ❌ Procesos, precios, garantías, nada

---

## 👨‍🏫 OptimizerAgent - El Maestro de Corrección

### **Rol: Corregir errores y enseñar**

Cuando el usuario da **👎 feedback negativo**:

### **PASO 1: Categorizar el Error**

```python
def categorize_error(question, answer):
    """
    Analiza QUÉ salió mal
    
    Categorías:
    - vago: Respuesta sin datos específicos
    - incompleto: Falta información
    - incorrecto: Datos erróneos
    - fuera_contexto: No responde la pregunta
    - general: Otro error
    """
```

**Ejemplo:**
```
Pregunta: "¿Tienen garantía?"
Respuesta: "Sí, tenemos garantía"
Categoría: "vago" (no da detalles)
```

### **PASO 2: Generar Regla Específica**

```python
def generate_rule(question, answer, error_category):
    """
    Crea una LECCIÓN específica para el MainAgent
    
    La regla debe:
    1. Ser ACCIONABLE (qué hacer)
    2. Incluir DATOS ESPECÍFICOS
    3. Aplicar a situaciones similares
    """
```

**Ejemplo de regla generada:**
```
REGLA: "Al hablar de garantías, SIEMPRE mencionar: 
duración (3 meses o 3,000 km), cobertura (motor, 
transmisión, sistema eléctrico), contacto (800-KAVAK-01)."
```

### **PASO 3: Validar la Regla**

```python
def validate_rule(rule_text, test_question):
    """
    Verifica que la regla REALMENTE mejore
    
    Proceso:
    1. Prueba respuesta SIN regla
    2. Prueba respuesta CON regla
    3. Compara ambas
    4. Score: 1.0 si mejora, 0.0 si no
    """
```

### **PASO 4: Guardar si es Buena**

```python
if validation_score >= 0.5:
    db_manager.save_rule(rule_text, error_category, validation_score)
    # MainAgent ahora tiene esta regla permanentemente
```

---

## 📚 SummarizerAgent - El Maestro de Memoria

### **Rol: Recordar y personalizar**

Cuando el usuario da **👍 feedback positivo**:

### **PASO 1: Analizar Conversación Completa**

```python
def summarize_conversation(chat_history):
    """
    Extrae TODA la información útil:
    
    1. Necesidad principal del usuario
    2. Preferencias específicas
    3. Contexto y situación
    4. Preguntas realizadas
    """
```

**Ejemplo de análisis:**
```
Conversación:
👤 "Quiero un auto para mi familia"
🤖 "¿Cuántas personas? ¿Presupuesto?"
👤 "Somos 5, tengo $350k"
🤖 "Te recomiendo SUVs..."
👍 Feedback positivo

Resumen generado:
"Usuario busca auto familiar para 5 personas. 
Presupuesto $350k. Interesado en SUVs. Primera 
compra de auto familiar. Está en etapa de exploración."
```

### **PASO 2: Guardar Memoria del Usuario**

```python
db_manager.save_user_memory(user_id, summary)
# Próxima sesión: MainAgent recordará esto
```

### **PASO 3: Personalización en Próxima Sesión**

```python
# Usuario regresa días después
memory = db_manager.get_user_memory(user_id)

# MainAgent recibe:
PROMPT_BASE + REGLAS + MEMORIA

# Ahora puede decir:
"¡Hola de nuevo! Veo que buscabas un SUV familiar 
para 5 personas con presupuesto de $350k. ¿Quieres 
que te muestre opciones?"
```

---

## 🔄 Ciclo Completo de Aprendizaje

### **Iteración 1: Sistema Virgen**

```
Estado Inicial:
- MainAgent: 5 líneas de prompt
- Reglas: 0
- Memoria: 0
- Madurez: 0/100

👤 Usuario: "Quiero un carro"

🤖 MainAgent (solo con prompt base):
"¡Hola! Claro, puedo ayudarte. ¿Qué tipo de auto buscas?"

👎 Usuario: Feedback negativo (muy básico)

👨‍🏫 OptimizerAgent ACTÚA:
1. Categoriza: "vago"
2. Genera regla: "Cuando pregunten por autos, SIEMPRE 
   preguntar: ¿Tipo (sedán/SUV/hatchback)? ¿Marca? 
   ¿Presupuesto? ¿Uso (ciudad/carretera/familiar)?"
3. Valida: Score 1.0 (mejora)
4. Guarda en BD

Estado Final:
- Reglas: 1
- Madurez: 10/100
```

### **Iteración 2: Sistema con 1 Regla**

```
Estado Inicial:
- MainAgent: 5 líneas + 1 REGLA
- Reglas: 1
- Madurez: 10/100

👤 Usuario: "Quiero un carro"

🤖 MainAgent (con REGLA 1):
"¡Perfecto! Para ayudarte mejor:
- ¿Qué tipo de vehículo? (sedán, SUV, hatchback)
- ¿Tienes marca preferida?
- ¿Cuál es tu presupuesto?
- ¿Lo usarás en ciudad o carretera?"

👍 Usuario: Feedback positivo (¡mucho mejor!)

📚 SummarizerAgent ACTÚA:
1. Analiza conversación
2. Extrae: "Usuario busca auto, necesita orientación 
   sobre tipo de vehículo y presupuesto"
3. Guarda memoria asociada al user_id

Estado Final:
- Reglas: 1
- Memorias: 1
- Madurez: 12/100
```

### **Iteración 3: Nueva Pregunta**

```
Estado Inicial:
- MainAgent: 5 líneas + 1 REGLA
- Reglas: 1
- Madurez: 12/100

👤 Usuario: "¿Tienen garantía?"

🤖 MainAgent (sin regla sobre garantías):
"Sí, ofrecemos garantía en nuestros autos. 
¿Te interesa saber más?"

👎 Usuario: Feedback negativo (no da datos)

👨‍🏫 OptimizerAgent ACTÚA:
1. Categoriza: "incompleto"
2. Genera regla: "Al hablar de garantías, SIEMPRE 
   mencionar: duración (3 meses o 3,000 km), cobertura 
   (motor, transmisión, eléctrico), contacto (800-KAVAK-01)"
3. Valida: Score 1.0
4. Guarda en BD

Estado Final:
- Reglas: 2
- Madurez: 22/100
```

### **Iteración 4: Misma Pregunta**

```
Estado Inicial:
- MainAgent: 5 líneas + 2 REGLAS
- Reglas: 2
- Madurez: 22/100

👤 Usuario: "¿Qué garantía tienen?"

🤖 MainAgent (con REGLA 2):
"Tenemos garantía mecánica de 3 meses o 3,000 km 
(lo que ocurra primero). Cubre motor, transmisión 
y sistema eléctrico. Si necesitas usarla, llama al 
800-KAVAK-01. ¿Quieres saber qué componentes 
específicos cubre?"

👍 Usuario: Feedback positivo (¡excelente!)

📚 SummarizerAgent ACTÚA:
1. Analiza conversación
2. Extrae: "Usuario preguntó por garantías, 
   interesado en cobertura mecánica"
3. Guarda memoria

Estado Final:
- Reglas: 2
- Memorias: 2
- Madurez: 24/100
```

### **Iteración 10: Sistema Entrenado**

```
Estado:
- MainAgent: 5 líneas + 10 REGLAS
- Reglas: 10
- Memorias: 8
- Madurez: 60/100

👤 Usuario: "Quiero un Jetta"

🤖 MainAgent (con 10 reglas aprendidas):
"¡Excelente elección! El Jetta es muy popular. 
Para recomendarte el mejor:

1. ¿Qué año prefieres? (Tenemos 2015-2024)
2. ¿Presupuesto? (Jetta: $180k-$450k aprox)
3. ¿Transmisión manual o automática?
4. ¿Necesitas financiamiento?

Todos pasan inspección 240 puntos e incluyen 
garantía 3 meses/3,000 km."

👍 Usuario: ¡Perfecto!

Estado Final:
- Madurez: 62/100
```

---

## 📊 Comparación: Antes vs Ahora

### **❌ Sistema Anterior (Prompt Completo)**

```
MainAgent: 142 líneas
OptimizerAgent: Genera reglas genéricas
SummarizerAgent: Resumen simple

Problema:
- MainAgent ya sabe todo
- Poco espacio para aprender
- Reglas redundantes
- No hay progresión real
```

### **✅ Sistema Nuevo (Agentes Maestros)**

```
MainAgent: 5 líneas (estudiante)
OptimizerAgent: Maestro de corrección (enseña QUÉ hacer)
SummarizerAgent: Maestro de memoria (personaliza)

Ventajas:
- MainAgent empieza casi vacío
- Aprende de CADA error
- Progresión visible (0→100)
- Personalización real por usuario
```

---

## 🎯 Roles Claros

### **MainAgent (Estudiante)**
- ✅ Responde preguntas
- ✅ Aplica reglas aprendidas
- ✅ Usa memoria de usuarios
- ❌ NO genera reglas
- ❌ NO decide qué aprender

### **OptimizerAgent (Maestro de Corrección)**
- ✅ Detecta errores
- ✅ Categoriza problemas
- ✅ Genera lecciones (reglas)
- ✅ Valida que funcionen
- ✅ Decide qué guardar

### **SummarizerAgent (Maestro de Memoria)**
- ✅ Analiza conversaciones
- ✅ Extrae información clave
- ✅ Crea perfiles de usuario
- ✅ Personaliza experiencia

---

## 🎬 Demo Impactante

### **Script Sugerido:**

```
"Nuestro bot NO es un experto desde el inicio.

Es un ESTUDIANTE que empieza sabiendo CASI NADA.

[Mostrar prompt: 5 líneas]

Pero tiene DOS MAESTROS:

1. OptimizerAgent - Le enseña cuando se equivoca
2. SummarizerAgent - Le ayuda a recordar usuarios

Miren...

[Pregunta vaga]
Bot responde básico.

[Feedback negativo 👎]
OptimizerAgent ANALIZA el error...
GENERA una lección específica...
VALIDA que funcione...
Y la GUARDA.

[Misma pregunta]
Bot responde MEJOR.

¿Por qué? Porque APRENDIÓ.

Cada error = Nueva lección
Cada feedback positivo = Nueva memoria
Cada interacción = Sistema más inteligente

En 30 días: 20+ lecciones aprendidas
En 90 días: Experto completo

TODO automático.
TODO por feedback de usuarios.
CERO programación manual.

Esto es aprendizaje REAL."
```

---

## 📈 Evolución del Conocimiento

### **Día 1:**
```
MainAgent:
  Prompt base: 5 líneas
  Reglas: 0
  Total conocimiento: 5 líneas
```

### **Día 7:**
```
MainAgent:
  Prompt base: 5 líneas
  Reglas: 5 (30 líneas)
  Total conocimiento: 35 líneas
```

### **Día 30:**
```
MainAgent:
  Prompt base: 5 líneas
  Reglas: 15 (90 líneas)
  Total conocimiento: 95 líneas
```

### **Día 90:**
```
MainAgent:
  Prompt base: 5 líneas
  Reglas: 25 (150 líneas)
  Total conocimiento: 155 líneas
```

**Pero con la diferencia de que TODO ese conocimiento fue APRENDIDO, no programado.**

---

## ✅ Resumen

**Sistema de 3 Agentes:**

1. **MainAgent (Estudiante)**
   - Empieza con 5 líneas
   - Aprende de sus maestros
   - Aplica lecciones aprendidas

2. **OptimizerAgent (Maestro de Corrección)**
   - Detecta errores
   - Genera lecciones específicas
   - Valida efectividad
   - Entrena al MainAgent

3. **SummarizerAgent (Maestro de Memoria)**
   - Analiza conversaciones
   - Extrae información clave
   - Personaliza experiencia
   - Crea memoria de usuarios

**Resultado:**
- ✅ Aprendizaje real y progresivo
- ✅ Cada agente tiene rol claro
- ✅ Sistema auto-mejorable
- ✅ Demostración impactante

**¡Los maestros entrenan al estudiante!** 🎓🤖
