import os
import json
from groq import Groq
from services.iam_tool import analizar_politica_iam, IAM_TOOL_DOCS
from services.github_tool import crear_pull_request_seguridad, GITHUB_TOOL_DOCS

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generar_respuesta_groq(prompt: str, system_prompt: str, historial: list = []) -> str:
    MODELO = "llama-3.3-70b-versatile"
    # Reducimos el historial al mínimo para evitar que el modelo se confunda con logs viejos
    mensajes = [{"role": "system", "content": system_prompt}]
    for h in historial[-2:]: mensajes.append(h)
    mensajes.append({"role": "user", "content": prompt})

    herramientas = [{"type": "function", "function": IAM_TOOL_DOCS}, {"type": "function", "function": GITHUB_TOOL_DOCS}]

    try:
        # Turno 1: Decisión
        respuesta = client.chat.completions.create(
            model=MODELO, messages=mensajes, tools=herramientas, tool_choice="auto", temperature=0
        )
        msg = respuesta.choices[0].message
        
        if msg.tool_calls:
            mensajes.append(msg)
            for call in msg.tool_calls:
                args = json.loads(call.function.arguments)
                print(f"\n>>> EJECUTANDO: {call.function.name}") # Log de terminal
                
                if call.function.name == "analizar_politica_iam":
                    res = analizar_politica_iam(args.get("politica_json"))
                else:
                    res = crear_pull_request_seguridad(args.get("contenido_corregido"))
                
                mensajes.append({"tool_call_id": call.id, "role": "tool", "name": call.function.name, "content": res})
            
            # Turno 2: Respuesta final (aquí quitamos las herramientas para evitar el error 400)
            final = client.chat.completions.create(model=MODELO, messages=mensajes)
            return final.choices[0].message.content
        
        return msg.content
    except Exception as e:
        print(f"Error Agente Groq: {e}")
        return "Nexus detectó un fallo en el motor de ejecución. Revisa tu terminal."