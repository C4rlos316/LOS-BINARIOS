"""
Agente Optimizador
Analiza errores, categoriza y genera reglas de mejora validadas
"""

from typing import Tuple, List
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI


class OptimizerAgent:
    """
    Agente especializado en analizar fallos, categorizar errores
    y generar reglas de mejora validadas.
    """
    
    def __init__(self, llm: ChatOpenAI):
        """
        Inicializa el Agente Optimizador.
        
        Args:
            llm: Instancia del LLM configurado
        """
        self.llm = llm
    
    def categorize_error(self, question: str, answer: str) -> str:
        """
        Categoriza el tipo de error en la respuesta.
        
        Args:
            question: Pregunta del usuario
            answer: Respuesta del bot
        
        Returns:
            str: Categoría del error
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
            response = self.llm.invoke([HumanMessage(content=categorization_prompt)])
            category = response.content.strip().lower()
            
            # Validar categoría
            valid_categories = ['vago', 'incorrecto', 'incompleto', 'fuera_contexto', 'general']
            if category not in valid_categories:
                category = 'general'
            
            return category
        except:
            return 'general'
    
    def generate_rule(self, question: str, answer: str, error_category: str) -> str:
        """
        Genera una regla de mejora basada en el error detectado.
        
        Args:
            question: Pregunta del usuario
            answer: Respuesta fallida del bot
            error_category: Categoría del error
        
        Returns:
            str: Regla generada
        """
        optimizer_prompt = f"""Eres un 'Optimizador de Prompts' experto. La siguiente respuesta del bot fue marcada como 'No Útil' (tipo de error: {error_category}).

Tu tarea es generar una 'REGLA:' corta y específica para mejorar futuras respuestas.

Ejemplo: 'REGLA: Si el usuario pregunta por garantía, siempre mencionar la garantía mecánica de 3 meses.'

---
Pregunta del Usuario: {question}
Respuesta del Bot (fallida): {answer}
Tipo de error: {error_category}
---

Genera la nueva REGLA:"""
        
        response = self.llm.invoke([HumanMessage(content=optimizer_prompt)])
        new_rule_text = response.content
        
        return new_rule_text
    
    def validate_rule(self, rule_text: str, test_question: str) -> float:
        """
        Valida si una regla nueva realmente mejora las respuestas.
        
        Args:
            rule_text: Texto de la regla a validar
            test_question: Pregunta de prueba
        
        Returns:
            float: Score de validación (0.0 - 1.0)
        """
        # Crear prompt con y sin la regla
        base_prompt = "Eres un asistente de Kavak. Responde de forma útil."
        improved_prompt = f"{base_prompt}\n\n{rule_text}"
        
        try:
            # Probar sin regla
            response_without = self.llm.invoke([
                SystemMessage(content=base_prompt),
                HumanMessage(content=test_question)
            ])
            
            # Probar con regla
            response_with = self.llm.invoke([
                SystemMessage(content=improved_prompt),
                HumanMessage(content=test_question)
            ])
            
            # Evaluar ambas respuestas
            judge_prompt = f"""Compara estas dos respuestas a la pregunta: "{test_question}"

RESPUESTA A (sin regla): {response_without.content[:200]}
RESPUESTA B (con regla): {response_with.content[:200]}

¿La Respuesta B es mejor que la Respuesta A?
Responde SOLO: "si" o "no"."""
            
            judgment = self.llm.invoke([HumanMessage(content=judge_prompt)])
            is_better = judgment.content.strip().lower()
            
            return 1.0 if 'si' in is_better or 'sí' in is_better else 0.0
        except:
            return 0.5  # Score neutral si falla
    
    def optimize(self, chat_history: List) -> Tuple[str, str, float]:
        """
        Proceso completo de optimización: categoriza, genera y valida regla.
        
        Args:
            chat_history: Historial de la conversación
        
        Returns:
            Tuple[str, str, float]: (regla, categoría, score_validación)
        """
        # Extraer última pregunta y respuesta
        last_human_message = None
        last_ai_message = None
        
        for msg in reversed(chat_history):
            if isinstance(msg, AIMessage) and last_ai_message is None:
                last_ai_message = msg.content
            elif isinstance(msg, HumanMessage) and last_human_message is None:
                last_human_message = msg.content
            
            if last_human_message and last_ai_message:
                break
        
        if not last_human_message or not last_ai_message:
            raise ValueError("No se pudo extraer la conversación para optimizar")
        
        # PASO 1: Categorizar el error
        print("\n[Sistema: Analizando tipo de error...]")
        error_category = self.categorize_error(last_human_message, last_ai_message)
        print(f"[Sistema: Error categorizado como '{error_category}']")
        
        # PASO 2: Generar regla
        new_rule_text = self.generate_rule(last_human_message, last_ai_message, error_category)
        
        # PASO 3: Validar la regla
        print("[Sistema: Validando efectividad de la regla...]")
        validation_score = self.validate_rule(new_rule_text, last_human_message)
        
        return new_rule_text, error_category, validation_score
