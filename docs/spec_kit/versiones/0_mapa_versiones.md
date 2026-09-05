# Mapa de versiones — Módulo Gestión Profesoral

> La ruta completa del proyecto. Cada versión se especifica **solo cuando
> la anterior está cerrada** (commit + tag). Este mapa da la dirección; el
> spec kit de cada versión da el detalle.
>
> La ruta es la que define
> [modulo_gestion_profesoral.md](../../../ProyectosDeAula/docs/modulo_gestion_profesoral.md);
> aquí no se inventa nada, se ordena.

## La estrategia: back y front EN PARALELO

**Cada versión entrega su parte de la API *y* su parte del front**, y una
versión **no está cerrada** si la API responde y la pantalla no.

El front es **Flask** sobre Python 3.12, en un tercer contenedor, en el
puerto **8027**. Habla con la API solo por HTTP: no tiene cadena
de conexión, ni driver de base de datos, ni servicio `postgres` en su
`depends_on`.

Está exigido por el **Artículo 1.1** de la [constitución](../1_constitution.md).

## La ruta

| Versión | Qué agrega (acumulativo) | Estado |
|---|---|---|
| **v1** | CRUD completo de las **tablas sin clave foránea**, con los catálogos del Excel cargados | **En curso** ([spec](v1_programa/2_spec.md)) |
| v2 | CRUD de las **11 tablas con clave foránea**: las FK como listas desplegables cargadas desde la API, y validación de integridad referencial | Sin especificar |
| v3 | **JWT**, sesiones y control de acceso por roles; CRUD de `usuario`, `rol` y `rol_usuario` solo para administradores | Sin especificar |
| v4 | **10 consultas multitabla** (4+ tablas cada una), dashboard con gráficos, páginas corporativas, responsive/PWA y **publicación** en un servidor | Sin especificar |

## Qué tabla entra en qué versión

Las 19 tablas de la base, repartidas:

| Versión | Tablas |
|---|---|
| **v1** | `programa` · `area_conocimiento` · `termino_clave` · `linea_investigacion` · `red` |
| v2 | `docente` · `estudios_realizados` · `docente_departamento` · `intereses_futuros` · `evaluacion_docente` · `reconocimiento` · `experiecia` · `red_docente` · `estudio_ac` · `apoyo_profesoral` · `beca` |
| v3 | `rol` · `usuario` · `rol_usuario` |

> **Ojo:** las 19 tablas **existen en la base desde la v1** (Artículo 5 de
> la [constitución](../1_constitution.md)). Lo que reparte esta tabla es
> qué puede **nombrar el código** de cada versión, no qué existe en el
> motor.

## Lo que este ejemplo construye

La v1 de este repositorio se construye sobre **`programa`**: una rebanada
vertical completa —controlador, servicio, repositorio, interfaces,
peticiones y prueba sin base de datos— sobre la tabla **con más campos de
las siete sin clave foránea** (once, frente a los cuatro de la siguiente).

Y arranca **vacía**, a propósito: el Excel de referencia no trae programas.
Eso no es una carencia sino una ventaja para el smoke test, que puede
recorrer el ciclo completo desde el principio —**listado vacío → 204,
crear → 1 fila, borrar → 204 otra vez**— y ejercitar el 204 que una tabla
llena nunca deja probar.

Las demás tablas de la v1 son **ese mismo patrón** con otros nombres. El
equipo que tome este ejemplo lo revisa, y **si está de acuerdo lo retoma y
lo completa; si no, lo rehace a su manera** — lo que no puede es cambiar la
especificación sin pasar por sus compuertas.

## Reglas del mapa

1. **No se anticipa nada de una versión futura** (Artículo 1 de la
   constitución): en la v1 no aparece una FK, ni un programa, ni un token.
2. **Una versión cerrada no se reabre**: los ajustes van en la siguiente.
3. **Regresión obligatoria**: al cerrar la vN, los criterios de todas las
   versiones anteriores deben seguir pasando.
4. El repositorio siempre muestra la **versión en curso, funcionando**.
