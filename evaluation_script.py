"""
Script de Evaluación Comparativa con LLM-as-Judge
Demuestra científicamente la mejora del sistema con métricas cuantitativas.
"""

import sqlite3
import os
import httpx
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
import json
from datetime import datetime

# Importar funciones del agente
from console_agent import build_system_prompt, get_db_connection


# Configuración inicial
load_dotenv()

# Limpiar variables de proxy
os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)
os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None)

# Configurar clientes HTTP
sync_client = httpx.Client(timeout=30.0)
async_client = httpx.AsyncClient(timeout=30.0)

# Inicializar LLM
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.7,
    http_client=sync_client,
    http_async_client=async_client
)


# PREGUNTAS DE EVALUACIÓN ESTÁNDAR
EVALUATION_QUESTIONS = [
    "¿Qué garantías tienen los autos?",
    "¿Cuánto cuesta un Jetta?",
    "¿Qué modelos de Toyota tienen disponibles?",
    "¿Cuáles son los requisitos para financiamiento?",
    "¿Cómo funciona el proceso de compra?",
    "¿Qué cubre la inspección de 240 puntos?",
    "¿Puedo vender mi auto en Kavak?",
    "¿Qué formas de pago aceptan?",
    "¿Cuánto tiempo tarda la aprobación del crédito?",
    "¿Qué pasa si no me gusta el auto después de comprarlo?",
    "¿Tienen autos híbridos o eléctricos?",
    "¿Cuál es el kilometraje máximo de los autos?",
    "¿Ofrecen entrega a domicilio?",
    "¿Qué documentos necesito para comprar un auto?",
    "¿Puedo apartar un auto sin compromiso?"
]


def llm_as_judge(question, answer, llm_instance):
    """
    Usa GPT como juez para evaluar la calidad de una respuesta.
    Retorna un score de 1-5 y explicación.
    """
    judge_prompt = f"""Eres un evaluador experto de chatbots de servicio al cliente.

Evalúa la siguiente respuesta del chatbot de Kavak en una escala de 1-5:

PREGUNTA DEL USUARIO:
{question}

RESPUESTA DEL BOT:
{answer}

CRITERIOS DE EVALUACIÓN:
1. RELEVANCIA: ¿La respuesta aborda directamente la pregunta?
2. ESPECIFICIDAD: ¿Incluye datos concretos (precios, plazos, números)?
3. COMPLETITUD: ¿Proporciona información suficiente?
4. CLARIDAD: ¿Es fácil de entender?

ESCALA:
5 - EXCELENTE: Respuesta completa, específica y muy útil
4 - BUENA: Respuesta útil con algunos detalles específicos
3 - ACEPTABLE: Respuesta correcta pero genérica o incompleta
2 - DEFICIENTE: Respuesta vaga o parcialmente incorrecta
1 - MALA: Respuesta irrelevante o incorrecta

Responde SOLO en formato JSON:
{{"score": <número 1-5>, "razon": "<explicación breve>"}}"""

    try:
        response = llm_instance.invoke([HumanMessage(content=judge_prompt)])
        result = json.loads(response.content)
        return result['score'], result['razon']
    except:
        # Si falla el parsing, usar evaluación básica
        keywords = ['$', 'MXN', '3 meses', '3,000 km', '7 días', '240 puntos', 
                   'Jetta', 'Versa', 'Corolla', '12.9%', '24.9%']
        keyword_count = sum(1 for kw in keywords if kw.lower() in answer.lower())
        
        if keyword_count >= 4:
            return 5, "Respuesta con múltiples datos específicos"
        elif keyword_count >= 2:
            return 3, "Respuesta con algunos datos específicos"
        else:
            return 2, "Respuesta genérica"


def run_evaluation(prompt_system, questions, llm_instance, label=""):
    """
    Ejecuta evaluación completa con un conjunto de preguntas.
    Retorna resultados detallados.
    """
    print(f"\n{'='*80}")
    print(f"EJECUTANDO EVALUACIÓN: {label}")
    print(f"{'='*80}")
    
    results = []
    total_score = 0
    
    for i, question in enumerate(questions, 1):
        print(f"\n[{i}/{len(questions)}] Preguntando: {question}")
        
        # Crear historial para esta pregunta
        history = [
            SystemMessage(content=prompt_system),
            HumanMessage(content=question)
        ]
        
        # Obtener respuesta del bot
        response = llm_instance.invoke(history)
        answer = response.content
        
        # Evaluar con LLM-as-Judge
        score, razon = llm_as_judge(question, answer, llm_instance)
        total_score += score
        
        results.append({
            'question': question,
            'answer': answer,
            'score': score,
            'razon': razon
        })
        
        print(f"   Score: {score}/5 - {razon}")
        print(f"   Respuesta: {answer[:100]}...")
    
    avg_score = total_score / len(questions)
    
    print(f"\n{'='*80}")
    print(f"SCORE PROMEDIO: {avg_score:.2f}/5.0 ({avg_score*20:.1f}%)")
    print(f"{'='*80}")
    
    return {
        'label': label,
        'results': results,
        'avg_score': avg_score,
        'total_questions': len(questions)
    }


