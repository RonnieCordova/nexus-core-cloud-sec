import os
import time
from google import genai
from google.genai import types, errors
from services.iam_tool import analizar_politica_iam, IAM_TOOL_DOCS
from services.github_tool import crear_pull_request_seguridad, GITHUB_TOOL_DOCS

# Inicializamos el cliente una sola vez
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def generar_respuesta_gemini(prompt: str, system_prompt: str, historial: list = []) -> str:
    # Usamos el modelo que sabemos que existe en tu cuenta
    MODEL_ID = 'gemini-2.0-flash' 
    
    try:
        tools = [{ "function_declarations": [IAM_TOOL_DOCS, GITHUB_TOOL_DOCS] }]
        config = types.GenerateContentConfig(
            system_instruction=system_prompt, 
            tools=tools, 
            temperature=0.0
        )
        
        # Mantenemos el historial ligero para ahorrar tokens de tu cuota gratuita
        contents = [types.Content(role="user" if m["role"] == "user" else "model", 
                    parts=[types.Part.from_text(text=m["content"])]) for m in historial]
        contents.append(types.Content(role="user", parts=[types.Part.from_text(text=prompt)]))

        # Primera llamada: Razonamiento del agente
        response = client.models.generate_content(model=MODEL_ID, contents=contents, config=config)
        
        # Procesamiento de herramientas
        while response.candidates[0].content.parts and response.candidates[0].content.parts[0].function_call:
            call = response.candidates[0].content.parts[0].function_call
            print(f"DEBUG: Nexus ejecutando herramienta -> {call.name}")
            
            if call.name == "analizar_politica_iam":
                result = analizar_politica_iam(call.args["politica_json"])
            elif call.name == "crear_pull_request_seguridad":
                result = crear_pull_request_seguridad(call.args["contenido_corregido"])
            else:
                result = "Error: Herramienta no reconocida."
            
            # Devolvemos el resultado al modelo para que genere la respuesta final
            response = client.models.generate_content(
                model=MODEL_ID,
                contents=contents + [
                    response.candidates[0].content, 
                    types.Content(role="user", parts=[
                        types.Part.from_function_response(name=call.name, response={"result": result})
                    ])
                ],
                config=config
            )
            
        return response.text

    except errors.ClientError as e:
        # Manejo de cuota (429) para que el usuario sepa que debe esperar
        if "429" in str(e):
            return "⚠️ **Capacidad Temporal Alcanzada:** Nexus ha agotado su cuota de procesamiento gratuita. Por favor, espera 60 segundos y vuelve a intentarlo."
        return f"Error de la API de Google: {str(e)}"
    except Exception as e:
        print(f"Error interno: {e}")
        return "Nexus ha encontrado un error inesperado al procesar la solicitud."