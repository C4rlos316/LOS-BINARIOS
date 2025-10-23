"""
Configuración del LLM (Language Model)
Maneja la inicialización y configuración de OpenAI con LangChain
"""

import os
import httpx
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


class LLMConfig:
    """
    Clase para configurar y obtener instancias del LLM.
    Incluye configuración anti-proxy para evitar errores.
    """
    
    def __init__(self, model: str = "gpt-3.5-turbo", temperature: float = 0.7):
        """
        Inicializa la configuración del LLM.
        
        Args:
            model: Modelo de OpenAI a usar
            temperature: Temperatura para la generación (0.0-1.0)
        """
        self.model = model
        self.temperature = temperature
        self._llm_instance = None
        
        # Cargar variables de entorno
        load_dotenv()
        
        # Limpiar variables de proxy
        self._clear_proxy_variables()
    
    def _clear_proxy_variables(self):
        """Limpia variables de proxy del entorno para evitar conflictos."""
        os.environ.pop('HTTP_PROXY', None)
        os.environ.pop('HTTPS_PROXY', None)
        os.environ.pop('http_proxy', None)
        os.environ.pop('https_proxy', None)
    
    def get_llm(self) -> ChatOpenAI:
        """
        Obtiene una instancia configurada del LLM.
        Usa patrón Singleton para reutilizar la misma instancia.
        
        Returns:
            ChatOpenAI: Instancia configurada del LLM
        """
        if self._llm_instance is None:
            # Configurar clientes HTTP personalizados
            sync_client = httpx.Client(timeout=30.0)
            async_client = httpx.AsyncClient(timeout=30.0)
            
            # Inicializar LLM con clientes personalizados
            self._llm_instance = ChatOpenAI(
                model=self.model,
                temperature=self.temperature,
                http_client=sync_client,
                http_async_client=async_client
            )
        
        return self._llm_instance
    
    @staticmethod
    def create_default() -> 'LLMConfig':
        """
        Crea una configuración por defecto del LLM.
        
        Returns:
            LLMConfig: Instancia con configuración por defecto
        """
        return LLMConfig(model="gpt-3.5-turbo", temperature=0.7)