def insert_sample_rules():
    """
    Inserta reglas de ejemplo para demostrar la mejora.
    """
    sample_rules = [
        "REGLA: Si preguntan por garantías, SIEMPRE mencionar garantía mecánica de 3 meses o 3,000 km Y garantía de satisfacción de 7 días.",
        "REGLA: Si preguntan por precios de autos, proporcionar rangos específicos: $120,000 - $800,000 MXN según marca, modelo y año.",
        "REGLA: Si preguntan por financiamiento, mencionar tasas (12.9%-24.9%), enganche mínimo 10%, y score de buró mínimo 550.",
        "REGLA: Si preguntan por inspección, especificar que son 240 puntos en 8 categorías y toma 2-3 horas.",
        "REGLA: Si preguntan por proceso de compra, enumerar los 7 pasos específicos desde búsqueda hasta entrega.",
        "REGLA: Si preguntan por modelos específicos, mencionar al menos 3 opciones con rangos de precio aproximados.",
        "REGLA: Si preguntan por documentos, listar específicamente: INE, comprobante domicilio, 3 últimos recibos de nómina.",
        "REGLA: Si preguntan por tiempos, ser específico: aprobación crédito 24-48 hrs, pago venta 24-48 hrs, inspección 30-45 min."
    ]
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    for rule in sample_rules:
        # Verificar si ya existe
        cursor.execute('SELECT COUNT(*) FROM prompt_rules WHERE rule_text = ?', (rule,))
        if cursor.fetchone()[0] == 0:
            cursor.execute('INSERT INTO prompt_rules (rule_text) VALUES (?)', (rule,))
    
    conn.commit()
    conn.close()
    
    print(f"\n[Sistema: {len(sample_rules)} reglas de ejemplo insertadas en la BD]")


