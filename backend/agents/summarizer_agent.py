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
    
    MEMORY_PROMPT = """Eres un agente resumidor. Basado en esta conversación, extrae el interés clave, problema o intención del usuario en una sola frase concisa para usarla como memoria a futuro."""
    
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
