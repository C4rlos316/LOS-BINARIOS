"""
Sistema de autenticación y gestión de usuarios
"""

import streamlit as st
import hashlib
from datetime import datetime


def generate_user_id(username: str) -> str:
    """
    Genera un ID único para el usuario basado en su nombre.
    
    Args:
        username: Nombre de usuario
    
    Returns:
        str: ID único del usuario
    """
    # Crear hash del username + timestamp para unicidad
    unique_string = f"{username}_{datetime.now().isoformat()}"
    user_hash = hashlib.md5(unique_string.encode()).hexdigest()[:8]
    return f"{username}_{user_hash}"


def render_login_screen():
    """
    Renderiza la pantalla de login/registro.
    
    Returns:
        str: user_id si el usuario se autenticó, None en caso contrario
    """
    st.markdown("""
    <div class="main-header">
        <h1>🚗 Bienvenido a Kavak</h1>
        <p>Identifícate para comenzar</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Contenedor de login
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div class="chat-container" style="padding: 2rem;">
            <h2 style="text-align: center; color: #FF6B35; margin-bottom: 1.5rem;">
                👤 Identificación de Usuario
            </h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Tabs para Login o Registro
        tab1, tab2 = st.tabs(["🔑 Iniciar Sesión", "✨ Nuevo Usuario"])
        
        with tab1:
            st.markdown("### Usuarios Existentes")
            st.markdown("Ingresa tu ID de usuario para continuar tu conversación anterior.")
            
            existing_user_id = st.text_input(
                "ID de Usuario",
                key="existing_user",
                placeholder="Ej: juan_a1b2c3d4",
                help="Tu ID único de usuario"
            )
            
            if st.button("🚀 Continuar", key="login_btn", use_container_width=True):
                if existing_user_id.strip():
                    return existing_user_id.strip()
                else:
                    st.error("⚠️ Por favor ingresa tu ID de usuario")
        
        with tab2:
            st.markdown("### Crear Nuevo Usuario")
            st.markdown("Ingresa tu nombre para crear un nuevo perfil.")
            
            new_username = st.text_input(
                "Tu Nombre",
                key="new_user",
                placeholder="Ej: Juan Pérez",
                help="Nombre que usarás para identificarte"
            )
            
            if st.button("✨ Crear Usuario", key="register_btn", use_container_width=True):
                if new_username.strip():
                    # Generar ID único
                    user_id = generate_user_id(new_username.strip())
                    
                    # Mostrar ID generado
                    st.success(f"✅ Usuario creado exitosamente!")
                    st.info(f"**Tu ID de usuario es:** `{user_id}`")
                    st.warning("⚠️ **Importante:** Guarda este ID para futuras sesiones")
                    
                    # Botón para continuar
                    if st.button("Continuar con este usuario", key="continue_new"):
                        return user_id
                else:
                    st.error("⚠️ Por favor ingresa tu nombre")
        
        # Información adicional
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; color: #666; font-size: 0.9rem;">
            <strong>¿Por qué necesito un ID?</strong><br>
            Tu ID permite que el sistema recuerde tus conversaciones anteriores<br>
            y personalice las respuestas según tu historial.
        </div>
        """, unsafe_allow_html=True)
    
    return None


def render_user_info_sidebar(user_id: str):
    """
    Renderiza información del usuario en el sidebar.
    
    Args:
        user_id: ID del usuario actual
    """
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 👤 Usuario Actual")
    
    # Extraer nombre del user_id
    username = user_id.split('_')[0] if '_' in user_id else user_id
    
    st.sidebar.markdown(f"""
    <div class="metric-card">
        <h3>Nombre</h3>
        <p style="font-size: 1.2rem; color: #0F3460;">{username}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown(f"""
    <div style="background: #F7F7F7; padding: 0.8rem; border-radius: 8px; margin-top: 0.5rem;">
        <strong style="font-size: 0.85rem; color: #666;">ID de Usuario:</strong><br>
        <code style="font-size: 0.75rem; color: #FF6B35;">{user_id}</code>
    </div>
    """, unsafe_allow_html=True)
    
    # Botón para cerrar sesión
    if st.sidebar.button("🚪 Cerrar Sesión", use_container_width=True):
        # Limpiar sesión
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()


def get_user_display_name(user_id: str) -> str:
    """
    Obtiene el nombre de visualización del usuario.
    
    Args:
        user_id: ID del usuario
    
    Returns:
        str: Nombre para mostrar
    """
    if '_' in user_id:
        return user_id.split('_')[0].title()
    return user_id.title()
