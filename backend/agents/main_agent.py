"""
Agente Principal (Chatbot de Kavak)
Responde preguntas de usuarios sobre Kavak
"""

from typing import List
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI






















class MainAgent:
    """
    Agente Principal que responde preguntas usando el prompt base,
    reglas aprendidas y memoria del usuario.
    """
    
    # Prompt base MÍNIMO - Los agentes Optimizer y Summarizer mejorarán el sistema
    PROMPT_BASE = """Eres un asistente virtual de Kavak.

Kavak es una plataforma de compra y venta de autos seminuevos.

Tu trabajo es ayudar a los usuarios con sus preguntas sobre autos.

Sé amigable y haz preguntas para entender mejor lo que necesitan."""
    
    def __init__(self, llm: ChatOpenAI):
        """
        Inicializa el Agente Principal.
        
        Args:
            llm: Instancia del LLM configurado
        """
        self.llm = llm
    
    def build_system_prompt(self, rules: str, memory: str) -> str:
        """
        Construye el prompt del sistema combinando base, reglas y memoria.
        
        Args:
            rules: Reglas aprendidas de la BD
            memory: Memoria del usuario
        
        Returns:
            str: Prompt completo del sistema
        """
        prompt = self.PROMPT_BASE
        
        if rules:
            prompt += f"\n\nREGLAS ADICIONALES:\n{rules}"
        
        if memory:
            prompt += f"\n\n{memory}"
        
        return prompt
    
    def respond(self, chat_history: List) -> str:
        """
        Genera una respuesta a la pregunta del usuario.
        
        Args:
            chat_history: Historial de la conversación
        
        Returns:
            str: Respuesta del agente
        """
        response = self.llm.invoke(chat_history)
        return response.content
