import re

def realizar_auditoria_tf(codigo_terraform: str) -> str:
    # busco patrones de vulnerabilidad criticos en el texto
    hallazgos = []
    
    # 1. exposicion publica en sg (0.0.0.0/0)
    if "0.0.0.0/0" in codigo_terraform:
        hallazgos.append("- RIESGO ALTO: Se detectó un bloque CIDR 0.0.0.0/0. Esto expone el recurso a todo internet. Corrección: Limita el ingreso a IPs específicas o rangos de VPC.")
    
    # 2. buckets de s3 expuestos
    if re.search(r'acl\s*=\s*"public-read"', codigo_terraform):
        hallazgos.append("- RIESGO CRÍTICO: El Bucket S3 tiene ACL 'public-read'. Corrección: Cambiar a 'private' o usar Bucket Policies estrictas.")
        
    if not hallazgos:
        return "Análisis de Infraestructura: No se encontraron vulnerabilidades evidentes en la configuración provista."
    
    return "Auditoría Terraform Completada. Hallazgos:\n" + "\n".join(hallazgos)

AUDIT_TOOL_DOCS = {
    "name": "realizar_auditoria_tf",
    "description": "Analiza código de infraestructura de Terraform (.tf) para identificar configuraciones inseguras.",
    "parameters": {
        "type": "object",
        "properties": {
            "codigo_terraform": {
                "type": "string",
                "description": "El bloque de código Terraform a analizar."
            }
        },
        "required": ["codigo_terraform"]
    }
}