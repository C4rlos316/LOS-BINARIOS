---
description: 
auto_execution_mode: 3
---

# Step 1: Agente de Consola "Run 1"

**Asistente:** Actúa como mi Programador Experto en Python. Vamos a construir el "Step 1" de nuestro proyecto del hackathon.

**Objetivo:** Crear la lógica base para nuestro "Agente Principal". Esto debe funcionar 100% en la consola. El agente debe ser capaz de leer de una base de datos SQLite (reglas y memoria), aunque esta base de datos esté vacía (este es el "Run 1").

**Stack Tecnológico (Estricto):**
* `openai==1.54.0`
* `langchain==0.3.7`
* `langchain-openai==0.2.5`
* `python-dotenv`
* `sqlite3` (nativo de Python)
* `os`

---

### Instrucciones del "Step 1":

Crea los siguientes dos archivos Python en la raíz del proyecto.

Trabaja solo en el entorno virtual ya creado y funcionando 

#### 1. Archivo: `database_setup.py` (El Prerrequisito)

**Objetivo:** Crear el archivo `kavak_memory.db` y las tablas necesarias. El agente principal fallará si este archivo no se ejecuta primero.

**Instrucciones:**
* Importa `sqlite3`.
* Crea una función `setup_database()`.
* Dentro de la función, conéctate a `kavak_memory.db` (esto creará el archivo).
* Usa `cursor.execute()` para crear dos tablas usando `CREATE TABLE IF NOT EXISTS`:
    1.  `user_memory` (Columnas: `id` INTEGER PRIMARY KEY AUTOINCREMENT, `user_id` TEXT NOT NULL, `context` TEXT NOT NULL).
    2.  `prompt_rules` (Columnas: `id` INTEGER PRIMARY KEY AUTOINCREMENT, `rule_text` TEXT NOT NULL).
* Asegúrate de hacer `conn.commit()` y `conn.close()`.
* Imprime un mensaje de éxito, como "Base de datos 'kavak_memory.db' configurada."
* Usa `if __name__ == "__main__":` para ejecutar `setup_database()`.

#### 2. Archivo: `console_agent.py` (El Agente Principal "Run 1")

**Objetivo:** El script principal que corre el chatbot en la terminal. Debe contener toda la lógica para construir un prompt dinámico leyendo de la BD.

**Instrucciones:**
* **Imports:** Importa `os`, `sqlite3`, `load_dotenv` (de `dotenv`), `ChatOpenAI` (de `langchain_openai`), y `SystemMessage`, `HumanMessage`, `AIMessage` (de `langchain.schema`).
* **Configuración Inicial:**
    * Llama a `load_dotenv()` para cargar el `.env` (asumimos que existe).
    * Inicializa el LLM: `llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)`.
* **Funciones de Base de Datos (Lectura):**
    * `get_db_connection()`: Una función helper que retorna `sqlite3.connect('kavak_memory.db')`.
    * `get_all_rules()`:
        * Se conecta a la BD.
        * Ejecuta `SELECT rule_text FROM prompt_rules`.
        * Obtiene todos los resultados (`fetchall()`).
        * Cierra la conexión.
        * Retorna un solo string con todas las reglas unidas por un salto de línea (`\n`). Si no hay reglas, debe retornar un string vacío.
    * `get_user_memory(user_id)`:
        * Recibe un `user_id`.
        * Se conecta a la BD.
        * Ejecuta `SELECT context FROM user_memory WHERE user_id = ? ORDER BY id DESC LIMIT 1` (para obtener solo el recuerdo más reciente).
        * Obtiene el resultado (`fetchone()`).
        * Cierra la conexión.
        * Si encuentra un recuerdo, retorna un string formateado (ej. `"Contexto de memoria de este usuario: [contexto]"`). Si no, retorna un string vacío.
* **Función del "Agente" (El Cerebro):**
    * `build_system_prompt(user_id)`:
        * Recibe el `user_id`.
        * Define el `PROMPT_BASE` (un string largo que contiene las instrucciones iniciales y los 5 temas de Kavak).
        * Llama a `get_all_rules()` y guarda el resultado.
        * Llama a `get_user_memory(user_id)` y guarda el resultado.
        * Combina `PROMPT_BASE`, las reglas y la memoria en un solo string final.
        * Retorna el string del prompt final.
* **Bucle Principal de Consola (`main()`):**
    * Crea una función `main()`.
    * Imprime un mensaje de bienvenida.
    * Pide al usuario un `user_id` con `input()` (para simular un login).
    * Llama a `build_system_prompt(user_id)` *una vez* al inicio y guarda el resultado.
    * Inicializa el historial de chat: `chat_history = [SystemMessage(content=...)]` con el prompt que acabas de construir.
    * Inicia un bucle `while True:`.
    * Pide el input del usuario: `user_input = input("\nTú: ")`.
    * Añade un `if user_input.lower() == 'salir': break`.
    * Añade el `HumanMessage(content=user_input)` al `chat_history`.
    * Imprime un mensaje de espera (ej. "Kavak pensando...").
    * Llama a la IA: `response = llm.invoke(chat_history)`.
    * Obtiene el contenido: `ai_response_content = response.content`.
    * Imprime la respuesta del bot: `print(f"\nKavak: {ai_response_content}")`.
    * **Importante:** Añade la respuesta del bot `AIMessage(content=ai_response_content)` al `chat_history` para que el bot mantenga el contexto de la conversación actual.
* **Punto de Entrada:**
    * Usa `if __name__ == "__main__":` para ejecutar `main()`.

---

**Instrucciones de Ejecución (Para el Usuario Final):**

Cuando completes este workflow, el usuario debe poder hacer lo siguiente en su terminal:
1.  Ejecutar `python database_setup.py` (solo una vez) para crear el archivo `kavak_memory.db`.
2.  Ejecutar `python console_agent.py` para iniciar el chat.

**Resultado Esperado:**
Un chatbot funcional en la terminal. Al iniciarlo, me pedirá un `user_id`. Chatearé con él y responderá usando el `PROMPT_BASE` (ya que la base de datos de reglas y memoria está vacía). El bot recordará el contexto *dentro* de la misma sesión de chat (gracias a `chat_history`), pero no recordará nada si cierro y vuelvo a abrir el programa (eso es correcto para "Run 1").