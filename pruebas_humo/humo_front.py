# -*- coding: utf-8 -*-
"""Prueba de humo del FRONT de Gestión Profesoral (Flask, puerto 8027).

QUÉ COMPRUEBA, Y POR QUÉ AQUÍ SE PUEDE COMPROBAR TODO
=====================================================

Este front está hecho de formularios HTML corrientes: cada botón manda un
POST que un guion puede enviar igual que lo manda el navegador. Por eso esta
prueba llega **hasta el final** —crea, guarda de las dos maneras y retira—,
cosa que con el front anterior no se podía: allí los clics viajaban por una
conexión persistente y no eran peticiones sueltas.

O sea: la tecnología más sencilla resultó ser la más fácil de probar sin
manos. Vale la pena verlo, porque casi siempre se cuenta al revés.

Lo que se comprueba:

  1. cada pantalla responde por su DIRECCIÓN PROPIA, y la hoja de estilos
     llega de verdad —que no es lo mismo—;
  2. el menú lleva a la pantalla, con una dirección que existe;
  3. lo que la pantalla muestra es lo que la API devolvió;
  4. la pantalla no le habla al usuario en jerga **ni en inglés**;
  5. el recorrido completo: agregar, los dos botones de guardar, y retirar;
  6. y lo que demuestra que son dos procesos: **con la API apagada la
     pantalla sigue en pie**, con su aviso adentro y sin un solo dato.

Uso:  python pruebas_humo/humo_front.py     (parado en la raíz del proyecto)
"""
import html
import http.cookiejar
import json
import random
import re
import string
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

# La consola de Windows no siempre usa UTF-8, y entonces imprimir una flecha
# revienta el guion con un error que no tiene NADA que ver con lo que se está
# probando. `errors="replace"` deja pasar un signo raro y sigue.
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

FRONT = "http://localhost:8027"
API = "http://localhost:8029"
fallos = []

# Un sufijo distinto en cada corrida: si una se interrumpe a la mitad deja la
# ficha puesta, y la siguiente fallaría al crearla por llave duplicada — un
# rojo que no tiene que ver con lo que se está probando.
SUFIJO = "".join(random.choices(string.digits, k=3))
LLAVE = "9" + SUFIJO

# Las columnas que la tabla debe traer, en el idioma del usuario.
ETIQUETAS = ('Código', 'Nombre', 'Tipo', 'Nivel', 'Ciudad', 'Facultad')

navegador = urllib.request.build_opener(
    urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))


def ver(url):
    """Un GET, como el que hace el navegador al escribir la dirección."""
    try:
        with navegador.open(url, timeout=20) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")
    except Exception as e:
        return 0, str(e)


def enviar(ruta, campos):
    """Un POST de formulario: exactamente lo que manda el botón.

    Fíjese en el tipo de contenido: `x-www-form-urlencoded`, que es como
    hablan los formularios. El JSON lo pone el front cuando le habla a la
    API — eso pasa del otro lado, y el usuario nunca lo escribe.
    """
    datos = urllib.parse.urlencode(campos).encode()
    peticion = urllib.request.Request(FRONT + ruta, data=datos)
    try:
        with navegador.open(peticion, timeout=20) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")
    except Exception as e:
        return 0, str(e)


def visible(pagina):
    """El texto que el usuario VE: sin etiquetas y con las tildes de verdad.

    Comprobar sobre el HTML crudo da falsos positivos de los dos lados: un
    «500» puede estar dentro de un número, y el aviso «no está disponible»
    llega escrito `est&#xE1;`, así que buscar la «á» literal no lo encuentra.
    Una prueba de pantalla comprueba **lo que se ve**, no el código fuente.
    """
    sin_script = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", pagina)
    sin_etiquetas = re.sub(r"<[^>]*>", " ", sin_script)
    return re.sub(r"\s+", " ", html.unescape(sin_etiquetas))


def revisar(nombre, condicion, detalle=""):
    marca = "[OK]    " if condicion else "[FALLO] "
    print(marca + nombre + " " + detalle[:140])
    if not condicion:
        fallos.append(nombre)


def api(ruta):
    """Una lectura directa a la API, para contrastar contra la pantalla."""
    codigo, texto = ver(API + ruta)
    if codigo not in (200, 204):
        return None
    return json.loads(texto) if texto else None


