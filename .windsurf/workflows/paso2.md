---
description: 
auto_execution_mode: 3
---

# (Step 2: Agentes de Auto-Mejora)

**Asistente:** Actúa como mi Programador Experto en Python. Vamos a modificar `console_agent.py` (nuestro "Step 1") para implementar el "Step 2".

**Objetivo:** Integrar el ciclo de feedback (👍/👎) en el bucle principal. Crearemos dos nuevas funciones (agentes) que se llamarán con el feedback del usuario para *escribir* en la base de datos `kavak_memory.db`.

**Reglas de Codificación (¡MUY IMPORTANTE!):**
1.  **Anti-Proxy:** El `llm` principal ya está configurado con clientes `httpx` personalizados. Las nuevas funciones de agente (Resumidor y Optimizador) **deben** recibir esta instancia `llm` ya configurada para evitar errores de proxy.
2.  **Stack:** Sigue usando `langchain==0.3.7`, `openai==1.54.0` y `sqlite3`.

---

### Instrucciones del "Step 2":

Modifica el archivo `console_agent.py` existente.

#### 1. Modificar Archivo: `console_agent.py`

**Instrucciones:**
* **Conservar Imports:** Mantén todos los imports existentes (`os`, `sqlite3`, `dotenv`, `langchain`, `httpx`).
* **Conservar Configuración Anti-Proxy:** Mantén intacta la limpieza de variables de entorno (`os.environ.pop...`).
* **Conservar Funciones de Lectura:** Mantén intactas las funciones `get_db_connection()`, `get_all_rules()`, `get_user_memory()` y `build_system_prompt()`.

* **Nueva Función: `save_user_memory(user_id, chat_history_list, llm_instance)` (El Agente Resumidor)**
    * **Objetivo:** Genera y guarda un resumen de la conversación en `user_memory`.
    * **Instrucciones:**
        * Define la función para que acepte `user_id`, `chat_history_list` (la lista de mensajes) y `llm_instance` (el LLM ya configurado).
        * Define el `MEMORY_PROMPT`: `"Eres un agente resumidor. Basado en esta conversación, extrae el interés clave, problema o intención del usuario en una sola frase concisa para usarla como memoria a futuro."`
        * Crea una lista de mensajes para el "Resumidor" que combine el `MEMORY_PROMPT` con el historial de chat (`chat_history_list`).
        * **IMPORTANTE:** Llama al LLM usando la instancia pasada: `response = llm_instance.invoke(mensajes_para_resumen)`.
        * Obtén el resumen: `summary_text = response.content`.
        * Conéctate a la BD (usa `get_db_connection()`).
        * Ejecuta `INSERT INTO user_memory (user_id, context) VALUES (?, ?)`, pasando `(user_id, summary_text)`.
        * Haz `conn.commit()` y `conn.close()`.
        * Imprime un mensaje: `print("\n[Sistema: 👍 Memoria guardada exitosamente.]")`.

* **Nueva Función: `optimize_prompt_rule(chat_history_list, llm_instance)` (El Agente Optimizador)**
    * **Objetivo:** Genera y guarda una nueva regla de prompt en `prompt_rules`.
    * **Instrucciones:**
        * Define la función para que acepte `chat_history_list` y `llm_instance`.
        * Extrae la última pregunta (el último `HumanMessage`) y la última respuesta (el último `AIMessage`) del `chat_history_list`.
        * Define el `OPTIMIZER_PROMPT` (un string largo):
            ```
            Eres un 'Optimizador de Prompts' experto. La siguiente respuesta del bot a la pregunta del usuario fue marcada como 'No Útil'.
            
            Tu tarea es analizar el fallo y generar una 'REGLA:' corta y específica para el prompt del sistema que ayude a bots futuros a evitar este error.
            La regla debe ser accionable y clara.
            
            Ejemplo de Regla: 'REGLA: Si el usuario pregunta por garantía, siempre mencionar la garantía mecánica de 3 meses.'
            
            ---
            Pregunta del Usuario que falló: {pregunta_usuario}
            Respuesta del Bot que falló: {respuesta_bot}
            ---
            
            Genera la nueva REGLA:
            ```
        * Formatea el `OPTIMIZER_PROMPT` con la pregunta y respuesta extraídas.
        * **IMPORTANTE:** Llama al LLM: `response = llm_instance.invoke([HumanMessage(content=prompt_formateado)])`.
        * Obtén la nueva regla: `new_rule_text = response.content`.
        * Conéctate a la BD (usa `get_db_connection()`).
        * Ejecuta `INSERT INTO prompt_rules (rule_text) VALUES (?)`, pasando `(new_rule_text,)`.
        * Haz `conn.commit()` y `conn.close()`.
        * Imprime un mensaje: `print("\n[Sistema: 👎 Nueva regla aprendida y guardada.]")`.

