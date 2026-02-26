import os
from openai import OpenAI

# Inicializo el cliente asegurandome de jalar la key de las variables de entorno por seguridad
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("Falta la variable de entorno OPENAI_API_KEY. Revisar el archivo .env")

client = OpenAI(api_key=api_key)

def generar_respuesta(prompt: str, system_prompt: str = "Eres un asistente útil.") -> str:
    """
    Le envio el prompt del usuario y el contexto del sistema a OpenAI.
    Retorna solo el texto de la respuesta.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o", # O el modelo que prefiramos usar por costos (ej. gpt-4o-mini)
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7 # Un balance entre creatividad y coherencia
        )
        
        # Extraigo unicamente el texto de la respuesta que me da la API
        return response.choices[0].message.content
        
    except Exception as e:
        # Si algo falla con la API, lo atrapo aqui para que no se caiga todo el sistema
        print(f"Error al conectar con OpenAI: {e}")
        return "Hubo un error al procesar la solicitud."