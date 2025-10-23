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


def categorize_error(question, answer, llm_instance):
    """
    Categoriza el tipo de error en la respuesta.
    Retorna: categoria y descripción.
    """
    categorization_prompt = f"""Analiza esta interacción fallida y categoriza el tipo de error.

PREGUNTA: {question}
RESPUESTA: {answer}

CATEGORÍAS POSIBLES:
- vago: Respuesta genérica sin datos específicos
- incorrecto: Información errónea o desactualizada
- incompleto: Falta información importante
- fuera_contexto: No aborda la pregunta del usuario
- general: Otro tipo de error

Responde SOLO con el nombre de la categoría (una palabra)."""

    try:
        response = llm_instance.invoke([HumanMessage(content=categorization_prompt)])
        category = response.content.strip().lower()
        
        # Validar categoría
        valid_categories = ['vago', 'incorrecto', 'incompleto', 'fuera_contexto', 'general']
        if category not in valid_categories:
            category = 'general'
        
        return category
    except:
        return 'general'


def validate_rule(rule_text, test_question, llm_instance):
    """
    Valida si una regla nueva realmente mejora las respuestas.
    Retorna score de validación (0.0 - 1.0).
    """
    # Crear prompt con y sin la regla
    base_prompt = "Eres un asistente de Kavak. Responde de forma útil."
    improved_prompt = f"{base_prompt}\n\n{rule_text}"
    
    # Probar sin regla
    response_without = llm_instance.invoke([
        SystemMessage(content=base_prompt),
        HumanMessage(content=test_question)
    ])
    
    # Probar con regla
    response_with = llm_instance.invoke([
        SystemMessage(content=improved_prompt),
        HumanMessage(content=test_question)
    ])
    
    # Evaluar ambas respuestas
    judge_prompt = f"""Compara estas dos respuestas a la pregunta: "{test_question}"

RESPUESTA A (sin regla): {response_without.content[:200]}
RESPUESTA B (con regla): {response_with.content[:200]}

¿La Respuesta B es mejor que la Respuesta A?
Responde SOLO: "si" o "no"."""
    
    try:
        judgment = llm_instance.invoke([HumanMessage(content=judge_prompt)])
        is_better = judgment.content.strip().lower()
        
        return 1.0 if 'si' in is_better or 'sí' in is_better else 0.0
    except:
        return 0.5  # Score neutral si falla


def optimize_prompt_rule(chat_history_list, llm_instance):
    """
    Agente Optimizador MEJORADO: Categoriza errores y valida reglas antes de guardar.
    """
    # Extraer la última pregunta y respuesta
    last_human_message = None
    last_ai_message = None
    
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
    
    # PASO 1: Categorizar el error
    print("\n[Sistema: Analizando tipo de error...]")
    error_category = categorize_error(last_human_message, last_ai_message, llm_instance)
    print(f"[Sistema: Error categorizado como '{error_category}']")
    
    # PASO 2: Generar regla
    OPTIMIZER_PROMPT = f"""Eres un 'Optimizador de Prompts' experto. La siguiente respuesta del bot fue marcada como 'No Útil' (tipo de error: {error_category}).

Tu tarea es generar una 'REGLA:' corta y específica para mejorar futuras respuestas.

Ejemplo: 'REGLA: Si el usuario pregunta por garantía, siempre mencionar la garantía mecánica de 3 meses.'

---
Pregunta del Usuario: {last_human_message}
Respuesta del Bot (fallida): {last_ai_message}
Tipo de error: {error_category}
---

Genera la nueva REGLA:"""
    
    response = llm_instance.invoke([HumanMessage(content=OPTIMIZER_PROMPT)])
    new_rule_text = response.content
    
    # PASO 3: Validar la regla
    print("[Sistema: Validando efectividad de la regla...]")
    validation_score = validate_rule(new_rule_text, last_human_message, llm_instance)
    
    # PASO 4: Guardar solo si la validación es positiva
    if validation_score >= 0.5:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            'INSERT INTO prompt_rules (rule_text, error_category, validation_score) VALUES (?, ?, ?)',
            (new_rule_text, error_category, validation_score)
        )
        
        conn.commit()
        conn.close()
        
        print(f"\n[Sistema: ✓ Regla validada (score: {validation_score:.1f}) y guardada. Categoría: {error_category}]")
    else:
        print(f"\n[Sistema: ✗ Regla descartada (score: {validation_score:.1f}). No mejora las respuestas.]")


