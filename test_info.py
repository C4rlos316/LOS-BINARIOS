import os
from dotenv import load_dotenv
from openai import OpenAI
import httpx

# 1. Cargar el .env
load_dotenv()

print("="*60)
print("PRUEBA DE INFORMACIÓN - API DE OPENAI")
print("="*60)

try:
    # 2. Limpiar variables de proxy del entorno
    os.environ.pop('HTTP_PROXY', None)
    os.environ.pop('HTTPS_PROXY', None)
    os.environ.pop('http_proxy', None)
    os.environ.pop('https_proxy', None)
    
    # Inicializar el cliente con timeout más largo
    http_client = httpx.Client(timeout=30.0)
    client = OpenAI(http_client=http_client)

    print("\nEnviando pregunta a la API...")
    
    # 3. Hacer una pregunta real
    completion = client.chat.completions.create(
      model="gpt-3.5-turbo",
      messages=[
        {"role": "user", "content": "Explica brevemente qué es Kavak."}
      ]
    )

    # 4. Imprimir la respuesta
    response_text = completion.choices[0].message.content
    
    print("\n" + "="*60)
    print("✓ RESPUESTA DE LA API:")
    print("="*60)
    print(response_text)
    print("="*60)
    print("\n¡Éxito! La API está conectada y procesando información.")

except httpx.ProxyError as e:
    print("\n" + "="*60)
    print("✗ ERROR DE PROXY")
    print("="*60)
    print(f"Detalle: {e}")
    print("\nEjecuta en PowerShell:")
    print("  $env:HTTP_PROXY=''")
    print("  $env:HTTPS_PROXY=''")
    print("="*60)
    
except httpx.ConnectError as e:
    print("\n" + "="*60)
    print("✗ ERROR DE CONEXIÓN")
    print("="*60)
    print(f"Detalle: {e}")
    print("\nVerifica tu conexión a internet o desactiva VPN/proxy")
    print("="*60)
    
except Exception as e:
    print("\n" + "="*60)
    print("✗ ERROR AL CONECTAR")
    print("="*60)
    print(f"Tipo: {type(e).__name__}")
    print(f"Detalle: {e}")
    print("="*60)