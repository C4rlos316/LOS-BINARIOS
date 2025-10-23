import os
from dotenv import load_dotenv
from openai import OpenAI

# 1. Cargar el .env
load_dotenv()

print("Realizando prueba de información...")

try:
    # 2. Inicializar el cliente
    client = OpenAI()

    # 3. Hacer una pregunta real
    completion = client.chat.completions.create(
      model="gpt-3.5-turbo",
      messages=[
        {"role": "user", "content": "Explica brevemente qué es Kavak."}
      ]
    )

    # 4. Imprimir la respuesta
    response_text = completion.choices[0].message.content
    
    print("----------------------------------")
    print("Respuesta de la API:")
    print(response_text)
    print("----------------------------------")
    print("¡Éxito! La API está conectada y procesando información.")

except Exception as e:
    print("**********************************")
    print(f"¡ERROR! No se pudo conectar.")
    print(f"Detalle: {e}")
    print("**********************************")