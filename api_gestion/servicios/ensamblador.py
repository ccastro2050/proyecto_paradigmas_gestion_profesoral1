"""
ensamblador.py — El ÚNICO punto del sistema que decide qué motor se usa.

Los controladores llaman a `crear_servicio_programa()` y reciben algo que cumple
la interfaz del servicio. No saben —ni tienen por qué saber— qué repositorio
hay detrás.

Hoy hay un solo motor. El día que entre un segundo, este archivo es el único
que cambia: esa es toda la gracia de tener la construcción en un solo sitio.
"""

import os

from repositorios.repositorio_programa_postgresql import RepositorioProgramaPostgreSQL
from servicios.abstracciones.i_servicio_programa import IServicioPrograma
from servicios.servicio_programa import ServicioPrograma


def _cadena_conexion() -> str:
    cadena = os.environ.get("DB_POSTGRES")
    if not cadena:
        raise RuntimeError(
            "Falta la variable de entorno DB_POSTGRES con la cadena de conexión.")
    return cadena


def crear_servicio_programa() -> IServicioPrograma:
    """Arma el servicio con su repositorio. Construirlo NO abre conexiones."""
    return ServicioPrograma(RepositorioProgramaPostgreSQL(_cadena_conexion()))
