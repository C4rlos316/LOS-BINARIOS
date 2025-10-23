import os
import sqlite3
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage
import httpx


# Configuración inicial
load_dotenv()

# Limpiar variables de proxy del entorno para evitar conflictos
os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)
os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None)


# Funciones de Base de Datos (Lectura)
def get_db_connection():
    """Helper para obtener conexión a la base de datos"""
    return sqlite3.connect('kavak_memory.db')


def get_all_rules():
    """
    Obtiene todas las reglas de la tabla prompt_rules.
    Retorna un string con todas las reglas unidas por saltos de línea.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT rule_text FROM prompt_rules')
    results = cursor.fetchall()
    
    conn.close()
    
    if results:
        # Unir todas las reglas con saltos de línea
        return '\n'.join([row[0] for row in results])
    return ''


def get_user_memory(user_id):
    """
    Obtiene el recuerdo más reciente del usuario.
    Retorna un string formateado con el contexto o string vacío si no hay memoria.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        'SELECT context FROM user_memory WHERE user_id = ? ORDER BY id DESC LIMIT 1',
        (user_id,)
    )
    result = cursor.fetchone()
    
    conn.close()
    
    if result:
        return f"Contexto de memoria de este usuario: {result[0]}"
    return ''


def save_user_memory(user_id, chat_history_list, llm_instance):
    """
    Agente Resumidor: Genera y guarda un resumen de la conversación en user_memory.
    Usa la instancia llm_instance ya configurada para evitar errores de proxy.
    """
    MEMORY_PROMPT = "Eres un agente resumidor. Basado en esta conversación, extrae el interés clave, problema o intención del usuario en una sola frase concisa para usarla como memoria a futuro."
    
    # Crear lista de mensajes para el resumidor
    messages_for_summary = [SystemMessage(content=MEMORY_PROMPT)] + chat_history_list
    
    # Llamar al LLM usando la instancia configurada
    response = llm_instance.invoke(messages_for_summary)
    summary_text = response.content
    
    # Guardar en la base de datos
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        'INSERT INTO user_memory (user_id, context) VALUES (?, ?)',
        (user_id, summary_text)
    )
    
    conn.commit()
    conn.close()
    
    print("\n[Sistema: 👍 Memoria guardada exitosamente.]")


def optimize_prompt_rule(chat_history_list, llm_instance):
    """
    Agente Optimizador: Genera y guarda una nueva regla de prompt en prompt_rules.
    Usa la instancia llm_instance ya configurada para evitar errores de proxy.
    """
    # Extraer la última pregunta y respuesta
    last_human_message = None
    last_ai_message = None
    
    # Buscar desde el final hacia atrás
    for msg in reversed(chat_history_list):
        if isinstance(msg, AIMessage) and last_ai_message is None:
            last_ai_message = msg.content
        elif isinstance(msg, HumanMessage) and last_human_message is None:
            last_human_message = msg.content
        
        if last_human_message and last_ai_message:
            break
    
    if not last_human_message or not last_ai_message:
        print("\n[Sistema: ⚠️  No se pudo extraer la conversación para optimizar.]")
        return
    
    # Definir el prompt del optimizador
    OPTIMIZER_PROMPT = f"""Eres un 'Optimizador de Prompts' experto. La siguiente respuesta del bot a la pregunta del usuario fue marcada como 'No Útil'.

Tu tarea es analizar el fallo y generar una 'REGLA:' corta y específica para el prompt del sistema que ayude a bots futuros a evitar este error.
La regla debe ser accionable y clara.

Ejemplo de Regla: 'REGLA: Si el usuario pregunta por garantía, siempre mencionar la garantía mecánica de 3 meses.'

---
Pregunta del Usuario que falló: {last_human_message}
Respuesta del Bot que falló: {last_ai_message}
---

Genera la nueva REGLA:"""
    
    # Llamar al LLM usando la instancia configurada
    response = llm_instance.invoke([HumanMessage(content=OPTIMIZER_PROMPT)])
    new_rule_text = response.content
    
    # Guardar en la base de datos
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        'INSERT INTO prompt_rules (rule_text) VALUES (?)',
        (new_rule_text,)
    )
    
    conn.commit()
    conn.close()
    
    print("\n[Sistema: 👎 Nueva regla aprendida y guardada.]")


