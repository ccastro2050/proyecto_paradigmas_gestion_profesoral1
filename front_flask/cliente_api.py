"""
cliente_api.py — La capa de DATOS del front.

Es al front lo que el repositorio es a la API: la ÚNICA pieza que sabe dónde
viven los datos —en la API, nunca en la base— y la única que habla HTTP.
Traduce cada respuesta a `(ok, datos, errores)` para que las plantillas no
tengan que saber qué es un 422.

======================================================================
UNA FUNCIÓN POR OPERACIÓN, CON EL NOMBRE DEL RECURSO ADENTRO
======================================================================

`listar_programas`, `crear_programa`… no una `listar(recurso)` genérica.
Cuando la v2 traiga más tablas habrá más funciones, no un parámetro más — es
la regla de las rutas específicas (sección 6.1 de la metodología del curso),
aplicada del lado del front.

======================================================================
LO QUE ESTE ARCHIVO NO HACE, Y ES LO MÁS IMPORTANTE
======================================================================

No abre ninguna conexión a PostgreSQL. No hay un solo `import asyncpg` en
todo el front, y no lo va a haber: es el artículo de la constitución que dice
que el front no toca la base.

Y aquí la tentación es MAYOR que en otros proyectos, porque **la API también
está en Python** y está en la carpeta de al lado: bastaría un
`sys.path.append("../api_gestion")` para importar sus modelos y sus
servicios. Funcionaría. Y estaría mal — los dos dejarían de ser procesos
independientes, y renombrar un método adentro de la API rompería el front
**sin que nadie tocara el contrato**.

Por eso este archivo trabaja con **diccionarios**, no con objetos de la API:
lo que llega es lo que el JSON traía, ni más ni menos.
"""

import os

import requests

# El hostname INTERNO del compose, jamás localhost: dentro de un contenedor,
# localhost es él mismo.
URL_API = os.environ.get("URL_API_GESTION", "http://localhost:8029")

TIEMPO_MAXIMO = 10  # segundos

NO_DISPONIBLE = ["El servicio no está disponible. ¿Está arriba la API?"]


def _llamar(metodo: str, ruta: str, **kwargs):
    """Ejecuta la petición y unifica un solo caso: «la API no responde».

    Devuelve None cuando NO hubo respuesta —API caída, tiempo agotado—, que
    es distinto de «respondió con un error». Un 404 es la API funcionando y
    diciendo que esa ficha no existe; un None es que no hay con quién hablar.
    """
    try:
        return requests.request(
            metodo, f"{URL_API}{ruta}", timeout=TIEMPO_MAXIMO, **kwargs
        )
    except requests.RequestException:
        return None


def _cuerpo(respuesta):
    """El JSON, o un diccionario vacío si no vino JSON."""
    try:
        return respuesta.json()
    except ValueError:
        return {}


def _mensajes(respuesta) -> list[str]:
    """Traduce a texto los errores que produce ESTA API.

    **Es el único sitio del front que conoce el formato del error.** Si
    mañana la API cambia el sobre, se cambia aquí y en ninguna plantilla.

    Hay dos formatos, y no es un descuido: FastAPI valida con Pydantic y
    devuelve el 422 en SU formato —`{"detail": [{"loc": [...], "msg": ...}]}`—
    mientras los demás errores llegan con el sobre del proyecto,
    `{"detail": {"estado", "mensaje", "detalle"}}`. Los dos se traducen
    aquí a una lista de frases en español.
    """
    cuerpo = _cuerpo(respuesta)
    detalle = cuerpo.get("detail")

    # El 422 de Pydantic: una entrada por campo que no cumplió.
    if isinstance(detalle, list) and detalle:
        frases = []
        for fallo in detalle:
            if not isinstance(fallo, dict):
                frases.append(str(fallo))
                continue
            # `loc` viene como ("body", "nombre_del_campo"): la primera parte
            # es ruido para el usuario.
            partes = [str(p) for p in fallo.get("loc", []) if p != "body"]
            campo = partes[-1] if partes else ""
            mensaje = fallo.get("msg", "dato inválido")
            frases.append(_en_espanol(campo, str(mensaje)) if campo else str(mensaje))
        return frases

    # El sobre del proyecto.
    if isinstance(detalle, dict):
        partes = [detalle.get("mensaje", ""), detalle.get("detalle", "")]
        partes = [p for p in partes if p]
        if partes:
            return partes
    if isinstance(detalle, str) and detalle:
        return [detalle]

    partes = [cuerpo.get("mensaje", ""), cuerpo.get("detalle", "")]
    partes = [p for p in partes if p]
    return partes or ["No se pudo completar la operación."]


