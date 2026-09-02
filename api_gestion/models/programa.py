"""
Modelos Pydantic de programa — la FRONTERA DE ENTRADA de la API.

Aquí no hay ni un solo `if` de validación: se DECLARA la forma correcta de
los datos y Pydantic valida al construir el objeto. Un cuerpo inválido muere
en 422 antes de tocar el servicio o la base.

Hay UN modelo por semántica HTTP, y esa es la razón de que PUT y PATCH se
comporten distinto sin una línea que los compare.
"""

from pydantic import BaseModel, Field


class Programa(BaseModel):
    """POST /api/programa — 10 campos obligatorios y 1 opcional."""

    """El código del programa."""
    id: int = Field(ge=1)
    nombre: str = Field(min_length=1, max_length=60)

    """Pregrado, posgrado…"""
    tipo: str = Field(min_length=1, max_length=45)

    nivel: str = Field(min_length=1, max_length=45)

    """Es TEXTO, no una fecha: así lo declara el esquema dado."""
    fecha_creacion: str = Field(min_length=1, max_length=45)

    numero_cohortes: str = Field(min_length=1, max_length=45)

    cant_graduados: str = Field(min_length=1, max_length=45)

    fecha_actualizacion: str = Field(min_length=1, max_length=45)

    ciudad: str = Field(min_length=1, max_length=45)

    """Un número sin clave foránea: la tabla facultad no existe en este módulo."""
    facultad: int = Field(ge=0)


    """El ÚNICO opcional: un programa abierto no tiene fecha de cierre."""
    fecha_cierre: str | None = Field(default=None, max_length=45)


class ProgramaReemplazo(BaseModel):
    """PUT /api/programa/{id} — reemplazo COMPLETO.

    Omitir un campo es 422, no "dejarlo como estaba": esa es la semántica
    de PUT. La llave no va aquí: identifica la fila y viaja en la ruta.
    """

    nombre: str = Field(min_length=1, max_length=60)

    """Pregrado, posgrado…"""
    tipo: str = Field(min_length=1, max_length=45)

    nivel: str = Field(min_length=1, max_length=45)

    """Es TEXTO, no una fecha: así lo declara el esquema dado."""
    fecha_creacion: str = Field(min_length=1, max_length=45)

    numero_cohortes: str = Field(min_length=1, max_length=45)

    cant_graduados: str = Field(min_length=1, max_length=45)

    fecha_actualizacion: str = Field(min_length=1, max_length=45)

    ciudad: str = Field(min_length=1, max_length=45)

    """Un número sin clave foránea: la tabla facultad no existe en este módulo."""
    facultad: int = Field(ge=0)


    """El ÚNICO opcional: un programa abierto no tiene fecha de cierre."""
    fecha_cierre: str | None = Field(default=None, max_length=45)


class ProgramaActualizar(BaseModel):
    """PATCH /api/programa/{id} — parcial: solo se modifican los enviados.

    El MISMO cuerpo que el modelo de arriba rechaza con 422, aquí es válido.
    Lo decide el tipo, no un if en el servicio.
    """

    nombre: str | None = Field(default=None, min_length=1, max_length=60)

    """Pregrado, posgrado…"""
    tipo: str | None = Field(default=None, min_length=1, max_length=45)

    nivel: str | None = Field(default=None, min_length=1, max_length=45)

    """Es TEXTO, no una fecha: así lo declara el esquema dado."""
    fecha_creacion: str | None = Field(default=None, min_length=1, max_length=45)

    numero_cohortes: str | None = Field(default=None, min_length=1, max_length=45)

    cant_graduados: str | None = Field(default=None, min_length=1, max_length=45)

    fecha_actualizacion: str | None = Field(default=None, min_length=1, max_length=45)

    ciudad: str | None = Field(default=None, min_length=1, max_length=45)

    """Un número sin clave foránea: la tabla facultad no existe en este módulo."""
    facultad: int | None = Field(default=None, ge=0)

    """El ÚNICO opcional: un programa abierto no tiene fecha de cierre."""
    fecha_cierre: str | None = Field(default=None, max_length=45)
