"""
Agente Resumidor
Genera resúmenes de conversaciones para memoria del usuario
"""

from typing import List
from langchain.schema import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI


class SummarizerAgent:
    """
    Agente especializado en resumir conversaciones y extraer
    el interés clave del usuario.
    """
    
    MEMORY_PROMPT = """Eres un agente resumidor experto. Analiza esta conversación y extrae TODA la información útil del usuario.

INFORMACIÓN A CAPTURAR:

1. NECESIDAD PRINCIPAL:
   - ¿Qué busca? (comprar auto, vender auto, información, financiamiento, etc.)
   - ¿Por qué? (necesidad familiar, trabajo, primer auto, cambio, etc.)

2. PREFERENCIAS ESPECÍFICAS:
   - Tipo de vehículo (sedán, SUV, hatchback, pickup, etc.)
   - Marca(s) preferida(s)
   - Modelo(s) de interés
   - Año deseado
   - Presupuesto (mínimo y máximo)
   - Características importantes (espacio, economía, potencia, etc.)

3. CONTEXTO DEL USUARIO:
   - Experiencia previa con autos
   - Uso previsto (ciudad, carretera, familiar, trabajo)
   - Urgencia (explorando, comparando, listo para comprar)
   - Preocupaciones mencionadas (garantía, financiamiento, documentos, etc.)

4. PREGUNTAS REALIZADAS:
   - Temas sobre los que preguntó
   - Dudas específicas que tiene

Resume TODO en 2-4 frases concisas pero COMPLETAS.

EJEMPLOS:

Bueno: "Usuario busca SUV familiar para 5 personas, uso ciudad y viajes fin de semana. Presupuesto $300k-$400k, prefiere Toyota RAV4 o Mazda CX-5. Preguntó por garantía y financiamiento. Está en etapa de exploración, primer auto familiar."

Malo: "Usuario busca auto."

Genera el resumen COMPLETO:"""
    
    def __init__(self, llm: ChatOpenAI):
        """
        Inicializa el Agente Resumidor.
        
        Args:
            llm: Instancia del LLM configurado
        """
        self.llm = llm
    
    def summarize_conversation(self, chat_history: List) -> str:
        """
        Resume la conversación en una frase concisa.
        
        Args:
            chat_history: Historial completo de la conversación
        
        Returns:
            str: Resumen conciso de la conversación
        """
        # Preparar mensajes para el LLM
        messages_for_summary = [
            SystemMessage(content=self.MEMORY_PROMPT)
        ] + chat_history
        
        # Generar resumen
        response = self.llm.invoke(messages_for_summary)
        summary_text = response.content
        
        return summary_text
    
    def extract_key_interests(self, chat_history: List) -> List[str]:
        """
        Extrae los intereses clave de la conversación.
        
        Args:
            chat_history: Historial de la conversación
        
        Returns:
            List[str]: Lista de intereses clave
        """
        summary = self.summarize_conversation(chat_history)
        
        # Dividir en puntos clave (si el resumen contiene múltiples puntos)
        interests = [interest.strip() for interest in summary.split(',')]
        
        return interests
