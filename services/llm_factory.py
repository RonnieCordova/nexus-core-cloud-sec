import os
from services.gemini_provider import generar_respuesta_gemini
# importo el nuevo proveedor
from services.groq_provider import generar_respuesta_groq

def consultar_ia(prompt: str, system_prompt: str = "", historial: list = []):
    """
    Decido que cerebro usar segun la configuracion del .env
    """
    provider = os.getenv("LLM_PROVIDER", "gemini").lower()
    
    if provider == "groq":
        return generar_respuesta_groq(prompt, system_prompt, historial)
    else:
        # por defecto sigo teniendo gemini como respaldo
        return generar_respuesta_gemini(prompt, system_prompt, historial)