import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict
from dotenv import load_dotenv

# importo slowapi para proteger la api de abusos de peticiones
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

load_dotenv()
from services.llm_factory import consultar_ia

# configuro el limitador usando la ip del usuario como identificador
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="Nexus Core API", version="1.0.0")

# le digo a fastapi que use mi limitador y defino como manejar el error visualmente
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.mount("/static", StaticFiles(directory="static"), name="static")

class ConsultaRequest(BaseModel):
    pregunta: str
    historial: List[Dict[str, str]] = []

# ACTUALIZACION: agrego el decorador de limite (5 peticiones por minuto por ip)
# NOTA: En FastAPI, cuando usamos limitadores, debemos inyectar el objeto 'Request' puro
@app.post("/api/consultar")
@limiter.limit("5/minute") 
def endpoint_consultar_ia(request: Request, body: ConsultaRequest):
    try:
        contexto_sistema = """
        Eres Nexus, un experto en ciberseguridad y desarrollo web. 
        Tus respuestas deben ser claras, estructuradas y precisas.
        
        REGLA CRÍTICA:
        Si el usuario te pregunta sobre temas fuera de tu dominio, 
        responde basándote en el historial si es posible, pero 
        añade una breve advertencia de que no es tu campo. 
        NO inventes términos técnicos.
        """
        
        # extraigo los datos del body que ya paso la validacion
        respuesta_ia = consultar_ia(
            prompt=body.pregunta, 
            system_prompt=contexto_sistema,
            historial=body.historial
        )
        
        return {
            "status": "success",
            "modelo_activo": os.getenv("LLM_PROVIDER", "gemini").upper(),
            "respuesta": respuesta_ia
        }
    except Exception as e:
        print(f"Error en endpoint: {e}")
        raise HTTPException(status_code=500, detail="Error interno al procesar la solicitud.")

@app.get("/")
def serve_index():
    return FileResponse("static/index.html")