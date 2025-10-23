"""
Estilos CSS personalizados para la aplicación Streamlit
Colores y diseño moderno inspirado en Kavak
"""

# Colores de Kavak
KAVAK_ORANGE = "#FF6B35"
KAVAK_DARK = "#1A1A2E"
KAVAK_LIGHT = "#F7F7F7"
KAVAK_BLUE = "#0F3460"
KAVAK_GREEN = "#16DB93"

def get_custom_css():
    """
    Retorna el CSS personalizado para la aplicación.
    """
    return f"""
    <style>
    /* Importar fuente moderna */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    /* Estilos globales */
    .stApp {{
        background: linear-gradient(135deg, {KAVAK_LIGHT} 0%, #E8E8E8 100%);
        font-family: 'Inter', sans-serif;
    }}
    
    /* Header personalizado */
    .main-header {{
        background: linear-gradient(135deg, {KAVAK_ORANGE} 0%, #FF8C42 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        text-align: center;
    }}
    
    .main-header h1 {{
        color: white;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }}
    
    .main-header p {{
        color: white;
        font-size: 1.1rem;
        margin-top: 0.5rem;
        opacity: 0.95;
    }}
    
    /* Contenedor de chat */
    .chat-container {{
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        margin-bottom: 1rem;
    }}
    
    /* Mensajes del usuario */
    .user-message {{
        background: linear-gradient(135deg, {KAVAK_BLUE} 0%, #1A4D7A 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 20px 20px 5px 20px;
        margin: 1rem 0;
        margin-left: 20%;
        box-shadow: 0 2px 8px rgba(15, 52, 96, 0.3);
        animation: slideInRight 0.3s ease-out;
    }}
    
    /* Mensajes del bot */
    .bot-message {{
        background: linear-gradient(135deg, {KAVAK_ORANGE} 0%, #FF8C42 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 20px 20px 20px 5px;
        margin: 1rem 0;
        margin-right: 20%;
        box-shadow: 0 2px 8px rgba(255, 107, 53, 0.3);
        animation: slideInLeft 0.3s ease-out;
    }}
    
    /* Animaciones */
    @keyframes slideInRight {{
        from {{
            opacity: 0;
            transform: translateX(50px);
        }}
        to {{
            opacity: 1;
            transform: translateX(0);
        }}
    }}
    
    @keyframes slideInLeft {{
        from {{
            opacity: 0;
            transform: translateX(-50px);
        }}
        to {{
            opacity: 1;
            transform: translateX(0);
        }}
    }}
    
    /* Botones de feedback */
    .feedback-container {{
        display: flex;
        gap: 1rem;
        justify-content: center;
        margin-top: 1rem;
        padding: 0.5rem;
    }}
    
    .feedback-btn {{
        background: white;
        border: 2px solid {KAVAK_ORANGE};
        color: {KAVAK_ORANGE};
        padding: 0.5rem 1.5rem;
        border-radius: 25px;
        cursor: pointer;
        font-weight: 600;
        transition: all 0.3s ease;
        font-size: 1.1rem;
    }}
    
    .feedback-btn:hover {{
        background: {KAVAK_ORANGE};
        color: white;
        transform: scale(1.05);
    }}
    
    /* Input de chat */
    .stTextInput > div > div > input {{
        border-radius: 25px;
        border: 2px solid {KAVAK_ORANGE};
        padding: 1rem 1.5rem;
        font-size: 1rem;
    }}
    
    .stTextInput > div > div > input:focus {{
        border-color: {KAVAK_BLUE};
        box-shadow: 0 0 0 0.2rem rgba(255, 107, 53, 0.25);
    }}
    
    /* Botón de enviar */
    .stButton > button {{
        background: linear-gradient(135deg, {KAVAK_ORANGE} 0%, #FF8C42 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 10px rgba(255, 107, 53, 0.3);
    }}
    
    .stButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(255, 107, 53, 0.4);
    }}
    
    /* Sidebar */
    .css-1d391kg {{
        background: linear-gradient(180deg, {KAVAK_DARK} 0%, {KAVAK_BLUE} 100%);
    }}
    
    /* Métricas */
    .metric-card {{
        background: white;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border-left: 4px solid {KAVAK_ORANGE};
    }}
    
    .metric-card h3 {{
        color: {KAVAK_DARK};
        font-size: 1.2rem;
        margin: 0;
    }}
    
    .metric-card p {{
        color: {KAVAK_ORANGE};
        font-size: 2rem;
        font-weight: 700;
        margin: 0.5rem 0 0 0;
    }}
    
    /* Iconos */
    .icon {{
        font-size: 2rem;
        margin-right: 0.5rem;
    }}
    
    /* Badges */
    .badge {{
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 0.2rem;
    }}
    
    .badge-success {{
        background: {KAVAK_GREEN};
        color: white;
    }}
    
    .badge-warning {{
        background: {KAVAK_ORANGE};
        color: white;
    }}
    
    .badge-info {{
        background: {KAVAK_BLUE};
        color: white;
    }}
    
    /* Ocultar elementos de Streamlit */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    
    /* Scrollbar personalizado */
    ::-webkit-scrollbar {{
        width: 10px;
    }}
    
    ::-webkit-scrollbar-track {{
        background: {KAVAK_LIGHT};
    }}
    
    ::-webkit-scrollbar-thumb {{
        background: {KAVAK_ORANGE};
        border-radius: 5px;
    }}
    
    ::-webkit-scrollbar-thumb:hover {{
        background: #FF8C42;
    }}
    </style>
    """
