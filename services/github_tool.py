import os
import requests
import base64

def crear_pull_request_seguridad(contenido_corregido: str) -> str:
    token = os.getenv("GITHUB_TOKEN")
    repo = os.getenv("GITHUB_REPO")
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
    url = f"https://api.github.com/repos/{repo}"

    try:
        # 1. Obtener SHA de main
        ref_res = requests.get(f"{url}/git/refs/heads/main", headers=headers)
        if ref_res.status_code != 200:
            return f"Error GitHub ({ref_res.status_code}): {ref_res.json().get('message')}"
        
        sha_base = ref_res.json()['object']['sha']
        branch_name = f"nexus-fix-{os.urandom(2).hex()}"

        # 2. Crear rama
        requests.post(f"{url}/git/refs", headers=headers, json={"ref": f"refs/heads/{branch_name}", "sha": sha_base})

        # 3. Crear archivo
        content_b64 = base64.b64encode(contenido_corregido.encode()).decode()
        requests.put(f"{url}/contents/iam_policy_fix.json", headers=headers, json={
            "message": "fix: restringir privilegios excesivos",
            "content": content_b64,
            "branch": branch_name
        })

        # 4. Crear PR
        pr_res = requests.post(f"{url}/pulls", headers=headers, json={
            "title": "🛡️ Nexus Core: Parche de Seguridad",
            "body": "Remediación automática de política IAM.",
            "head": branch_name, "base": "main"
        })

        if pr_res.status_code == 201:
            url_pr = pr_res.json().get('html_url')
            print(f">>> ÉXITO: PR creado en {url_pr}")
            return f"¡PR Creado! Puedes revisarlo aquí: {url_pr}"
        
        # Si falla, imprimimos el error real en la terminal
        print(f">>> FALLO GITHUB: {pr_res.json()}")
        return f"GitHub rechazó el PR: {pr_res.json().get('message')}"

    except Exception as e:
        return f"Error en el script de GitHub: {str(e)}"