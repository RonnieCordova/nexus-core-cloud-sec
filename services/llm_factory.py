import os
from services.openai_provider import generar_respuesta_openai

def consultar_ia(prompt: str, system_prompt: str = "", historial: list = []):
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    
    if provider == "openai":
        return generar_respuesta_openai(prompt, system_prompt, historial)
    else:
        return "Proveedor no soportado actualmente."