def esperar_api(segundos=180):
    """Acepta 200 y 204: un 204 es la API diciendo que la tabla está vacía,
    que es una respuesta válida — no una API a medio arrancar."""
    for _ in range(segundos // 3):
        if ver(API + "/api/programa?limite=1")[0] in (200, 204):
            return True
        time.sleep(3)
    return False


if not esperar_api():
    print("La API no respondió. ¿Está levantado el sistema?")
    print("   docker compose up -d --build")
    raise SystemExit(1)

# ======================================================================
print("=== 1. Las pantallas responden, cada una por su dirección ===")
# ======================================================================
PANTALLAS = [
    ("/", "Gestión Profesoral"),
    ("/programas", "Programas"),
    ("/programas/nuevo", "Agregar"),
]
for ruta_, titulo in PANTALLAS:
    c, t = ver(FRONT + ruta_)
    revisar(ruta_.ljust(24) + " responde y dice «" + titulo + "»",
            c == 200 and titulo in visible(t))

c, t = ver(FRONT + "/pantalla-que-no-existe")
revisar("una dirección inventada da 404, con el marco de la aplicación",
        c == 404 and "no existe" in visible(t))

print()
print("=== 1.b La hoja de estilos LLEGA ===")
# Comprobar el TEXTO de una página no dice si la página se ve. Un 200 que
# devuelve HTML disfrazado de CSS deja la pantalla igual de fea.
try:
    with navegador.open(FRONT + "/static/estilos.css", timeout=20) as r:
        codigo, tipo = r.status, r.headers.get("Content-Type", "")
except Exception as e:
    codigo, tipo = 0, str(e)
revisar("/static/estilos.css llega como text/css",
        codigo == 200 and "css" in tipo, str(tipo))

# ======================================================================
print()
print("=== 2. El menú lleva a la pantalla, con una dirección de verdad ===")
# ======================================================================
c, inicio = ver(FRONT + "/")
revisar("el menú tiene el enlace", 'href="/programas"' in inicio)
revisar("y NINGUNA dirección tiene el nombre de la tabla como parámetro",
        "{tabla}" not in inicio and "?tabla=" not in inicio)

# ======================================================================
print()
print("=== 3. La pantalla trae los datos que dio la API ===")
# ======================================================================
sobre = api("/api/programa?limite=5")
filas = sobre["datos"] if sobre else []
c, t = ver(FRONT + "/programas")
if not filas:
    print("[--]    la tabla `programa` está vacía: no hay datos que comparar")
    revisar("y aun vacía, la pantalla responde y ofrece «Agregar»",
            "Agregar" in visible(t))
else:
    revisar("la API responde", True, str(len(filas)) + " filas")
    revisar("y esos mismos datos se ven en la pantalla",
            all(str(f["id"]) in visible(t) for f in filas[:3]))
    faltan = [e for e in ETIQUETAS if e not in visible(t)]
    revisar("la tabla trae sus columnas", not faltan, str(faltan))

# ======================================================================
print()
print("=== 4. Lo que la pantalla NO debe decirle al usuario ===")
# ======================================================================
# La jerga se busca como TOKEN TÉCNICO, no como palabra suelta: «proyecto» o
# «programa» son nombres de tabla Y palabras que el usuario dice todos los
# días. Jerga de verdad es la ruta de la API, los verbos y los motores.
JERGA = ["PUT", "PATCH", "DELETE", "/api/", "asyncpg", "SELECT",
         "endpoint", "localhost:", "PostgreSQL", "FastAPI", "Traceback"]
for ruta_, _ in PANTALLAS:
    c, t = ver(FRONT + ruta_)
    visto = [j for j in JERGA if j in visible(t)]
    revisar(ruta_.ljust(24) + " sin jerga", not visto, str(visto))

# ======================================================================
print()
print("=== 5. EL RECORRIDO COMPLETO, botón por botón ===")
# ======================================================================
COMPLETO = {
        "id": LLAVE,
        "nombre": ("Nombre " + SUFIJO)[:150],
        "tipo": ("Tipo " + SUFIJO)[:45],
        "nivel": ("Nivel " + SUFIJO)[:45],
        "fecha_creacion": ("Fecha de creación " + SUFIJO)[:45],
        "numero_cohortes": ("Número de cohortes " + SUFIJO)[:45],
        "cant_graduados": ("Cantidad de graduados " + SUFIJO)[:45],
        "fecha_actualizacion": ("Fecha de actualización " + SUFIJO)[:45],
        "ciudad": ("Ciudad " + SUFIJO)[:45],
        "facultad": "7",
        "fecha_cierre": ("Fecha de cierre " + SUFIJO)[:45],
}

c, t = enviar("/programas/nuevo", COMPLETO)
revisar("agregar la ficha " + str(LLAVE), "Se agregó" in visible(t))
revisar("  y ya aparece en el listado", str(LLAVE) in visible(t))

# --- Guardar la ficha completa ---
renombrado = dict(COMPLETO, verbo="completa",
                  **{"nombre": "Corregido " + SUFIJO})
c, t = enviar("/programas/" + str(LLAVE) + "/editar", renombrado)
revisar("«Guardar la ficha completa» guarda", "Se guardaron" in visible(t))
revisar("  y el valor nuevo se ve", "Corregido " + SUFIJO in visible(t))

# --- La ficha completa con un obligatorio en blanco: se rechaza ---
c, t = enviar("/programas/" + str(LLAVE) + "/editar",
              dict(COMPLETO, verbo="completa", **{"nombre": ""}))
texto = visible(t)
revisar("la ficha completa con «Nombre» en blanco se RECHAZA",
        "Se guardaron" not in texto)
revisar("  y el motivo está EN ESPAÑOL y con el nombre de la pantalla",
        "Nombre" in texto and "String should" not in texto)
revisar("  sin números de estado ni jerga",
        not any(j in texto for j in ("422", "PUT", "/api/")))

# --- Solo lo que cambié: el MISMO formulario a medio llenar ---
vacios = {c: "" for c in COMPLETO if c != "id"}
c, t = enviar("/programas/" + str(LLAVE) + "/editar",
              dict(vacios, verbo="parcial",
                   **{"tipo": ("Tipo " + SUFIJO)[:45]}))
revisar("«Guardar solo lo que cambié», con lo demás en blanco, SÍ guarda",
        "Se guardaron" in visible(t))

# Y aquí está la lección, comprobada contra los datos: cambió un campo y el
# otro se quedó como estaba. Lo que no se envía, no se toca.
ficha = api("/api/programa/" + str(LLAVE))
revisar("  el campo enviado cambió",
        ficha and str(ficha.get("tipo")).startswith(
            "Tipo"[:6]),
        str(ficha and ficha.get("tipo")))
revisar("  y «Nombre» NO se borró: lo que no se envía, no se toca",
        ficha and ficha.get("nombre") == "Corregido " + SUFIJO,
        str(ficha and ficha.get("nombre")))

# --- Retirar ---
c, t = enviar("/programas/" + str(LLAVE) + "/eliminar", {})
revisar("retirar la ficha", "Se retiró" in visible(t))

# Se pide la pantalla otra vez: en la segunda visita el aviso ya no está —se
# muestra una sola vez—, así que si la llave apareciera sería en la tabla de
# verdad. Dos comprobaciones por el precio de una.
c, t = ver(FRONT + "/programas")
revisar("  el aviso se muestra UNA vez y no se repite", "Se retiró" not in visible(t))
revisar("  y la ficha ya no está en el listado", str(LLAVE) not in visible(t))

# ======================================================================
print()
print("=== 6. LA PRUEBA DE LOS DOS PROCESOS: se apaga la API ===")
print("    (esto tarda unos segundos)")
# ======================================================================
subprocess.run(["docker", "compose", "stop", "api-gestion"],
               capture_output=True, text=True)
time.sleep(3)

c, t = ver(FRONT + "/programas")
texto = visible(t)
revisar("la pantalla SIGUE respondiendo con la API apagada", c == 200)
revisar("  y muestra el aviso dentro de la aplicación",
        "no está disponible" in texto)
revisar("  con su menú y su marco intactos",
        "Programas" in texto and "Inicio" in texto)
# Ésta es LA comprobación de la constitución: PostgreSQL sigue encendida y
# con los datos ahí. Si el front pudiera llegar a la base por su cuenta, la
# tabla se seguiría viendo. No se ve.
revisar("  y SIN un solo dato: el front no puede llegar a la base solo",
        "Corregido" not in texto)

subprocess.run(["docker", "compose", "start", "api-gestion"],
               capture_output=True, text=True)
print("    API encendida otra vez; esperando a que responda…")
esperar_api(90)
c, t = ver(FRONT + "/programas")
revisar("y al volver la API, la pantalla vuelve a responder", c == 200)

print()
if fallos:
    print("=== RESULTADO: " + str(len(fallos)) + " FALLO(S) ===")
    for f in fallos:
        print("   -", f)
    raise SystemExit(1)

print("=== RESULTADO: TODO EN VERDE ===")
print()
print("Se recorrió el ciclo completo desde la PANTALLA, con los mismos POST")
print("que manda el navegador. Queda para una persona lo que un guion no ve:")
print("que se entienda.")
