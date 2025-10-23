"""
Aplicación Web del Chatbot de Kavak con Streamlit
Interfaz moderna, colorida e intuitiva con feedback de pulgares
"""

import streamlit as st
from langchain.schema import SystemMessage, HumanMessage, AIMessage

# Importar módulos del backend
from backend.utils.llm_config import LLMConfig
from backend.utils.database import DatabaseManager
from backend.agents.main_agent import MainAgent
from backend.agents.summarizer_agent import SummarizerAgent
from backend.agents.optimizer_agent import OptimizerAgent

# Importar componentes de UI
from frontend.ui.styles import get_custom_css
from frontend.ui.components import (
    render_header,
    render_user_message,
    render_bot_message,
    render_feedback_buttons,
    render_metrics_sidebar,
    render_info_sidebar,
    render_welcome_message,
    render_thinking_animation
)
from frontend.ui.auth import (
    render_login_screen,
    render_user_info_sidebar,
    get_user_display_name
)


# Configuración de la página
st.set_page_config(
    page_title="Kavak - Asistente Virtual",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)


def initialize_session_state():
    """
    Inicializa el estado de la sesión de Streamlit.
    """
    if 'initialized' not in st.session_state:
        # Inicializar componentes del backend
        llm_config = LLMConfig.create_default()
        st.session_state.llm = llm_config.get_llm()
        
        st.session_state.db_manager = DatabaseManager()
        st.session_state.main_agent = MainAgent(st.session_state.llm)
        st.session_state.summarizer_agent = SummarizerAgent(st.session_state.llm)
        st.session_state.optimizer_agent = OptimizerAgent(st.session_state.llm)
        
        # Flag de inicialización
        st.session_state.initialized = True
    
    # Inicializar user_id si no existe
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    
    # Inicializar historial de chat por usuario
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
        st.session_state.messages = []


def rebuild_system_prompt():
    """
    Reconstruye el prompt del sistema con reglas y memoria actualizadas.
    """
    rules = st.session_state.db_manager.get_all_rules()
    memory = st.session_state.db_manager.get_user_memory(st.session_state.user_id)
    system_prompt = st.session_state.main_agent.build_system_prompt(rules, memory)
    
    # Actualizar historial con nuevo prompt
    if st.session_state.chat_history:
        st.session_state.chat_history[0] = SystemMessage(content=system_prompt)
    else:
        st.session_state.chat_history = [SystemMessage(content=system_prompt)]


def handle_user_input(user_input: str):
    """
    Maneja el input del usuario y genera respuesta.
    
    Args:
        user_input: Texto ingresado por el usuario
    """
    # Agregar mensaje del usuario al historial
    st.session_state.chat_history.append(HumanMessage(content=user_input))
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Generar respuesta del bot
    with st.spinner(""):
        try:
            ai_response = st.session_state.main_agent.respond(st.session_state.chat_history)
            
            # Agregar respuesta al historial
            st.session_state.chat_history.append(AIMessage(content=ai_response))
            st.session_state.messages.append({
                "role": "assistant", 
                "content": ai_response,
                "feedback": None
            })
        except Exception as e:
            st.error(f"❌ Error al comunicarse con la IA: {str(e)}")