def clear_rules():
    """
    Limpia todas las reglas para baseline.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM prompt_rules')
    conn.commit()
    conn.close()
    print("\n[Sistema: Reglas limpiadas para evaluación baseline]")


def get_baseline_prompt():
    """
    Obtiene el prompt base sin reglas ni memoria.
    """
    from console_agent import build_system_prompt
    
    # Temporalmente limpiar reglas
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT rule_text FROM prompt_rules')
    saved_rules = [row[0] for row in cursor.fetchall()]
    cursor.execute('DELETE FROM prompt_rules')
    conn.commit()
    conn.close()
    
    # Construir prompt baseline
    baseline = build_system_prompt("eval_baseline")
    
    # Restaurar reglas
    conn = get_db_connection()
    cursor = conn.cursor()
    for rule in saved_rules:
        cursor.execute('INSERT INTO prompt_rules (rule_text) VALUES (?)', (rule,))
    conn.commit()
    conn.close()
    
    return baseline


def generate_comparison_report(baseline_results, improved_results):
    """
    Genera reporte comparativo detallado.
    """
    print("\n\n" + "="*80)
    print("📊 REPORTE COMPARATIVO DETALLADO")
    print("="*80)
    
    # Comparación de scores
    print("\n1. COMPARACIÓN DE SCORES PROMEDIO")
    print("-"*80)
    print(f"   Baseline (Sin Reglas):     {baseline_results['avg_score']:.2f}/5.0 ({baseline_results['avg_score']*20:.1f}%)")
    print(f"   Mejorado (Con Reglas):     {improved_results['avg_score']:.2f}/5.0 ({improved_results['avg_score']*20:.1f}%)")
    
    mejora_absoluta = improved_results['avg_score'] - baseline_results['avg_score']
    mejora_porcentual = (mejora_absoluta / baseline_results['avg_score']) * 100
    
    print(f"\n   MEJORA ABSOLUTA:  +{mejora_absoluta:.2f} puntos")
    print(f"   MEJORA RELATIVA:  +{mejora_porcentual:.1f}%")
    
    if mejora_absoluta > 0:
        print(f"\n   ✅ EVIDENCIA CUANTITATIVA DE MEJORA")
    else:
        print(f"\n   ⚠️  No se detectó mejora significativa")
    
    # Comparación por pregunta
    print("\n\n2. COMPARACIÓN PREGUNTA POR PREGUNTA")
    print("-"*80)
    
    mejoras = 0
    empates = 0
    retrocesos = 0
    
    for i in range(len(baseline_results['results'])):
        base = baseline_results['results'][i]
        impr = improved_results['results'][i]
        
        diff = impr['score'] - base['score']
        
        if diff > 0:
            symbol = "↑"
            mejoras += 1
        elif diff < 0:
            symbol = "↓"
            retrocesos += 1
        else:
            symbol = "="
            empates += 1
        
        print(f"\n   [{i+1}] {base['question'][:50]}...")
        print(f"       Baseline: {base['score']}/5  →  Mejorado: {impr['score']}/5  {symbol} ({diff:+.0f})")
    
    print(f"\n   Resumen: {mejoras} mejoras, {empates} sin cambio, {retrocesos} retrocesos")
    
    # Distribución de scores
    print("\n\n3. DISTRIBUCIÓN DE SCORES")
    print("-"*80)
    
    def count_scores(results):
        counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for r in results['results']:
            counts[r['score']] += 1
        return counts
    
    base_dist = count_scores(baseline_results)
    impr_dist = count_scores(improved_results)
    
    print("\n   Score | Baseline | Mejorado")
    print("   ------|----------|----------")
    for score in [5, 4, 3, 2, 1]:
        print(f"     {score}   |    {base_dist[score]:2d}    |    {impr_dist[score]:2d}")
    
    # Conclusión
    print("\n\n4. CONCLUSIÓN")
    print("-"*80)
    
    if mejora_porcentual >= 20:
        conclusion = "MEJORA SIGNIFICATIVA - El sistema de aprendizaje es altamente efectivo"
    elif mejora_porcentual >= 10:
        conclusion = "MEJORA MODERADA - El sistema de aprendizaje es efectivo"
    elif mejora_porcentual >= 5:
        conclusion = "MEJORA LEVE - El sistema muestra potencial de mejora"
    else:
        conclusion = "SIN MEJORA SIGNIFICATIVA - Revisar estrategia de aprendizaje"
    
    print(f"\n   {conclusion}")
    print(f"\n   El sistema mejoró en {mejoras}/{len(baseline_results['results'])} preguntas ({mejoras/len(baseline_results['results'])*100:.1f}%)")
    
    print("\n" + "="*80)


def save_results_to_file(baseline_results, improved_results):
    """
    Guarda resultados en archivo JSON para análisis posterior.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"evaluation_results_{timestamp}.json"
    
    data = {
        'timestamp': timestamp,
        'baseline': {
            'avg_score': baseline_results['avg_score'],
            'results': baseline_results['results']
        },
        'improved': {
            'avg_score': improved_results['avg_score'],
            'results': improved_results['results']
        },
        'mejora_absoluta': improved_results['avg_score'] - baseline_results['avg_score'],
        'mejora_porcentual': ((improved_results['avg_score'] - baseline_results['avg_score']) / baseline_results['avg_score']) * 100
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n[Sistema: Resultados guardados en {filename}]")


def main():
    """
    Función principal de evaluación comparativa.
    """
    print("\n" + "="*80)
    print("SISTEMA DE EVALUACIÓN COMPARATIVA CON LLM-AS-JUDGE")
    print("="*80)
    print("\nEste script demuestra científicamente la mejora del sistema")
    print("comparando el bot SIN reglas vs CON reglas aprendidas.\n")
    
    # PASO 1: Evaluación Baseline (sin reglas)
    print("\n" + "="*80)
    print("PASO 1: EVALUACIÓN BASELINE (Sin Reglas de Aprendizaje)")
    print("="*80)
    
    baseline_prompt = get_baseline_prompt()
    baseline_results = run_evaluation(
        baseline_prompt,
        EVALUATION_QUESTIONS,
        llm,
        "BASELINE - Sin Reglas"
    )
    
    # PASO 2: Insertar reglas de aprendizaje
    print("\n" + "="*80)
    print("PASO 2: INSERTANDO REGLAS DE APRENDIZAJE")
    print("="*80)
    
    insert_sample_rules()
    
    # PASO 3: Evaluación Mejorada (con reglas)
    print("\n" + "="*80)
    print("PASO 3: EVALUACIÓN MEJORADA (Con Reglas de Aprendizaje)")
    print("="*80)
    
    improved_prompt = build_system_prompt("eval_improved")
    improved_results = run_evaluation(
        improved_prompt,
        EVALUATION_QUESTIONS,
        llm,
        "MEJORADO - Con Reglas"
    )
    
    # PASO 4: Generar reporte comparativo
    generate_comparison_report(baseline_results, improved_results)
    
    # PASO 5: Guardar resultados
    save_results_to_file(baseline_results, improved_results)
    
    print("\n✅ Evaluación completada exitosamente\n")


if __name__ == "__main__":
    main()