* **Modificar Función `main()` (El Bucle Principal):**
    * **Conservar Configuración:** Mantén toda la configuración inicial dentro de `main()` (petición de `user_id`, clientes `httpx`, inicialización de `llm`, `build_system_prompt`, etc.).
    * **Modificar Bucle `while True`:**
        * Localiza el final del bloque `try...except`, justo después de `chat_history.append(AIMessage(content=ai_response_content))`.
        * **Inmediatamente después**, inserta un nuevo **bucle de feedback**:
        * Imprime en consola: `print("\n¿Esta respuesta fue útil? ( 👍 / 👎 / 'siguiente' para continuar )")`
        * Captura el feedback: `feedback = input("Tu feedback: ").strip().lower()`
        * Usa un `if/elif/else`:
            * `if feedback == '👍'`:
                * Llama a `save_user_memory(user_id, chat_history, llm)`
            * `elif feedback == '👎'`:
                * Llama a `optimize_prompt_rule(chat_history, llm)`
            * `elif feedback == 'siguiente' or feedback == '':`
                * `pass` (simplemente continúa)
            * `else`:
                * `print("[Sistema: Feedback no reconocido, continuando...]")`
        * **IMPORTANTE:** Este bloque de feedback debe estar *dentro* del `while True` principal, pero *fuera* del bloque `try...except`.

---

**Instrucciones de Ejecución (Para el Usuario Final):**

* El usuario debe ejecutar la aplicación con `python console_agent.py`.

**Resultado Esperado:**
La aplicación de consola `console_agent.py` ahora funciona como un ciclo completo de auto-mejora:
1.  El usuario (ej. "user_123") inicia el chat.
2.  El bot usa el prompt V1 (base) porque la BD está vacía.
3.  El usuario pregunta: "¿Qué garantías tienen?"
4.  El bot da una respuesta vaga: "Tenemos garantías en nuestros autos."
5.  El sistema pregunta: `¿Esta respuesta fue útil? ( 👍 / 👎 / 'siguiente' para continuar )`
6.  El usuario escribe: `👎`
7.  El "Agente Optimizador" se activa, llama a OpenAI y genera una regla.
8.  La consola imprime: `[Sistema: 👎 Nueva regla aprendida y guardada.]`.
9.  El usuario pregunta: "¿Qué Jettas tienes?"
10. El bot responde: "Tenemos varios Jettas. ¿Te interesa algún año o color?"
11. El sistema pregunta por feedback.
12. El usuario escribe: `👍`
13. El "Agente Resumidor" se activa y genera un resumen (ej. "Usuario está buscando Jettas.").
14. La consola imprime: `[Sistema: 👍 Memoria guardada exitosamente.]`.
15. **PRUEBA FINAL:** El usuario cierra el programa (`salir`) y lo **vuelve a ejecutar** con el mismo `user_id` ("user_123").
16. Al iniciar, `build_system_prompt` ahora carga la regla y la memoria.
17. El usuario pregunta: "¿Qué garantías tienen?"
18. El bot (ahora "Run 2") da la respuesta mejorada: "¡Claro! Tenemos una garantía mecánica de 3 meses..."