def build_system_prompt(user_id):
    """
    Construye el prompt del sistema combinando:
    - PROMPT_BASE (instrucciones base)
    - Reglas de la BD
    - Memoria del usuario
    """
    PROMPT_BASE = """Eres un asistente virtual de Kavak, la plataforma líder de compra y venta de autos seminuevos en Latinoamérica.

Tu objetivo es ayudar a los usuarios con información sobre nuestros servicios y resolver sus dudas de manera amigable y profesional.

TEMAS PRINCIPALES QUE MANEJAS:

1. **Compra de Autos**: Ayuda a los usuarios a encontrar el auto ideal, explica el proceso de compra, financiamiento disponible, garantías y beneficios de comprar en Kavak.

2. **Venta de Autos**: Guía a los usuarios que quieren vender su auto, explica cómo funciona la valuación, el proceso de inspección, y los tiempos de pago.

3. **Financiamiento**: Informa sobre las opciones de crédito, tasas de interés, plazos disponibles, requisitos y proceso de aprobación.

4. **Garantía y Servicio Post-Venta**: Explica la garantía mecánica de Kavak, los servicios de mantenimiento, y cómo hacer válida la garantía.

5. **Proceso de Inspección**: Detalla el riguroso proceso de certificación de 240 puntos que pasa cada auto antes de ser vendido.

INSTRUCCIONES:
- Sé amigable, claro y conciso
- Si no sabes algo, admítelo y ofrece conectar al usuario con un asesor
- Usa un tono profesional pero cercano
- Prioriza la experiencia del usuario"""

    # Obtener reglas y memoria
    rules = get_all_rules()
    memory = get_user_memory(user_id)
    
    # Combinar todo en el prompt final
    final_prompt = PROMPT_BASE
    
    if rules:
        final_prompt += f"\n\nREGLAS ADICIONALES:\n{rules}"
    
    if memory:
        final_prompt += f"\n\n{memory}"
    
    return final_prompt


def main():
    """
    Bucle principal del chatbot en consola.
    """
    print("=" * 60)
    print("🚗 BIENVENIDO AL ASISTENTE VIRTUAL DE KAVAK 🚗")
    print("=" * 60)
    print("\nEscribe 'salir' en cualquier momento para terminar la conversación.\n")
    
    # Solicitar user_id (simulación de login)
    user_id = input("Por favor, ingresa tu ID de usuario: ").strip()
    
    if not user_id:
        print("❌ Error: Debes ingresar un ID de usuario válido.")
        return
    
    print(f"\n✅ Sesión iniciada para usuario: {user_id}")
    print("\nCargando asistente...")
    
    # Configurar clientes HTTP (síncrono y asíncrono) con timeout personalizado
    sync_client = httpx.Client(timeout=30.0)
    async_client = httpx.AsyncClient(timeout=30.0)
    
    # Inicializar el LLM con clientes HTTP personalizados
    llm = ChatOpenAI(
        model="gpt-3.5-turbo", 
        temperature=0.7,
        http_client=sync_client,
        http_async_client=async_client
    )
    
    # Construir el prompt del sistema
    system_prompt = build_system_prompt(user_id)
    
    # Inicializar historial de chat
    chat_history = [SystemMessage(content=system_prompt)]
    
    print("\n" + "=" * 60)
    print("Puedes empezar a chatear con el asistente de Kavak")
    print("=" * 60)
    
    # Bucle principal de conversación
    while True:
        # Obtener input del usuario
        user_input = input("\n🧑 Tú: ").strip()
        
        # Verificar comando de salida
        if user_input.lower() == 'salir':
            print("\n👋 ¡Gracias por usar el asistente de Kavak! Hasta pronto.")
            break
        
        # Validar que el input no esté vacío
        if not user_input:
            print("⚠️  Por favor, escribe algo.")
            continue
        
        # Añadir mensaje del usuario al historial
        chat_history.append(HumanMessage(content=user_input))
        
        # Mostrar mensaje de espera
        print("\n🤖 Kavak pensando...")
        
        try:
            # Llamar a la IA
            response = llm.invoke(chat_history)
            ai_response_content = response.content
            
            # Mostrar respuesta
            print(f"\n🚗 Kavak: {ai_response_content}")
            
            # Añadir respuesta del bot al historial para mantener contexto
            chat_history.append(AIMessage(content=ai_response_content))
            
            # Sistema de feedback
            print("\n¿Esta respuesta fue útil? ( 👍 / 👎 / 'siguiente' para continuar )")
            feedback = input("Tu feedback: ").strip().lower()
            
            if feedback == '👍':
                save_user_memory(user_id, chat_history, llm)
            elif feedback == '👎':
                optimize_prompt_rule(chat_history, llm)
            elif feedback == 'siguiente' or feedback == '':
                pass  # Continuar sin hacer nada
            else:
                print("[Sistema: Feedback no reconocido, continuando...]")
            
        except Exception as e:
            print(f"\n❌ Error al comunicarse con la IA: {str(e)}")
            print("Por favor, verifica tu configuración de API key en el archivo .env")
            break


if __name__ == "__main__":
    main()