def handle_feedback(message_index: int, feedback_type: str):
    """
    Maneja el feedback del usuario (pulgar arriba/abajo).
    
    Args:
        message_index: Índice del mensaje
        feedback_type: 'up' o 'down'
    """
    # Marcar feedback en el mensaje
    st.session_state.messages[message_index]['feedback'] = feedback_type
    
    if feedback_type == 'up':
        # Feedback positivo: guardar memoria
        try:
            summary = st.session_state.summarizer_agent.summarize_conversation(
                st.session_state.chat_history
            )
            st.session_state.db_manager.save_user_memory(st.session_state.user_id, summary)
            st.success("✅ ¡Gracias! Memoria guardada para mejorar futuras conversaciones.")
        except Exception as e:
            st.error(f"Error al guardar memoria: {str(e)}")
    
    elif feedback_type == 'down':
        # Feedback negativo: optimizar
        try:
            with st.spinner("Analizando y aprendiendo..."):
                rule_text, error_category, validation_score = st.session_state.optimizer_agent.optimize(
                    st.session_state.chat_history
                )
                
                if validation_score >= 0.5:
                    st.session_state.db_manager.save_rule(rule_text, error_category, validation_score)
                    rebuild_system_prompt()
                    st.success(f"✅ ¡Gracias! El sistema aprendió una nueva regla (categoría: {error_category})")
                else:
                    st.warning("⚠️ Gracias por el feedback. Trabajaremos en mejorar esta respuesta.")
        except Exception as e:
            st.error(f"Error al optimizar: {str(e)}")


def main():
    """
    Función principal de la aplicación.
    """
    # Aplicar estilos personalizados
    st.markdown(get_custom_css(), unsafe_allow_html=True)
    
    # Inicializar estado de sesión
    initialize_session_state()
    
    # SISTEMA DE LOGIN
    if st.session_state.user_id is None:
        # Mostrar pantalla de login
        user_id = render_login_screen()
        
        if user_id:
            # Usuario se identificó
            st.session_state.user_id = user_id
            
            # Inicializar chat para este usuario
            st.session_state.chat_history = []
            st.session_state.messages = []
            
            # Construir prompt inicial con memoria del usuario
            rebuild_system_prompt()
            
            st.rerun()
        
        return  # No mostrar el chat hasta que se identifique
    
    # USUARIO YA IDENTIFICADO - Mostrar chat
    
    # Renderizar header
    render_header()
    
    # Sidebar con métricas y usuario
    stats = st.session_state.db_manager.get_system_stats()
    render_metrics_sidebar(stats)
    render_user_info_sidebar(st.session_state.user_id)
    render_info_sidebar()
    
    # Área principal de chat
    chat_container = st.container()
    
    with chat_container:
        # Mostrar mensaje de bienvenida si no hay mensajes
        if not st.session_state.messages:
            user_name = get_user_display_name(st.session_state.user_id)
            render_welcome_message(user_name)
        else:
            # Mostrar historial de mensajes
            for idx, message in enumerate(st.session_state.messages):
                if message["role"] == "user":
                    render_user_message(message["content"])
                else:
                    render_bot_message(message["content"])
                    
                    # Mostrar botones de feedback solo si no se ha dado feedback
                    if message.get("feedback") is None:
                        feedback = render_feedback_buttons(idx)
                        
                        if feedback:
                            handle_feedback(idx, feedback)
                            st.rerun()
                    else:
                        # Mostrar feedback dado
                        if message["feedback"] == "up":
                            st.markdown("""
                            <div style="text-align: center; color: #16DB93; font-size: 0.9rem; margin-top: 0.5rem;">
                                ✅ Marcaste esta respuesta como útil
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown("""
                            <div style="text-align: center; color: #FF6B35; font-size: 0.9rem; margin-top: 0.5rem;">
                                ⚠️ Marcaste esta respuesta como no útil - El sistema aprendió de esto
                            </div>
                            """, unsafe_allow_html=True)
    
    # Input del usuario (siempre al final)
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([5, 1])
    
    with col1:
        user_input = st.text_input(
            "Escribe tu pregunta aquí...",
            key="user_input",
            placeholder="Ej: ¿Qué garantías tienen los autos?",
            label_visibility="collapsed"
        )
    
    with col2:
        send_button = st.button("Enviar 🚀", use_container_width=True)
    
    # Procesar input
    if send_button and user_input:
        handle_user_input(user_input)
        st.rerun()
    
    # Botón para limpiar conversación
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🗑️ Limpiar Conversación", use_container_width=False):
        st.session_state.messages = []
        rebuild_system_prompt()
        st.rerun()


if __name__ == "__main__":
    main()