def calculate_metrics(chat_history):
    """
    Calcula métricas de la conversación para mostrar al final.
    Retorna un diccionario con las métricas calculadas.
    """
    # Extraer solo mensajes de usuario y bot (sin SystemMessage)
    user_messages = []
    bot_messages = []
    
    for msg in chat_history:
        if isinstance(msg, HumanMessage):
            user_messages.append(msg.content)
        elif isinstance(msg, AIMessage):
            bot_messages.append(msg.content)
    
    # MÉTRICA 1: Tasa de Resolución (basada en especificidad de respuestas)
    keywords_especificos = [
        '3 meses', '3,000 km', '7 días', '$', 'MXN', 'pesos',
        '12.9%', '24.9%', '10%', 'enganche', 'tasa',
        'Versa', 'Jetta', 'Corolla', 'Civic', 'Mazda',
        '240 puntos', 'inspección', 'Hub', 'Kavak',
        '800-KAVAK', 'SPEI', '24-48 horas', '5 minutos',
        'garantía', 'financiamiento', 'precio'
    ]
    
    resolved_count = 0
    for response in bot_messages:
        keyword_count = sum(1 for keyword in keywords_especificos if keyword.lower() in response.lower())
        if keyword_count >= 2:
            resolved_count += 1
    
    resolution_rate = (resolved_count / len(bot_messages) * 100) if bot_messages else 0
    
    # MÉTRICA 2: Precisión y Completitud (longitud promedio y densidad de información)
    avg_response_length = sum(len(msg) for msg in bot_messages) / len(bot_messages) if bot_messages else 0
    
    total_keywords = 0
    for response in bot_messages:
        total_keywords += sum(1 for keyword in keywords_especificos if keyword.lower() in response.lower())
    
    keyword_density = (total_keywords / len(bot_messages)) if bot_messages else 0
    
    # Clasificar completitud
    if keyword_density >= 5:
        completitud = "EXCELENTE"
    elif keyword_density >= 3:
        completitud = "BUENA"
    elif keyword_density >= 1:
        completitud = "REGULAR"
    else:
        completitud = "BAJA"
    
    return {
        'total_interactions': len(user_messages),
        'resolved_count': resolved_count,
        'resolution_rate': resolution_rate,
        'avg_response_length': avg_response_length,
        'keyword_density': keyword_density,
        'completitud': completitud,
        'user_messages': user_messages,
        'bot_messages': bot_messages
    }


def auto_learn_from_conversation(chat_history, user_id, llm_instance):
    """
    Analiza automáticamente la conversación y aprende patrones exitosos.
    Se ejecuta al finalizar cada conversación SIN intervención del usuario.
    """
    # Extraer mensajes de usuario y bot
    interactions = []
    for i in range(len(chat_history)):
        if isinstance(chat_history[i], HumanMessage):
            if i + 1 < len(chat_history) and isinstance(chat_history[i+1], AIMessage):
                interactions.append({
                    'question': chat_history[i].content,
                    'answer': chat_history[i+1].content
                })
    
    if not interactions:
        return
    
    # Analizar qué respuestas fueron específicas (aprendizaje automático)
    keywords_especificos = [
        '3 meses', '3,000 km', '7 días', '$', 'MXN', 'pesos',
        '12.9%', '24.9%', '10%', 'enganche', 'tasa',
        'Versa', 'Jetta', 'Corolla', 'Civic', 'Mazda',
        '240 puntos', 'inspección', 'Hub', 'Kavak',
        '800-KAVAK', 'SPEI', '24-48 horas', '5 minutos'
    ]
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    learned_something = False
    
    for interaction in interactions:
        keyword_count = sum(1 for kw in keywords_especificos if kw.lower() in interaction['answer'].lower())
        
        # Si la respuesta fue específica (>=3 keywords), aprender de ella
        if keyword_count >= 3:
            # Generar regla automáticamente usando el LLM
            learning_prompt = f"""Analiza esta interacción exitosa y genera UNA regla corta y específica para mejorar futuras respuestas similares.

Pregunta del usuario: {interaction['question']}
Respuesta exitosa del bot: {interaction['answer'][:200]}...

Genera solo la REGLA en formato: 'REGLA: [regla específica]'
Ejemplo: 'REGLA: Si preguntan por garantías, siempre mencionar 3 meses/3,000 km y 7 días de satisfacción.'"""
            
            try:
                response = llm_instance.invoke([HumanMessage(content=learning_prompt)])
                new_rule = response.content.strip()
                
                # Verificar que no sea una regla duplicada
                cursor.execute('SELECT COUNT(*) FROM prompt_rules WHERE rule_text = ?', (new_rule,))
                if cursor.fetchone()[0] == 0:
                    cursor.execute('INSERT INTO prompt_rules (rule_text) VALUES (?)', (new_rule,))
                    learned_something = True
            except:
                pass  # Si falla, continuar sin romper el flujo
    
    # Guardar memoria del usuario automáticamente
    if interactions:
        memory_prompt = f"Resume en UNA frase el interés principal del usuario basado en estas preguntas: {', '.join([i['question'] for i in interactions[:3]])}"
        try:
            response = llm_instance.invoke([HumanMessage(content=memory_prompt)])
            summary = response.content.strip()
            cursor.execute('INSERT INTO user_memory (user_id, context) VALUES (?, ?)', (user_id, summary))
        except:
            pass
    
    conn.commit()
    conn.close()
    
    if learned_something:
        print("\n[Sistema: El bot aprendió automáticamente de esta conversación]")


