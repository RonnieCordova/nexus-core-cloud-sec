import os
import requests
import base64

def crear_pull_request_seguridad(contenido_corregido: str) -> str:
    # Variables de entorno para la conexion
    token = os.getenv("GITHUB_TOKEN")
    repo = os.getenv("GITHUB_REPO")
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
    url = f"https://api.github.com/repos/{repo}"

    try:
        # 1. Obtener el SHA de la rama main
        ref_res = requests.get(f"{url}/git/refs/heads/main", headers=headers)
        if ref_res.status_code != 200:
            return f"Error GitHub ({ref_res.status_code}): {ref_res.json().get('message')}"
        
        sha_base = ref_res.json()['object']['sha']
        branch_name = f"nexus-fix-{os.urandom(2).hex()}"

        # 2. Crear una rama nueva
        requests.post(f"{url}/git/refs", headers=headers, json={"ref": f"refs/heads/{branch_name}", "sha": sha_base})

        # 3. Crear el archivo con el parche
        content_b64 = base64.b64encode(contenido_corregido.encode()).decode()
        requests.put(f"{url}/contents/iam_policy_fix.json", headers=headers, json={
            "message": "fix: restringir privilegios excesivos",
            "content": content_b64,
            "branch": branch_name
        })

        # 4. Crear el Pull Request oficial
        pr_res = requests.post(f"{url}/pulls", headers=headers, json={
            "title": "🛡️ Nexus Core: Parche de Seguridad",
            "body": "Remediacion automatica de politica IAM detectada como insegura.",
            "head": branch_name, 
            "base": "main"
        })

        if pr_res.status_code == 201:
            url_pr = pr_res.json().get('html_url')
            return f"Exito: PR creado en {url_pr}"
        
        return f"GitHub rechazo el PR: {pr_res.json().get('message')}"

    except Exception as e:
        return f"Error en el script de GitHub: {str(e)}"

# --- ESTA ES LA DEFINICION QUE FALTABA ---
GITHUB_TOOL_DOCS = {
    "name": "crear_pull_request_seguridad",
    "description": "Crea un Pull Request con la politica corregida en el repositorio de GitHub.",
    "parameters": {
        "type": "object",
        "properties": {
            "contenido_corregido": {
                "type": "string",
                "description": "El JSON de la politica de seguridad ya corregida."
            }
        },
        "required": ["contenido_corregido"]
    }
}