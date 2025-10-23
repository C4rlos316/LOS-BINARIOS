---
description: 
auto_execution_mode: 1
---

# (Step 3: Script de Evaluación CON Métricas)

**Asistente:** Actúa como mi Programador Experto en Python. Ya tengo `database_setup.py` y `console_agent.py` funcionando.

**Objetivo:** Crear un **NUEVO ARCHIVO** llamado `evaluation_test.py`. Este script **NO DEBE LIMPIAR** la base de datos. Su propósito es importar la lógica de `console_agent.py` para ejecutar una prueba controlada y **calcular automáticamente** la "Tasa de Resolución" y generar la "Comparación Pareada".

**Stack Tecnológico (Estricto):**
* `openai==1.54.0`
* `langchain==0.3.7`
* `langchain-openai==0.2.5`
* `python-dotenv`
* `sqlite3`
* `httpx`
* `os`

---

### Instrucciones del "Step 3":

Crea un **NUEVO ARCHIVO** llamado `evaluation_test.py`.

#### 1. Archivo: `evaluation_test.py`

**Instrucciones:**
* **Imports:**
    * Importa `sqlite3`, `os`, `httpx`.
    * Importa `load_dotenv` (de `dotenv`).
    * Importa `ChatOpenAI` (de `langchain_openai`).
    * Importa `SystemMessage`, `HumanMessage` (de `langchain.schema`).
    * **Importante (Importar tu lógica):** Importa la función de construcción de prompt de tu agente:
        ```python
        from console_agent import build_system_prompt
        ```
* **Configuración Inicial (Anti-Proxy y LLM):**
    * Llama a `load_dotenv()`.
    * **Copia la configuración Anti-Proxy:** Añade las líneas `os.environ.pop('HTTP_PROXY', None)`, etc., exactamente como en `console_agent.py`.
    * **Copia la configuración de Clientes:** Configura `sync_client = httpx.Client(timeout=30.0)` y `async_client = httpx.AsyncClient(timeout=30.0)`.
    * **Inicializa el LLM:** Inicializa `llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7, http_client=sync_client, http_async_client=async_client)`.
* **Variable `PROMPT_BASE_COPIADO`:**
    * **Copia y pega** la variable `PROMPT_BASE` *exacta* que tienes dentro de tu función `build_system_prompt` en `console_agent.py`. (El string largo que empieza con "Eres un asistente virtual experto de Kavak...").
* **Helper: `run_evaluation(...)`**
    * Define una función `run_evaluation(system_prompt_str, evaluation_questions, llm_instance)`.
    * Crea una lista vacía `results = []`.
    * Itera sobre cada `pregunta` en `evaluation_questions`:
        * Imprime `\nPreguntando: {pregunta}`.
        * Crea el historial para esta *única* pregunta (para aislar la prueba): `history_para_llm = [SystemMessage(content=system_prompt_str), HumanMessage(content=pregunta)]`.
        * Llama al LLM: `response = llm_instance.invoke(history_para_llm)`.
        * Guarda la respuesta: `ai_response = response.content`.
        * Añade `ai_response