import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict
from dotenv import load_dotenv

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

load_dotenv()
from services.llm_factory import consultar_ia

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Nexus Core")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.mount("/static", StaticFiles(directory="static"), name="static")

class RequestBody(BaseModel):
    pregunta: str
    historial: List[Dict[str, str]] = []

@app.post("/api/consultar")
@limiter.limit("10/minute")
async def chat(request: Request, body: RequestBody): # 'request' es obligatorio aquí
    try:
        # Dentro de main.py, cambia el system_prompt por este:
        system = """Eres Nexus Core, un Arquitecto de Seguridad Cloud.
Tu misión es auditar y REPARAR infraestructuras.

REGLAS DE ORO:
1. Analiza el JSON usando 'analizar_politica_iam'.
2. Sé imparcial: explica los PROS (funcionalidad) y CONTRAS (riesgo crítico) del JSON.
3. SIEMPRE pide confirmación antes de abrir un PR.
4. Si ejecutas 'crear_pull_request_seguridad', tu respuesta DEBE incluir la URL que devuelve la herramienta. 
5. NO inventes URLs ni digas que lo hiciste si la herramienta no devuelve éxito."""
        
        res = consultar_ia(prompt=body.pregunta, system_prompt=system, historial=body.historial)
        return {"respuesta": res}
    except Exception as e:
        print(f"Error en main: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def home(): return FileResponse("static/index.html")