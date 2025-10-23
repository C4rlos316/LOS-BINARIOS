"""
Componentes reutilizables de UI para Streamlit
"""

import streamlit as st


def render_header():
    """
    Renderiza el header principal de la aplicación.
    """
    st.markdown("""
    <div class="main-header">
        <h1>🚗 Asistente Virtual de Kavak</h1>
        <p>Tu compañero inteligente para comprar y vender autos seminuevos</p>
    </div>
    """, unsafe_allow_html=True)


def render_user_message(message: str):
    """
    Renderiza un mensaje del usuario.
    
    Args:
        message: Texto del mensaje
    """
    st.markdown(f"""
    <div class="user-message">
        <strong>👤 Tú:</strong><br>
        {message}
    </div>
    """, unsafe_allow_html=True)


def render_bot_message(message: str):
    """
    Renderiza un mensaje del bot.
    
    Args:
        message: Texto del mensaje
    """
    st.markdown(f"""
    <div class="bot-message">
        <strong>🚗 Kavak:</strong><br>
        {message}
    </div>
    """, unsafe_allow_html=True)


def render_feedback_buttons(message_index: int):
    """
    Renderiza botones de feedback (pulgar arriba/abajo).
    
    Args:
        message_index: Índice del mensaje para identificar el feedback
    
    Returns:
        str: 'up', 'down', o None
    """
    col1, col2, col3 = st.columns([1, 1, 1])
    
    feedback = None
    
    with col2:
        subcol1, subcol2 = st.columns(2)
        
        with subcol1:
            if st.button("👍", key=f"up_{message_index}", help="Respuesta útil"):
                feedback = 'up'
        
        with subcol2:
            if st.button("👎", key=f"down_{message_index}", help="Respuesta no útil"):
                feedback = 'down'
    
    return feedback


def render_metrics_sidebar(stats: dict):
    """
    Renderiza métricas en el sidebar.
    
    Args:
        stats: Diccionario con estadísticas del sistema
    """
    st.sidebar.markdown("### 📊 Estadísticas del Sistema")
    
    st.sidebar.markdown(f"""
    <div class="metric-card">
        <h3>🧠 Reglas Aprendidas</h3>
        <p>{stats.get('total_rules', 0)}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown(f"""
    <div class="metric-card">
        <h3>💾 Memorias Guardadas</h3>
        <p>{stats.get('total_memories', 0)}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Nivel de madurez
    maturity = min(100, (stats.get('total_rules', 0) * 10) + (stats.get('total_memories', 0) * 2))
    
    st.sidebar.markdown(f"""
    <div class="metric-card">
        <h3>🎯 Nivel de Madurez</h3>
        <p>{maturity}/100</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.progress(maturity / 100)
    
    # Clasificación
    if maturity >= 80:
        badge = '<span class="badge badge-success">🏆 Sistema Maduro</span>'
    elif maturity >= 50:
        badge = '<span class="badge badge-warning">📈 En Crecimiento</span>'
    elif maturity >= 20:
        badge = '<span class="badge badge-info">🌱 Sistema Inicial</span>'
    else:
        badge = '<span class="badge badge-info">🆕 Sistema Nuevo</span>'
    
    st.sidebar.markdown(badge, unsafe_allow_html=True)


def render_info_sidebar():
    """
    Renderiza información adicional en el sidebar.
    """
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ℹ️ Información")
    
    st.sidebar.markdown("""
    **¿Cómo funciona?**
    
    1. 🗣️ Haz preguntas sobre Kavak
    2. 🤖 El bot responde con información
    3. 👍👎 Da feedback con los botones
    4. 🧠 El sistema aprende automáticamente
    
    **Temas disponibles:**
    - 🚗 Compra de autos
    - 💰 Venta de autos
    - 💳 Financiamiento
    - 🛡️ Garantías
    - 🔍 Inspección de 240 puntos
    """)
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.85rem;">
        <strong>LOS BINARIOS</strong><br>
        Sistema de Chatbot Auto-Mejorable<br>
        v1.0.0
    </div>
    """, unsafe_allow_html=True)


def render_welcome_message(user_name: str = None):
    """
    Renderiza mensaje de bienvenida inicial.
    
    Args:
        user_name: Nombre del usuario (opcional)
    """
    greeting = f"¡Bienvenido, {user_name}! 👋" if user_name else "¡Bienvenido a Kavak! 👋"
    
    st.markdown(f"""
    <div class="chat-container" style="text-align: center; padding: 3rem;">
        <h2 style="color: #FF6B35;">{greeting}</h2>
        <p style="font-size: 1.1rem; color: #666; margin-top: 1rem;">
            Soy tu asistente virtual. Puedo ayudarte con:
        </p>
        <div style="display: flex; justify-content: center; gap: 2rem; margin-top: 2rem; flex-wrap: wrap;">
            <div style="text-align: center;">
                <div style="font-size: 3rem;">🚗</div>
                <p style="font-weight: 600; color: #1A1A2E;">Comprar autos</p>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 3rem;">💰</div>
                <p style="font-weight: 600; color: #1A1A2E;">Vender tu auto</p>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 3rem;">💳</div>
                <p style="font-weight: 600; color: #1A1A2E;">Financiamiento</p>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 3rem;">🛡️</div>
                <p style="font-weight: 600; color: #1A1A2E;">Garantías</p>
            </div>
        </div>
        <p style="font-size: 1rem; color: #999; margin-top: 2rem;">
            Escribe tu pregunta abajo para comenzar 👇
        </p>
    </div>
    """, unsafe_allow_html=True)


def render_thinking_animation():
    """
    Renderiza animación de "pensando".
    """
    st.markdown("""
    <div class="bot-message" style="text-align: center;">
        <strong>🚗 Kavak está pensando</strong>
        <span style="animation: blink 1.5s infinite;">...</span>
    </div>
    <style>
    @keyframes blink {
        0%, 100% { opacity: 0; }
        50% { opacity: 1; }
    }
    </style>
    """, unsafe_allow_html=True)
