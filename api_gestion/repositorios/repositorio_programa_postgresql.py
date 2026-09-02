"""
Repositorio de programa para PostgreSQL — la capa de DATOS.

SQLAlchemy async como EJECUTOR, no como ORM: el SQL se escribe a mano, queda
a la vista y SIEMPRE va parametrizado con `text()` y `:parametro`.

Todas las consultas filtran por activo = TRUE: el borrado es LÓGICO.
"""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine


class RepositorioProgramaPostgreSQL:
    """Implementación concreta de IRepositorioPrograma."""

    # Las columnas se listan una sola vez: si mañana entra una, entra aquí.
    COLUMNAS = "id, nombre, tipo, nivel, fecha_creacion, numero_cohortes, cant_graduados, fecha_actualizacion, ciudad, facultad, fecha_cierre"

    def __init__(self, cadena_conexion: str):
        self._cadena_conexion = cadena_conexion
        self._engine: AsyncEngine | None = None

    def _obtener_engine(self) -> AsyncEngine:
        # Se crea la primera vez que se necesita: construir el repositorio no
        # abre conexiones.
        if self._engine is None:
            self._engine = create_async_engine(self._cadena_conexion)
        return self._engine

    async def obtener_todos(self, limite: int) -> list[dict]:
        sql = text(
            f"SELECT {self.COLUMNAS} FROM programa "
            "WHERE activo = TRUE ORDER BY id LIMIT :limite"
        )
        async with self._obtener_engine().connect() as conexion:
            resultado = await conexion.execute(sql, {"limite": limite})
            return [dict(fila._mapping) for fila in resultado]

    async def obtener_por_llave(self, llave) -> dict | None:
        # Una fila inactiva responde como inexistente.
        sql = text(
            f"SELECT {self.COLUMNAS} FROM programa "
            "WHERE id = :llave AND activo = TRUE"
        )
        async with self._obtener_engine().connect() as conexion:
            resultado = await conexion.execute(sql, {"llave": llave})
            fila = resultado.first()
            return dict(fila._mapping) if fila else None

    async def crear(self, datos: dict) -> bool:
        columnas = ", ".join(datos)
        valores = ", ".join(f":{c}" for c in datos)
        # Se componen NOMBRES DE COLUMNA que vienen de un modelo Pydantic —una
        # lista cerrada, escrita por nosotros—, nunca del usuario. Los VALORES
        # siempre viajan como :parametro.
        sql = text(
            f"INSERT INTO programa ({columnas}, activo) VALUES ({valores}, TRUE)")
        async with self._obtener_engine().begin() as conexion:
            resultado = await conexion.execute(sql, datos)
            return resultado.rowcount == 1

    async def actualizar(self, llave, datos: dict) -> int:
        asignaciones = ", ".join(f"{columna} = :{columna}" for columna in datos)
        sql = text(
            f"UPDATE programa SET {asignaciones} "
            "WHERE id = :pk_llave AND activo = TRUE"
        )
        async with self._obtener_engine().begin() as conexion:
            resultado = await conexion.execute(
                sql, {**datos, "pk_llave": llave})
            return resultado.rowcount

    async def eliminar_logico(self, llave) -> int:
        # Borrado LÓGICO en una sola consulta: cero filas afectadas significa
        # "no existe o ya estaba inactiva", que es el 404 del contrato.
        sql = text(
            "UPDATE programa SET activo = FALSE "
            "WHERE id = :llave AND activo = TRUE"
        )
        async with self._obtener_engine().begin() as conexion:
            resultado = await conexion.execute(sql, {"llave": llave})
            return resultado.rowcount
