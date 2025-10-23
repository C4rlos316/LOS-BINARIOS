import os
from dotenv import load_dotenv
from openai import OpenAI

# 1. Cargar variables de entorno (busca el archivo .env)
load_dotenv()

print("Intentando conectar con la API de OpenAI...")

# 2. Verificar si la key existe en el entorno
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("--------------------------------------------------")
    print("¡ERROR! No se encontró la variable OPENAI_API_KEY.")
    print("Asegúrate de tener un archivo .env en esta carpeta con tu key.")
    print("--------------------------------------------------")
else:
    try:
        # 3. Inicializar el cliente de OpenAI
        client = OpenAI() # El cliente lee la key automáticamente de las variables de entorno

        # 4. Hacer una llamada de prueba muy simple
        print("Key encontrada. Realizando llamada de prueba...")
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un asistente de prueba."},
                {"role": "user", "content": "Responde 'OK' si me escuchas."}
            ]
        )
        
        # 5. Imprimir la respuesta
        response = completion.choices[0].message.content
        print("--------------------------------------------------")
        print(f"Respuesta de la API: {response}")
        if "OK" in response.upper():
            print("¡ÉXITO! Tu API key funciona correctamente.")
        else:
            print("La API respondió, pero no lo esperado. Revisa la respuesta.")
        print("--------------------------------------------------")

    except Exception as e:
        print("--------------------------------------------------")
        print(f"¡ERROR! La llamada a la API falló.")
        print(f"Detalle del error: {e}")
        print("Verifica tu conexión a internet, tu API key o el estado de tu cuenta de OpenAI.")
        print("--------------------------------------------------")