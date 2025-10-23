import os
import sys
import urllib.request
from dotenv import load_dotenv
from openai import OpenAI
import httpx

# 1. Cargar variables de entorno (busca el archivo .env)
load_dotenv()

print("="*60)
print("DIAGNÓSTICO DE CONEXIÓN A LA API DE OPENAI")
print("="*60)

# Verificar conectividad a internet
print("\n[1/4] Verificando conectividad a internet...")
try:
    urllib.request.urlopen('https://www.google.com', timeout=5)
    print("✓ Conexión a internet OK")
except Exception as e:
    print(f"✗ ERROR: No hay conexión a internet")
    print(f"  Detalle: {e}")
    sys.exit(1)

# Verificar conectividad a OpenAI
print("\n[2/4] Verificando acceso a api.openai.com...")
try:
    urllib.request.urlopen('https://api.openai.com', timeout=10)
    print("✓ Acceso a OpenAI OK")
except Exception as e:
    print(f"✗ ADVERTENCIA: No se puede acceder a api.openai.com")
    print(f"  Detalle: {e}")
    print("  Esto puede indicar un problema de proxy o firewall")

print("\n[3/4] Verificando API Key...")

# 2. Verificar si la key existe en el entorno
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("✗ ERROR: No se encontró la variable OPENAI_API_KEY")
    print("  Asegúrate de tener un archivo .env con tu key")
    sys.exit(1)

print(f"✓ API Key encontrada (primeros 10 chars): {api_key[:10]}...")

print("\n[4/4] Realizando llamada de prueba a la API...")

try:
    # Limpiar variables de proxy del entorno antes de crear el cliente
    os.environ.pop('HTTP_PROXY', None)
    os.environ.pop('HTTPS_PROXY', None)
    os.environ.pop('http_proxy', None)
    os.environ.pop('https_proxy', None)
    
    # Configurar cliente con timeout más largo
    http_client = httpx.Client(timeout=30.0)
    client = OpenAI(http_client=http_client)

    print("  Enviando solicitud...")
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Eres un asistente de prueba."},
            {"role": "user", "content": "Responde 'OK' si me escuchas."}
        ]
    )
    
    response = completion.choices[0].message.content
    print("\n" + "="*60)
    print("✓ ¡ÉXITO! CONEXIÓN ESTABLECIDA")
    print("="*60)
    print(f"Respuesta de la API: {response}")
    print("\nTu configuración está funcionando correctamente.")
    print("="*60)

except httpx.ProxyError as e:
    print("\n" + "="*60)
    print("✗ ERROR DE PROXY DETECTADO")
    print("="*60)
    print(f"Detalle: {e}")
    print("\nSOLUCIONES POSIBLES:")
    print("1. Desactiva cualquier proxy en tu sistema")
    print("2. Configura las variables de entorno:")
    print("   set HTTP_PROXY=")
    print("   set HTTPS_PROXY=")
    print("3. Si estás en una red corporativa, contacta a tu administrador")
    print("="*60)
    
except httpx.ConnectError as e:
    print("\n" + "="*60)
    print("✗ ERROR DE CONEXIÓN")
    print("="*60)
    print(f"Detalle: {e}")
    print("\nSOLUCIONES POSIBLES:")
    print("1. Verifica tu conexión a internet")
    print("2. Desactiva VPN o proxy si los tienes activos")
    print("3. Verifica que no haya firewall bloqueando la conexión")
    print("4. Intenta desde otra red (ej: datos móviles)")
    print("="*60)
    
except Exception as e:
    print("\n" + "="*60)
    print("✗ ERROR AL CONECTAR CON LA API")
    print("="*60)
    print(f"Tipo de error: {type(e).__name__}")
    print(f"Detalle: {e}")
    print("\nVERIFICA:")
    print("1. Tu API key es válida y tiene créditos")
    print("2. No hay problemas de red o firewall")
    print("3. El servicio de OpenAI está operativo")
    print("="*60)