def get_system_evolution_metrics():
    """
    Calcula métricas de evolución del sistema a lo largo del tiempo.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Contar reglas aprendidas
    cursor.execute('SELECT COUNT(*) FROM prompt_rules')
    total_rules = cursor.fetchone()[0]
    
    # Contar memorias de usuarios
    cursor.execute('SELECT COUNT(DISTINCT user_id) FROM user_memory')
    total_users = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM user_memory')
    total_memories = cursor.fetchone()[0]
    
    # Análisis de errores por categoría
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


def display_metrics(metrics):
    """
    Muestra las métricas de forma visual al final de la conversación.
    """
    print("\n" + "="*70)
    print("📊 REPORTE DE MÉTRICAS DE LA CONVERSACIÓN")
    print("="*70)
    
    # MÉTRICA 1: COMPARACIÓN PAREADA (La Tabla)
    print("\n1️⃣  COMPARACIÓN PAREADA - Historial de Interacciones")
    print("─"*70)
    
    for i in range(metrics['total_interactions']):
        print(f"\n[Interacción {i+1}]")
        print(f"👤 Usuario: {metrics['user_messages'][i][:100]}{'...' if len(metrics['user_messages'][i]) > 100 else ''}")
        print(f"🤖 Kavak:   {metrics['bot_messages'][i][:100]}{'...' if len(metrics['bot_messages'][i]) > 100 else ''}")
    
    # MÉTRICA 2: TASA DE RESOLUCIÓN (El Puntaje)
    print("\n" + "─"*70)
    print("2️⃣  TASA DE RESOLUCIÓN DE PROBLEMAS")
    print("─"*70)
    print(f"\n   Respuestas con datos específicos: {metrics['resolved_count']}/{metrics['total_interactions']}")
    print(f"   Tasa de Resolución: {metrics['resolution_rate']:.1f}%")
    
    # Barra visual
    bar_length = 30
    filled = int((metrics['resolution_rate'] / 100) * bar_length)
    bar = "█" * filled + "░" * (bar_length - filled)
    print(f"   [{bar}] {metrics['resolution_rate']:.1f}%")
    
    if metrics['resolution_rate'] >= 80:
        print("   ✅ EXCELENTE - El bot proporcionó información específica")
    elif metrics['resolution_rate'] >= 60:
        print("   ✓ BUENO - La mayoría de respuestas fueron específicas")
    elif metrics['resolution_rate'] >= 40:
        print("   ⚠️  REGULAR - Algunas respuestas fueron vagas")
    else:
        print("   ❌ BAJO - El bot necesita más datos específicos")
    
    # MÉTRICA 3: PRECISIÓN Y COMPLETITUD (La Explicación)
    print("\n" + "─"*70)
    print("3️⃣  PRECISIÓN Y COMPLETITUD")
    print("─"*70)
    print(f"\n   Longitud promedio de respuestas: {metrics['avg_response_length']:.0f} caracteres")
    print(f"   Densidad de información: {metrics['keyword_density']:.1f} datos específicos por respuesta")
    print(f"   Nivel de Completitud: {metrics['completitud']}")
    
    if metrics['completitud'] == "EXCELENTE":
        print("   ✅ Las respuestas incluyen múltiples datos concretos (precios, plazos, etc.)")
    elif metrics['completitud'] == "BUENA":
        print("   ✓ Las respuestas incluyen datos específicos relevantes")
    elif metrics['completitud'] == "REGULAR":
        print("   ⚠️  Las respuestas podrían ser más específicas")
    else:
        print("   ❌ Las respuestas carecen de datos concretos")
    
    # MÉTRICA 4: EVOLUCIÓN DEL SISTEMA (Nueva métrica de aprendizaje global)
    evolution = get_system_evolution_metrics()
    print("\n" + "─"*70)
    print("4️⃣  EVOLUCIÓN DEL SISTEMA (Aprendizaje Global)")
    print("─"*70)
    print(f"\n   Reglas aprendidas de todos los usuarios: {evolution['total_rules']}")
    print(f"   Usuarios que han contribuido: {evolution['total_users']}")
    print(f"   Memorias acumuladas: {evolution['total_memories']}")
    
    # Análisis de errores por categoría
    if evolution['error_distribution']:
        print(f"\n   Distribución de Errores Categorizados:")
        for category, count in evolution['error_distribution'].items():
            print(f"      - {category}: {count} reglas")
    
    # Score de validación promedio
    if evolution['avg_validation_score'] > 0:
        print(f"\n   Score Promedio de Validación: {evolution['avg_validation_score']:.2f}/1.0")
        if evolution['avg_validation_score'] >= 0.8:
            print("      ✓ Las reglas generadas son altamente efectivas")
        elif evolution['avg_validation_score'] >= 0.5:
            print("      ✓ Las reglas generadas son moderadamente efectivas")
        else:
            print("      ⚠️ Las reglas necesitan mejorar su efectividad")
    
    # Calcular nivel de madurez del sistema
    maturity_score = min(100, (evolution['total_rules'] * 10) + (evolution['total_memories'] * 2))
    
    print(f"\n   Nivel de Madurez del Sistema: {maturity_score:.0f}/100")
    
    # Barra de madurez
    bar_length = 30
    filled = int((maturity_score / 100) * bar_length)
    bar = "#" * filled + "-" * (bar_length - filled)
    print(f"   [{bar}] {maturity_score:.0f}%")
    
    if maturity_score >= 80:
        print("   >>> SISTEMA MADURO - El bot ha aprendido mucho de los usuarios")
    elif maturity_score >= 50:
        print("   >>> SISTEMA EN CRECIMIENTO - Aprendiendo activamente")
    elif maturity_score >= 20:
        print("   >>> SISTEMA INICIAL - Comenzando a aprender")
    else:
        print("   >>> SISTEMA NUEVO - Primeras interacciones")
    
    print("\n" + "="*70)
    print("Fin del Reporte de Métricas")
    print("="*70 + "\n")


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
            # Aprendizaje automático de la conversación
            if len(chat_history) > 1:
                print("\n" + "="*70)
                print("Analizando conversación y aprendiendo automáticamente...")
                print("="*70)
                
                # APRENDIZAJE AUTOMÁTICO (sin intervención del usuario)
                auto_learn_from_conversation(chat_history, user_id, llm)
                
                # Calcular y mostrar métricas
                print("\nGenerando reporte de métricas...\n")
                metrics = calculate_metrics(chat_history)
                display_metrics(metrics)
            
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
            
            # Sistema de feedback OPCIONAL (el aprendizaje real es automático al salir)
            print("\n¿Quieres dar feedback? (si/no para forzar aprendizaje, Enter para continuar)")
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
                pass  # Continuar - el aprendizaje real ocurre automáticamente al salir
            else:
                pass  # Continuar
            
        except Exception as e:
            print(f"\n❌ Error al comunicarse con la IA: {str(e)}")
            print("Por favor, verifica tu configuración de API key en el archivo .env")
            break


if __name__ == "__main__":
    main()
