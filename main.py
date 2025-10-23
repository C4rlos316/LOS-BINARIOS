"""
Punto de entrada principal del Sistema de Chatbot Auto-Mejorable para Kavak
Versión refactorizada con arquitectura modular
"""

from langchain.schema import SystemMessage, HumanMessage, AIMessage

# Importar módulos del backend
from backend.utils.llm_config import LLMConfig
from backend.utils.database import DatabaseManager
from backend.utils.metrics import MetricsCalculator
from backend.agents.main_agent import MainAgent
from backend.agents.summarizer_agent import SummarizerAgent
from backend.agents.optimizer_agent import OptimizerAgent


def main():
    """
    Función principal del chatbot.
    """
    print("=" * 60)
    print("🚗 BIENVENIDO AL ASISTENTE VIRTUAL DE KAVAK 🚗")
    print("=" * 60)
    print("\nEscribe 'salir' en cualquier momento para terminar la conversación.\n")
    
    # Sistema de identificación de usuario
    print("=" * 60)
    print("IDENTIFICACIÓN DE USUARIO")
    print("=" * 60)
    print("\n1. ¿Eres un usuario nuevo o existente?")
    print("   [1] Usuario nuevo (crear ID)")
    print("   [2] Usuario existente (usar ID anterior)")
    
    opcion = input("\nSelecciona una opción (1 o 2): ").strip()
    
    if opcion == "1":
        # Usuario nuevo
        nombre = input("\nIngresa tu nombre: ").strip()
        if not nombre:
            print("❌ Error: Debes ingresar un nombre válido.")
            return
        
        # Generar ID único
        import hashlib
        from datetime import datetime
        unique_string = f"{nombre}_{datetime.now().isoformat()}"
        user_hash = hashlib.md5(unique_string.encode()).hexdigest()[:8]
        user_id = f"{nombre}_{user_hash}"
        
        print(f"\n✅ Usuario creado exitosamente!")
        print(f"📝 Tu ID de usuario es: {user_id}")
        print("⚠️  IMPORTANTE: Guarda este ID para futuras sesiones\n")
        input("Presiona Enter para continuar...")
        
    elif opcion == "2":
        # Usuario existente
        user_id = input("\nIngresa tu ID de usuario: ").strip()
        if not user_id:
            print("❌ Error: Debes ingresar un ID de usuario válido.")
            return
    else:
        print("❌ Opción inválida.")
        return
    
    print(f"\n✅ Sesión iniciada para usuario: {user_id}")
    print("\nCargando asistente...")
    
    # Inicializar componentes
    llm_config = LLMConfig.create_default()
    llm = llm_config.get_llm()
    
    db_manager = DatabaseManager()
    metrics_calculator = MetricsCalculator()
    
    # Inicializar agentes
    main_agent = MainAgent(llm)
    summarizer_agent = SummarizerAgent(llm)
    optimizer_agent = OptimizerAgent(llm)
    
    # Construir prompt del sistema
    rules = db_manager.get_all_rules()
    memory = db_manager.get_user_memory(user_id)
    system_prompt = main_agent.build_system_prompt(rules, memory)
    
    # Inicializar historial de chat
    chat_history = [SystemMessage(content=system_prompt)]
    
    print("\n" + "=" * 60)
    print("Puedes empezar a chatear con el asistente de Kavak")
    print("=" * 60)
    
    # Bucle principal de conversación
    while True:
        # Obtener input del usuario
        user_input = input("\n🧑 Tú: ").strip()
        
        # Verificar comando de salida
        if user_input.lower() == 'salir':
            # Aprendizaje automático de la conversación
            if len(chat_history) > 1:
                print("\n" + "="*70)
                print("Analizando conversación y aprendiendo automáticamente...")
                print("="*70)
                
                # APRENDIZAJE AUTOMÁTICO
                auto_learn_from_conversation(
                    chat_history, user_id, 
                    summarizer_agent, db_manager
                )
                
                # Calcular y mostrar métricas
                print("\nGenerando reporte de métricas...\n")
                metrics = metrics_calculator.calculate_metrics(chat_history)
                system_stats = db_manager.get_system_stats()
                metrics_calculator.display_metrics(metrics, system_stats)
            
            print("\n👋 ¡Gracias por usar el asistente de Kavak! Hasta pronto.")
            break
        
        # Validar que el input no esté vacío
        if not user_input:
            print("⚠️  Por favor, escribe algo.")
            continue
        
        # Añadir mensaje del usuario al historial
        chat_history.append(HumanMessage(content=user_input))
        
        # Mostrar mensaje de espera
        print("\n🤖 Kavak pensando...")
        
        try:
            # Llamar al Agente Principal
            ai_response_content = main_agent.respond(chat_history)
            
            # Mostrar respuesta
            print(f"\n🚗 Kavak: {ai_response_content}")
            
            # Añadir respuesta del bot al historial
            chat_history.append(AIMessage(content=ai_response_content))
            
            # Sistema de feedback OPCIONAL
            print("\n¿Quieres dar feedback? (si/no para forzar aprendizaje, Enter para continuar)")
            feedback = input("Tu feedback: ").strip().lower()
            
            if feedback == 'si' or feedback == 's':
                # Usar Agente Resumidor
                summary = summarizer_agent.summarize_conversation(chat_history)
                db_manager.save_user_memory(user_id, summary)
                print("\n[Sistema: ✓ Memoria guardada exitosamente. Esta información se recordará en futuras conversaciones.]")
                
            elif feedback == 'no' or feedback == 'n':
                # Usar Agente Optimizador
                try:
                    rule_text, error_category, validation_score = optimizer_agent.optimize(chat_history)
                    
                    # Guardar solo si la validación es positiva
                    if validation_score >= 0.5:
                        db_manager.save_rule(rule_text, error_category, validation_score)
                        print(f"\n[Sistema: ✓ Regla validada (score: {validation_score:.1f}) y guardada. Categoría: {error_category}]")
                        
                        # Reconstruir el prompt con la nueva regla
                        print("\n[Sistema: Aplicando mejora al asistente...]")
                        rules = db_manager.get_all_rules()
                        memory = db_manager.get_user_memory(user_id)
                        system_prompt = main_agent.build_system_prompt(rules, memory)
                        chat_history[0] = SystemMessage(content=system_prompt)
                        print("[Sistema: ✓ Asistente mejorado. Continuemos...]")
                    else:
                        print(f"\n[Sistema: ✗ Regla descartada (score: {validation_score:.1f}). No mejora las respuestas.]")
                        
                except ValueError as e:
                    print(f"\n[Sistema: ⚠️  {str(e)}]")
            
        except Exception as e:
            print(f"\n❌ Error al comunicarse con la IA: {str(e)}")
            print("Por favor, verifica tu configuración de API key en el archivo .env")
            break


def auto_learn_from_conversation(chat_history, user_id, summarizer_agent, db_manager):
    """
    Analiza automáticamente la conversación y aprende patrones exitosos.
    
    Args:
        chat_history: Historial de la conversación
        user_id: ID del usuario
        summarizer_agent: Instancia del agente resumidor
        db_manager: Instancia del gestor de BD
    """
    # Extraer interacciones
    interactions = []
    for i in range(len(chat_history)):
        if isinstance(chat_history[i], HumanMessage):
            if i + 1 < len(chat_history) and isinstance(chat_history[i+1], AIMessage):
                interactions.append({
                    'question': chat_history[i].content,
                    'answer': chat_history[i+1].content
                })
    
    if not interactions:
        return
    
    # Guardar memoria del usuario automáticamente
    if interactions:
        summary = summarizer_agent.summarize_conversation(chat_history)
        db_manager.save_user_memory(user_id, summary)
        print("\n[Sistema: El bot aprendió automáticamente de esta conversación]")


if __name__ == "__main__":
    main()
