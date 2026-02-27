import os
import json
from openai import OpenAI
from services.security_audit_tool import realizar_auditoria_tf, AUDIT_TOOL_DOCS
from services.github_tool import crear_pull_request_seguridad, GITHUB_TOOL_DOCS

# inicializo cliente de openai
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generar_respuesta_openai(prompt: str, system_prompt: str, historial: list = []) -> str:
    MODELO = "gpt-4o"
    
    mensajes = [{"role": "system", "content": system_prompt}]
    for h in historial[-4:]:
        mensajes.append(h)
    mensajes.append({"role": "user", "content": prompt})

    # agrego ambas herramientas al agente
    herramientas = [
        {"type": "function", "function": AUDIT_TOOL_DOCS},
        {"type": "function", "function": GITHUB_TOOL_DOCS}
    ]

    try:
        respuesta = client.chat.completions.create(
            model=MODELO,
            messages=mensajes,
            tools=herramientas,
            temperature=0.2
        )

        msg = respuesta.choices[0].message
        
        if msg.tool_calls:
            mensajes.append(msg)
            for call in msg.tool_calls:
                func_name = call.function.name
                args = json.loads(call.function.arguments)
                
                print(f"--- NEXUS EJECUTANDO: {func_name} ---")
                
                # enrutamiento de la accion
                if func_name == "realizar_auditoria_tf":
                    resultado = realizar_auditoria_tf(args.get("codigo_terraform"))
                elif func_name == "crear_pull_request_seguridad":
                    resultado = crear_pull_request_seguridad(args.get("contenido_corregido"))
                else:
                    resultado = "Accion no soportada."
                
                mensajes.append({
                    "tool_call_id": call.id,
                    "role": "tool",
                    "name": func_name,
                    "content": resultado
                })
            
            # segunda pasada con los datos de la funcion
            final = client.chat.completions.create(model=MODELO, messages=mensajes)
            return final.choices[0].message.content
        
        return msg.content

    except Exception as e:
        print(f"Error OpenAI: {e}")
        return "Nexus detectó un fallo crítico de conexión con el motor principal."