# ----------------------------------------------------------------------
# DE LA JERGA DE PYDANTIC AL ESPAÑOL DEL USUARIO
# ----------------------------------------------------------------------
#
# FastAPI valida con Pydantic, y Pydantic reporta en inglés y con el nombre
# de la columna: «nombre: String should have at least 1 character».
#
# Eso está bien para quien lee Swagger y está mal delante de un usuario. Es
# un defecto que **solo se ve cuando existe una pantalla** — con la API sola,
# nadie se inmuta.
#
# Se traduce AQUÍ y no en la API porque traducir es trabajo de la capa de
# presentación: la misma API podría atender mañana a un cliente en otro
# idioma, y el mensaje correcto en ese caso no sería éste.

# Cómo se llama cada campo en la pantalla. El usuario nunca ve `cant_graduados`.
ETIQUETAS = {
    "id": "Código",
    "nombre": "Nombre",
    "tipo": "Tipo",
    "nivel": "Nivel",
    "fecha_creacion": "Fecha de creación",
    "numero_cohortes": "Número de cohortes",
    "cant_graduados": "Cantidad de graduados",
    "fecha_actualizacion": "Fecha de actualización",
    "ciudad": "Ciudad",
    "facultad": "Facultad",
    "fecha_cierre": "Fecha de cierre",
}

# Los mensajes que Pydantic produce con más frecuencia. La comparación es por
# fragmento, no exacta, porque el texto trae el número adentro
# («at least 1 character»).
TRADUCCIONES = (
    ("field required", "es obligatorio"),
    ("Field required", "es obligatorio"),
    ("String should have at least", "no puede quedar vacío"),
    ("String should have at most", "es demasiado largo"),
    ("Input should be a valid integer", "debe ser un número entero"),
    ("Input should be a valid number", "debe ser un número"),
    ("Input should be a valid date", "debe ser una fecha válida"),
    ("Input should be greater than or equal to 0", "no puede ser negativo"),
    ("Input should be greater than or equal to 1", "debe ser mayor que cero"),
    ("unable to parse string as an integer", "debe ser un número entero"),
    ("unable to parse string as a number", "debe ser un número"),
)


def _en_espanol(campo: str, mensaje: str) -> str:
    """Arma la frase que ve el usuario: «Nombre no puede quedar vacío»."""
    etiqueta = ETIQUETAS.get(campo, campo)
    for ingles, espanol in TRADUCCIONES:
        if ingles in mensaje:
            return f"{etiqueta} {espanol}."
    # Si es un mensaje que no conocemos, se muestra tal cual: es preferible
    # un texto raro a esconderle al usuario que algo falló.
    return f"{etiqueta}: {mensaje}"


# ----------------------------------------------------------------------
# PROGRAMAS  ·  /api/programa
# ----------------------------------------------------------------------


def listar_programas(limite: int = 1000):
    """GET → (ok, lista, errores). El 204 es «no hay ninguno», y NO es error."""
    respuesta = _llamar("GET", f"/api/programa?limite={limite}")
    if respuesta is None:
        return False, [], NO_DISPONIBLE
    if respuesta.status_code == 204:
        return True, [], []
    if respuesta.status_code == 200:
        return True, _cuerpo(respuesta).get("datos", []), []
    return False, [], _mensajes(respuesta)


def obtener_programa(id):
    """GET de una ficha → (ok, diccionario, errores)."""
    respuesta = _llamar("GET", f"/api/programa/{id}")
    if respuesta is None:
        return False, None, NO_DISPONIBLE
    if respuesta.status_code == 200:
        return True, _cuerpo(respuesta), []
    return False, None, _mensajes(respuesta)


def crear_programa(datos: dict):
    """POST → (ok, errores)."""
    respuesta = _llamar("POST", "/api/programa", json=datos)
    if respuesta is None:
        return False, NO_DISPONIBLE
    return (True, []) if respuesta.status_code == 200 else (False, _mensajes(respuesta))


def reemplazar_programa(id, datos: dict):
    """PUT — «guardar la ficha completa»: todos los obligatorios viajan."""
    respuesta = _llamar("PUT", f"/api/programa/{id}", json=datos)
    if respuesta is None:
        return False, NO_DISPONIBLE
    return (True, []) if respuesta.status_code == 200 else (False, _mensajes(respuesta))


def actualizar_programa(id, datos: dict):
    """PATCH — «guardar solo lo que cambié»: viaja solo lo diligenciado."""
    respuesta = _llamar("PATCH", f"/api/programa/{id}", json=datos)
    if respuesta is None:
        return False, NO_DISPONIBLE
    return (True, []) if respuesta.status_code == 200 else (False, _mensajes(respuesta))


def eliminar_programa(id):
    """DELETE → (ok, errores). Retiro lógico: la ficha deja de listarse."""
    respuesta = _llamar("DELETE", f"/api/programa/{id}")
    if respuesta is None:
        return False, NO_DISPONIBLE
    return (True, []) if respuesta.status_code == 200 else (False, _mensajes(respuesta))
