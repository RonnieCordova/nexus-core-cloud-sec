import json

def analizar_politica_iam(politica_json: str) -> str:
    """
    Analiza una política de AWS IAM buscando privilegios excesivos.
    """
    try:
        data = json.loads(politica_json)
        hallazgos = []
        statements = data.get("Statement", [])
        if isinstance(statements, dict): 
            statements = [statements]
            
        for s in statements:
            # Buscamos el temido "estrella" que da acceso total
            if s.get("Effect") == "Allow" and s.get("Action") == "*":
                hallazgos.append("- CRÍTICO: Permite TODAS las acciones (*).")
            if s.get("Effect") == "Allow" and s.get("Resource") == "*":
                hallazgos.append("- RIESGO: Permite acceso a TODOS los recursos (*).")

        if not hallazgos:
            return "Seguridad confirmada: No se detectaron comodines peligrosos."
        
        return "Reporte de Vulnerabilidades:\n" + "\n".join(hallazgos)
    except Exception as e:
        return f"Error de formato JSON: {str(e)}"

# Definición para que la IA entienda cómo usar esta función
IAM_TOOL_DOCS = {
    "name": "analizar_politica_iam",
    "description": "Escanea una política de AWS IAM en JSON para detectar riesgos de seguridad.",
    "parameters": {
        "type": "object",  # CORREGIDO: minúsculas
        "properties": {
            "politica_json": {
                "type": "string",  # CORREGIDO: minúsculas
                "description": "El JSON de la política a analizar."
            }
        },
        "required": ["politica_json"]
    }
}