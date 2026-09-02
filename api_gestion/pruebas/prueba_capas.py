"""
prueba_capas.py — El servicio SIN base de datos.

Enchufa al servicio un repositorio de mentiras que guarda las filas en una
lista. Si esta prueba pasa con PostgreSQL apagado, la separación de capas es
real y no un dibujo: el servicio nunca supo que había un motor detrás.

Se corre con:
    docker compose exec api_gestion python pruebas/prueba_capas.py
"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from servicios.servicio_programa import ServicioPrograma

LLAVE = "id"


class RepositorioDeMentiras:
    """Cumple la interfaz del repositorio, pero guarda en una lista."""

    def __init__(self):
        self._filas: list[dict] = []

    async def obtener_todos(self, limite: int) -> list[dict]:
        return self._filas[:limite]

    async def obtener_por_llave(self, llave) -> dict | None:
        return next((f for f in self._filas if f[LLAVE] == llave), None)

    async def crear(self, datos: dict) -> bool:
        self._filas.append(dict(datos))
        return True

    async def actualizar(self, llave, datos: dict) -> int:
        fila = await self.obtener_por_llave(llave)
        if fila is None:
            return 0
        fila.update(datos)
        return 1

    async def eliminar_logico(self, llave) -> int:
        fila = await self.obtener_por_llave(llave)
        if fila is None:
            return 0
        self._filas.remove(fila)
        return 1


def revisar(condicion: bool, mensaje_ok: str, mensaje_error: str) -> bool:
    print(f"[{'OK' if condicion else 'ERROR'}] "
          f"{mensaje_ok if condicion else mensaje_error}")
    return condicion


async def main() -> int:
    print("=== Prueba de capas — SIN base de datos ===")
    servicio = ServicioPrograma(RepositorioDeMentiras())
    bien = True

    bien &= revisar(await servicio.listar(1000) == [],
                    "El sistema arranca vacío.",
                    "Arrancó con filas que nadie creó.")

    nueva = {"id": 9001, "nombre": "Ingenieria de Sistemas", "tipo": "Pregrado", "nivel": "Profesional", "fecha_creacion": "2005-01-15", "numero_cohortes": "40", "cant_graduados": "1250", "fecha_actualizacion": "2026-01-30", "ciudad": "Medellin", "facultad": 1}
    await servicio.crear(nueva)
    lista = await servicio.listar(1000)
    bien &= revisar(len(lista) == 1 and lista[0][LLAVE] == 9001,
                    f"Registro creado y listado: {lista[0]['nombre']}",
                    "La creación no se reflejó en el listado.")

    try:
        await servicio.obtener(999999)
        bien &= revisar(False, "", "Una llave inexistente NO lanzó LookupError.")
    except LookupError:
        bien &= revisar(True, "Buscar una llave inexistente lanza LookupError.", "")

    try:
        await servicio.listar(0)
        bien &= revisar(False, "", "limite = 0 NO lanzó ValueError.")
    except ValueError:
        bien &= revisar(True, "Límite menor o igual a cero rechazado.", "")

    try:
        await servicio.actualizar(9001, {})
        bien &= revisar(False, "", "Un cuerpo vacío NO lanzó ValueError.")
    except ValueError:
        bien &= revisar(True, "Cuerpo vacío en la actualización rechazado.", "")

    await servicio.actualizar(9001, {"nombre": "CAMBIADO"})
    tras = await servicio.obtener(9001)
    bien &= revisar(tras["nombre"] == "CAMBIADO"
                    and tras["tipo"] == nueva["tipo"],
                    "La actualización parcial cambió SOLO un campo.",
                    "La actualización parcial tocó campos que no debía.")

    await servicio.eliminar(9001)
    bien &= revisar(await servicio.listar(1000) == [],
                    "Tras el borrado, el sistema vuelve a estar vacío.", "")

    try:
        await servicio.eliminar(9001)
        bien &= revisar(False, "", "La segunda eliminación NO falló.")
    except LookupError:
        bien &= revisar(True,
                        "Segunda eliminación rechazada: ya no existe.", "")

    print("=== Prueba de capas completada "
          f"{'CON ÉXITO' if bien else 'CON ERRORES'} ===")
    return 0 if bien else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
