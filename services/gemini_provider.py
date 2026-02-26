import os
from google import genai
from google.genai import types

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("Falta GEMINI_API_KEY en el archivo .env")

client = genai.Client(api_key=api_key)

# ACTUALIZACION: Recibimos el historial
def generar_respuesta_gemini(prompt: str, system_prompt: str = "Eres un asistente útil.", historial: list = []) -> str:
    try:
        config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.7 
        )
        
        # TRADUCTOR DE HISTORIAL: Convertimos nuestro formato generico al de Gemini
        formatted_contents = []
        for msg in historial:
            # Gemini usa 'model' en lugar de 'assistant'
            rol_gemini = "user" if msg["role"] == "user" else "model"
            formatted_contents.append(
                types.Content(role=rol_gemini, parts=[types.Part.from_text(text=msg["content"])])
            )
            
        # Al final, añadimos la nueva pregunta del usuario
        formatted_contents.append(
            types.Content(role="user", parts=[types.Part.from_text(text=prompt)])
        )
        
        # Le enviamos toda la lista construida (formatted_contents)
        response = client.models.generate_content(
            model='gemini-2.5-flash', 
            contents=formatted_contents,
            config=config
        )
        
        return response.text
        
    except Exception as e:
        print(f"Error al conectar con Gemini: {e}")
        return "Hubo un error al procesar la solicitud con Gemini."