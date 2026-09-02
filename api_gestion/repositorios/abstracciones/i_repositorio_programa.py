"""
Contrato del repositorio de programa. El servicio depende de ESTA interfaz, nunca
de una clase concreta: por eso se le puede enchufar un repositorio de
mentiras y probarlo sin base de datos (inversión de dependencias).
"""

from typing import Protocol


class IRepositorioPrograma(Protocol):
    """Las operaciones de datos de programa."""

    async def obtener_todos(self, limite: int) -> list[dict]:
        """Hasta `limite` filas ACTIVAS, ordenadas por id."""
        ...

    async def obtener_por_llave(self, llave) -> dict | None:
        """La fila con esa llave si está activa, o None."""
        ...

    async def crear(self, datos: dict) -> bool:
        """Inserta. Devuelve True si quedó insertada."""
        ...

    async def actualizar(self, llave, datos: dict) -> int:
        """Escribe los campos de `datos`. Devuelve filas afectadas."""
        ...

    async def eliminar_logico(self, llave) -> int:
        """Marca activo = FALSE. Cero filas = no existía o ya estaba
        inactiva."""
        ...
