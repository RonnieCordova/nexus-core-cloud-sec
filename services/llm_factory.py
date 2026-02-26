import os
from services.openai_provider import generar_respuesta as ask_openai
from services.gemini_provider import generar_respuesta_gemini as ask_gemini

# ACTUALIZACION: Agregamos el parametro historial
def consultar_ia(prompt: str, system_prompt: str, historial: list = []) -> str:
    """
    Enruta la peticion con todo y su historial al modelo configurado.
    """
    proveedor = os.getenv("LLM_PROVIDER", "gemini").lower()
    
    if proveedor == "openai":
        return ask_openai(prompt, system_prompt, historial) # Nota: openai_provider aun no lo soporta, lo actualizaremos cuando volvamos a el.
        
    elif proveedor == "gemini":
        return ask_gemini(prompt, system_prompt, historial)
        
    else:
        return "Proveedor de IA no soportado."