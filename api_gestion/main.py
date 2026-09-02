"""
main.py — El arranque de la API del módulo Gestión Profesoral.

Arma la aplicación y registra el router. Nada más: la lógica vive en las
capas, no aquí.

Arranque:  uvicorn main:app --port 8029 --reload
Contratos: http://localhost:8029/docs
"""

from fastapi import FastAPI

from controllers.programa_controller import router as router_programa

app = FastAPI(
    title="API Gestión Profesoral",
    description="Módulo Gestión Profesoral — versión 1: el CRUD de programa.",
    version="v1",
)

app.include_router(router_programa)


@app.get("/")
async def diagnostico():
    """Responde sin tocar la base: sirve para saber si la API está viva."""
    return {"mensaje": "API Gestión Profesoral — módulo de programa",
            "version": "v1", "contratos": "/docs"}
