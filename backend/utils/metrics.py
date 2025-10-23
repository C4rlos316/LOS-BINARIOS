"""
Calculador de Métricas
Calcula y muestra métricas de conversaciones
"""

from typing import Dict, List
from langchain.schema import HumanMessage, AIMessage


class MetricsCalculator:
    """
    Clase para calcular métricas de conversaciones.
    """
    
    # Palabras clave para detectar especificidad
    KEYWORDS_ESPECIFICOS = [
        '3 meses', '3,000 km', '7 días', '$', 'MXN', 'pesos',
        '12.9%', '24.9%', '10%', 'enganche', 'tasa',
        'Versa', 'Jetta', 'Corolla', 'Civic', 'Mazda',
        '240 puntos', 'inspección', 'Hub', 'Kavak',
        '800-KAVAK', 'SPEI', '24-48 horas', '5 minutos',
        'garantía', 'financiamiento', 'precio'
    ]
    
    @staticmethod
    def calculate_metrics(chat_history: List) -> Dict:
        """
        Calcula métricas de la conversación.
        
        Args:
            chat_history: Historial de mensajes
        
        Returns:
            Dict: Diccionario con métricas calculadas
        """
        # Extraer mensajes de usuario y bot
        user_messages = []
        bot_messages = []
        
        for msg in chat_history:
            if isinstance(msg, HumanMessage):
                user_messages.append(msg.content)
            elif isinstance(msg, AIMessage):
                bot_messages.append(msg.content)
        
        if not bot_messages:
            return MetricsCalculator._empty_metrics()
        
        # Calcular tasa de resolución
        resolved_count = 0
        for response in bot_messages:
            keyword_count = sum(
                1 for keyword in MetricsCalculator.KEYWORDS_ESPECIFICOS 
                if keyword.lower() in response.lower()
            )
            if keyword_count >= 2:
                resolved_count += 1
        
        resolution_rate = (resolved_count / len(bot_messages) * 100)
        
        # Calcular precisión y completitud
        avg_response_length = sum(len(msg) for msg in bot_messages) / len(bot_messages)
        
        total_keywords = 0
        for response in bot_messages:
            total_keywords += sum(
                1 for keyword in MetricsCalculator.KEYWORDS_ESPECIFICOS 
                if keyword.lower() in response.lower()
            )
        
        keyword_density = total_keywords / len(bot_messages)
        
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
    
    @staticmethod
    def _empty_metrics() -> Dict:
        """Retorna métricas vacías."""
        return {
            'total_interactions': 0,
            'resolved_count': 0,
            'resolution_rate': 0.0,
            'avg_response_length': 0.0,
            'keyword_density': 0.0,
            'completitud': 'N/A',
            'user_messages': [],
            'bot_messages': []
        }
    
    @staticmethod
    def display_metrics(metrics: Dict, system_stats: Dict):
        """
        Muestra las métricas de forma visual.
        
        Args:
            metrics: Métricas de la conversación
            system_stats: Estadísticas del sistema
        """
        print("\n" + "="*70)
        print("📊 REPORTE DE MÉTRICAS DE LA CONVERSACIÓN")
        print("="*70)
        
        # MÉTRICA 1: COMPARACIÓN PAREADA
        print("\n1️⃣  COMPARACIÓN PAREADA - Historial de Interacciones")
        print("─"*70)
        
        for i in range(metrics['total_interactions']):
            print(f"\n[Interacción {i+1}]")
            user_msg = metrics['user_messages'][i]
            bot_msg = metrics['bot_messages'][i]
            print(f"👤 Usuario: {user_msg[:100]}{'...' if len(user_msg) > 100 else ''}")
            print(f"🤖 Kavak:   {bot_msg[:100]}{'...' if len(bot_msg) > 100 else ''}")
        
        # MÉTRICA 2: TASA DE RESOLUCIÓN
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
        
        # MÉTRICA 3: PRECISIÓN Y COMPLETITUD
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
        
        # MÉTRICA 4: EVOLUCIÓN DEL SISTEMA
        print("\n" + "─"*70)
        print("4️⃣  EVOLUCIÓN DEL SISTEMA (Aprendizaje Global)")
        print("─"*70)
        print(f"\n   Reglas aprendidas de todos los usuarios: {system_stats['total_rules']}")
        print(f"   Usuarios que han contribuido: {system_stats['total_users']}")
        print(f"   Memorias acumuladas: {system_stats['total_memories']}")
        
        # Análisis de errores
        if system_stats['error_distribution']:
            print(f"\n   Distribución de Errores Categorizados:")
            for category, count in system_stats['error_distribution'].items():
                print(f"      - {category}: {count} reglas")
        
        # Score de validación
        if system_stats['avg_validation_score'] > 0:
            print(f"\n   Score Promedio de Validación: {system_stats['avg_validation_score']:.2f}/1.0")
            if system_stats['avg_validation_score'] >= 0.8:
                print("      ✓ Las reglas generadas son altamente efectivas")
            elif system_stats['avg_validation_score'] >= 0.5:
                print("      ✓ Las reglas generadas son moderadamente efectivas")
            else:
                print("      ⚠️ Las reglas necesitan mejorar su efectividad")
        
        # Nivel de madurez
        maturity_score = min(100, (system_stats['total_rules'] * 10) + (system_stats['total_memories'] * 2))
        
        print(f"\n   Nivel de Madurez del Sistema: {maturity_score:.0f}/100")
        
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
