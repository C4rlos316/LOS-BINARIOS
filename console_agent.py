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
    Obtiene TODA la memoria histórica del usuario (todas las conversaciones previas).
    Retorna un string formateado con todos los contextos acumulados.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        'SELECT context FROM user_memory WHERE user_id = ? ORDER BY id ASC',
        (user_id,)
    )
    results = cursor.fetchall()
    
    conn.close()
    
    if results:
        # Combinar todas las memorias en un solo contexto
        all_memories = '\n'.join([f"- {row[0]}" for row in results])
        return f"HISTORIAL DE MEMORIA DEL USUARIO:\n{all_memories}"
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
    
    print("\n[Sistema: ✓ Memoria guardada exitosamente. Esta información se recordará en futuras conversaciones.]")


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
    
    print("\n[Sistema: ✓ Nueva regla aprendida y guardada. El bot mejorará sus respuestas.]")


def build_system_prompt(user_id):
    """
    Construye el prompt del sistema combinando:
    - PROMPT_BASE (instrucciones base)
    - Reglas de la BD
    - Memoria del usuario
    """
    PROMPT_BASE = """Eres un asistente virtual experto de Kavak, la plataforma líder de compra y venta de autos seminuevos en Latinoamérica.

SIEMPRE proporciona información ESPECÍFICA, DETALLADA y con DATOS CONCRETOS. Nunca des respuestas vagas o genéricas.

INFORMACIÓN CORPORATIVA:
- Fundada en 2016 en México
- Presencia en 7 países: México, Argentina, Chile, Brasil, Colombia, Perú y Turquía
- Más de 20 centros de distribución (Hubs)
- Inventario de +10,000 autos disponibles
- +300,000 autos vendidos desde fundación

1. COMPRA DE AUTOS - DATOS ESPECÍFICOS:

INVENTARIO:
- Marcas: Nissan, VW, Chevrolet, Toyota, Honda, Mazda, Ford, Hyundai, KIA, Seat
- Modelos populares: Versa, Jetta, Aveo, Vento, Sentra, March, Corolla, Civic, Mazda 3
- Precios: $120,000 - $800,000 MXN
- Años: 2015-2022 típicamente
- Kilometraje: 30,000 - 120,000 km

PROCESO (7 PASOS):
1. Búsqueda online con filtros
2. Agenda prueba de manejo (sin compromiso)
3. Revisión del auto (inspección 240 puntos)
4. Simulación de crédito (respuesta en 5 min)
5. Apartado con $5,000 MXN (reembolsable en 7 días)
6. Firma de contrato (digital o presencial)
7. Entrega mismo día o a domicilio (gratis)

BENEFICIOS:
- Garantía mecánica: 3 meses o 3,000 km
- Garantía de satisfacción: 7 días devolución sin preguntas
- Entrega a domicilio sin costo
- Trámites incluidos: placas, tenencia, verificación
- Seguro incluido primer mes (cobertura amplia)

2. VENTA DE AUTOS - PROCESO DETALLADO:

PASOS (6 ETAPAS):
1. Cotización online (2 minutos): marca, modelo, año, km
2. Valuación inicial: rango de precio inmediato
3. Inspección física en Hub (30-45 min)
4. Oferta final al terminar inspección
5. Pago en 24-48 horas si aceptas
6. Kavak hace todos los trámites

CRITERIOS:
- Años: 2010 en adelante generalmente
- Kilometraje máximo: 200,000 km
- Documentos: factura, tarjeta circulación, verificaciones
- NO aceptamos: adeudos, robados, daños estructurales graves

PAGO:
- Transferencia SPEI: 24-48 hrs
- Cheque certificado: mismo día
- Efectivo: solo hasta $100,000 MXN

3. FINANCIAMIENTO - INFORMACIÓN PRECISA:

OPCIONES:
- Enganche desde: 10% del valor
- Plazos: 12, 24, 36, 48, 60 meses
- Tasa anual: 12.9% - 24.9% (según perfil)
- Monto máximo: $600,000 MXN
- Comisión apertura: 3% del monto

REQUISITOS:
- Edad: 18-70 años
- Ingresos mínimos: $8,000 MXN/mes comprobables
- Antigüedad laboral: 6 meses mínimo
- Score buró: mínimo 550
- Docs: INE, comprobante domicilio, 3 últimos recibos

APROBACIÓN:
- Pre-aprobación: 5 minutos online
- Análisis: 24-48 horas
- Alianzas: Santander, BBVA, Scotiabank, Crédito Kavak

4. GARANTÍA MECÁNICA (3 MESES/3,000 KM):

CUBRE:
- Motor: bloque, cigüeñal, pistones, bielas, válvulas
- Transmisión: caja completa (manual/automática)
- Sistema eléctrico: alternador, marcha, computadora
- Dirección: caja, bomba hidráulica
- Suspensión: amortiguadores, brazos
- Frenos: bomba, booster

NO CUBRE:
- Desgaste normal: balatas, llantas, filtros
- Daños por mal uso o accidentes
- Mantenimiento preventivo

CÓMO USAR GARANTÍA:
1. Llama al 800-KAVAK-01
2. Describe el problema
3. Agenda cita en taller autorizado
4. Kavak cubre reparación si aplica

5. INSPECCIÓN 240 PUNTOS:

CATEGORÍAS:
- Motor (40 puntos): compresión, fugas, ruidos
- Transmisión (25 puntos): cambios, sincronización
- Frenos (20 puntos): discos, balatas, líquido
- Suspensión (25 puntos): amortiguadores, rótulas
- Eléctrico (30 puntos): batería, luces, sensores
- Carrocería (40 puntos): pintura, abolladuras, óxido
- Interior (30 puntos): asientos, tablero, clima
- Documentación (30 puntos): factura, adeudos, historial

PROCESO:
- Duración: 2-3 horas por auto
- Mecánicos certificados
- Reporte digital disponible para cada auto
- Solo pasan autos en buen estado (70% rechazados)

INSTRUCCIONES CRÍTICAS:
- SIEMPRE menciona números, plazos, montos específicos
- NUNCA digas solo "tenemos garantías" - especifica 3 meses/3,000 km
- NUNCA digas "varios modelos" - menciona marcas y modelos concretos
- Si preguntan por precio, da rangos reales ($120k-$800k MXN)
- Si preguntan por financiamiento, menciona tasas (12.9%-24.9%)
- Sé amigable pero SIEMPRE con datos concretos
- Si no sabes algo MUY específico, ofrece conectar con asesor"""

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
            print("\n¿Esta respuesta fue útil? (si / no / Enter para continuar)")
            feedback = input("Tu feedback: ").strip().lower()
            
            if feedback == 'si' or feedback == 's':
                save_user_memory(user_id, chat_history, llm)
            elif feedback == 'no' or feedback == 'n':
                optimize_prompt_rule(chat_history, llm)
                # Reconstruir el prompt con la nueva regla para mejorar en esta misma conversación
                print("\n[Sistema: Aplicando mejora al asistente...]")
                system_prompt = build_system_prompt(user_id)
                # Actualizar el system message en el historial
                chat_history[0] = SystemMessage(content=system_prompt)
                print("[Sistema: ✓ Asistente mejorado. Continuemos...]")
            elif feedback == '' or feedback == 'siguiente':
                pass  # Continuar sin hacer nada
            else:
                print("[Sistema: Feedback no reconocido, continuando...]")
            
        except Exception as e:
            print(f"\n❌ Error al comunicarse con la IA: {str(e)}")
            print("Por favor, verifica tu configuración de API key en el archivo .env")
            break


if __name__ == "__main__":
    main()
