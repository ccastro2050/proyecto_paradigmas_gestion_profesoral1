# Especificación — Versión 1: `programa` + PostgreSQL

> **Versión 1** ([mapa](../0_mapa_versiones.md)) · La primera rebanada
> vertical del módulo Gestión Profesoral: una tabla, sus siete endpoints y
> las tres capas completas. Ante conflicto, manda la
> [constitución](../../1_constitution.md).

## 1. Propósito de la v1

Construir la API del catálogo de **programas académicos** de punta a punta:
controlador, servicio, repositorio e interfaces, contra PostgreSQL y en un
solo comando.

La v1 no busca cubrir el módulo: busca **dejar el patrón montado y
verificado**. Las demás tablas sin clave foránea son este mismo patrón con
otros nombres — y con menos campos, porque `programa` es la más grande de
las cinco.

## 2. Alcance

**Incluye**

- El CRUD completo de `programa`: listar (con límite), obtener por código,
  crear, reemplazar, actualizar parcialmente y eliminar.
- **Borrado lógico**: `DELETE` marca `activo = FALSE` y los listados filtran
  los inactivos (Artículo 6).
- Un endpoint de diagnóstico y la documentación interactiva en `/docs`.
- La prueba de capas: el servicio con un repositorio de mentiras, sin base
  de datos.

**NO incluye** — y no se anticipa nada de esto (Artículo 1)

- Ninguna otra tabla de las 19, aunque existan todas en la base.
- El docente y todo lo que cuelga de él —estudios, evaluaciones,
  reconocimientos, experiencia—: eso es la v2.
- Autenticación, JWT, roles ni usuarios: eso es la v3.
- Dashboard ni consultas multitabla: eso es la v4.
- Más pantallas que la de `programa`: las demás tablas llegan en la
  v2, cada una con la suya.
- **Reactivar** un registro inactivo (`activo = TRUE`).
- Validar que las fechas sean fechas: en esta versión son texto, tal como
  las declara el esquema dado (C6).

## 3. Requisitos funcionales

### RF1 — Listar programas (GET + query string)
`GET /api/programa` → 200 con el sobre `{tabla, limite, total, datos:[…]}`.
- Devuelve **solo los activos**.
- Parámetro opcional `limite` (entero > 0; por defecto 1000).
- Sin filas activas → **204** sin cuerpo. **Este es el estado inicial**: la
  tabla arranca vacía.

### RF2 — Obtener por código (GET + parámetro de ruta)
`GET /api/programa/{id}` → 200 con el programa.
- Inexistente **o inactivo** → 404.

### RF3 — Crear (POST + cuerpo completo)
`POST /api/programa` con los diez campos obligatorios más `fechaCierre`,
que es el único opcional.
- Nace con `activo = TRUE`.
- Código ya existente → 500 (lo rechaza la llave primaria).

### RF4 — Reemplazar (PUT + cuerpo completo)
`PUT /api/programa/{id}` con los mismos campos del cuerpo, sin el `id`.
- **Los nueve obligatorios lo siguen siendo**: es un reemplazo. Falta uno → 422.
- Devuelve `filasAfectadas`; inexistente → 404.

### RF5 — Actualizar parcialmente (PATCH + cuerpo parcial)
`PATCH /api/programa/{id}` con los campos que se quieran cambiar.
- Solo se modifican los enviados.
- Cuerpo vacío → 400.
- Devuelve `filasAfectadas`; inexistente → 404.

### RF6 — Eliminar (DELETE, borrado lógico)
`DELETE /api/programa/{id}` marca `activo = FALSE`.
- Devuelve `filasAfectadas`; inexistente o ya inactivo → 404.
- La fila **no desaparece** de la base.

### RF7 — Diagnóstico
`GET /` → JSON con mensaje, versión (`"v1"`) y la ruta de los contratos.

## 4. Requisitos no funcionales

- **Un solo comando**: `docker compose up -d --build` (Artículo 4).
- **Tres capas con interfaces** (Artículo 3).
- **SQL a mano y parametrizado**, sin ORM (Artículo 2).
- **Todo en español** (Artículo 8).
- Documentación interactiva en `/docs`.

## 5. Criterios de aceptación

1. **Un solo comando.** `docker compose up -d --build` deja corriendo SQL
   Server —con la base y sus 19 tablas— y la API.
   `GET http://localhost:8029/` responde `"version":"v1"`.
2. **El sistema arranca vacío.** `GET /api/programa` responde **204 sin
   cuerpo**.
3. **Crear y listar.** Un `POST` con los campos obligatorios responde 200;
   después, `GET /api/programa` responde **200 con `total: 1`**.
4. **Ciclo de los cinco verbos.** `POST` crea el código `9001` → `PUT` lo
   reemplaza → `PATCH` le cambia solo `ciudad` → `GET` lo confirma →
   `DELETE` lo desactiva, y un **segundo** `DELETE` responde **404**.
   Además, un `PUT` sin el campo `nivel` responde **422** mientras el
   **mismo cuerpo** enviado por `PATCH` responde **200**.
5. **El borrado es lógico, y se verifica.** Después del `DELETE` el listado
   vuelve a responder **204**, **y la fila sigue en la base** con
   `activo = FALSE`.
6. **La validación es la frontera.** `POST` sin `nivel` → **422** con
   `errores:[…]`; `POST` con un `id` que no es número → **422**; `POST` con
   un código que ya existe → **500**. En ninguno se toca la base.
7. **Prueba de capas.** El proyecto `pruebas/` ejecuta el servicio con un
   **repositorio de mentiras** y todas sus verificaciones pasan **con SQL
   Server apagado**.

## 6. Clarificaciones

> **Qué es esta sección:** el registro de las ambigüedades detectadas ANTES
> de planear. Es la **compuerta 1** del método.

| # | La pregunta | La respuesta, con su razón | Dónde quedó |
|---|---|---|---|
| C1 | `area_conocimiento.id` está declarado `INT`, pero los datos son códigos como `1A01` | **Mandan los datos: `VARCHAR(6)`.** Si no, el script no puede cargar su propio catálogo. Arrastra a `estudio_ac` | `db/init.sql` |
| C2 | `area_conocimiento.disciplina` es `VARCHAR(60)` y el valor más largo tiene **124** caracteres | **Se agranda a `VARCHAR(150)`.** Recortar un catálogo oficial lo falsea | `db/init.sql` |
| C3 | Ninguna tabla del módulo trae `activo`, pero la metodología exige borrado lógico | **Se agrega `activo BOOLEAN NOT NULL DEFAULT TRUE`** a las 16 tablas del módulo | Artículo 6 · RF6 |
| C4 | El catálogo trae **"Cienias Naturales"** en 48 de las 218 filas | **Se corrige.** Es un error de digitación de la fuente | `db/init.sql` |
| C5 | El Excel trae **191 programas**, pero solo cuatro de las once columnas, y seis de las que faltan **no admiten nulos**. ¿Se siembran? | **No.** Rellenar `nivel`, `fecha_creacion`, `numero_cohortes`, `cant_graduados`, `fecha_actualizacion` y `ciudad` para 191 programas sería **inventar datos**. La tabla arranca vacía, y eso da un smoke test que empieza por el 204 | `5_data_model` §3 · criterio 2 |
| C6 | Las fechas están declaradas `VARCHAR(45)`, no `DATE`. ¿Se corrige el tipo? | **No en la v1.** El esquema es artefacto **dado** (Artículo 5), y esta versión no hace aritmética de fechas: no las compara, no las ordena, no calcula duraciones. Queda anotado como deuda para la versión que sí lo necesite | `5_data_model` §2 |
| C7 | `programa.facultad` es un `INT`, pero **en este módulo no existe la tabla `facultad`** | **Se deja como está: un número sin restricción.** El módulo no incluye esa tabla, así que no hay integridad referencial que imponer. La v1 lo trata como un dato más | `5_data_model` §2 |
| C8 | Un registro inactivo, ¿se puede consultar por su código? | **No: responde 404.** Si el listado los filtra, individualmente tampoco existen | RF2 · RF6 |
| C9 | ¿Y un segundo `DELETE`? | **404**, por consecuencia de C8 | RF6 · criterio 4 |
| C10 | `?limite=0` o negativo, ¿422 o 400? | **400.** La forma del dato es correcta; lo que se rompe es una regla de negocio | RF1 · Artículo 10 |
| C11 | Crear con un código que ya existe, ¿409 o 500? | **500.** En la v1 la llave la defiende la base, no la API | RF3 · criterio 6 |
| C12 | `fecha_cierre` admite nulos y los demás no. ¿Es un descuido? | **No: es la regla.** Un programa abierto no tiene fecha de cierre. Es el único campo opcional del cuerpo | RF3 · `5_data_model` §2 |

## 7. Definición de TERMINADA

La v1 está terminada —y solo entonces se escribe la spec de la v2— cuando:

1. Los **7 criterios** pasan, verificados con el smoke test de
   [7_quickstart.md](7_quickstart.md) **corrido por una persona**.
2. La lista de [9_checklist.md](9_checklist.md) está en verde y firmada.
3. No queda ningún `[NECESITA ACLARACIÓN: …]` en este documento.
4. Se hace commit y **tag `v1`**.


---

## La PANTALLA — el requisito que completa la versión

Los requisitos anteriores describen la API. **Este describe lo que ve quien la
usa**, y sin él la versión no está cerrada: una versión que responde por HTTP
pero no se puede usar es media versión (Artículo 1.1).

En `http://localhost:8027/programas`:

| Lo que se puede hacer | Cómo se ve |
|---|---|
| **Consultar** | Una tabla con sus columnas: Código · Nombre · Tipo · Nivel… |
| **Agregar** una ficha | Un formulario con **un** botón |
| **Corregir** una ficha | El mismo formulario con **dos**: «Guardar la ficha completa» y «Guardar solo lo que cambié» |
| **Retirar** una ficha | Un botón que pide confirmación primero |

**Tres reglas de esta pantalla**, y las tres se comprueban:

1. **No le habla al usuario en jerga.** Ni «PUT», ni «422», ni rutas de la API.
   Los botones se llaman como el usuario piensa; que uno mande un reemplazo y
   el otro una modificación parcial es asunto del programa.
2. **Un error no pierde lo escrito.** Si la API rechaza el guardado, el
   formulario vuelve con lo que la persona había digitado.
3. **Vacío no es error.** Sin filas, la pantalla muestra un recuadro que lo
   dice, no un aviso rojo.

> **Los dos botones son la lección del contrato hecha pantalla.** El mismo
> formulario a medio llenar que «la ficha completa» rechaza, «solo lo que
> cambié» lo guarda. La diferencia no la decide ningún `if`: la decide **qué se
> envía**.

### Criterios de aceptación de la pantalla

| # | Criterio | Cómo se comprueba |
|---|---|---|
| P1 | La pantalla muestra las filas **que dio la API** | Se le piden a la API y se buscan en el texto visible de la pantalla |
| P2 | El ciclo completo se hace **desde la pantalla**, sin Swagger ni `curl` | Recorrido a mano de `7_quickstart.md` |
| P3 | **No hay jerga** en el texto visible | Se quitan las etiquetas HTML y se busca |
| P4 | **Son dos procesos**: con la API apagada la pantalla sigue en pie, con su aviso y **sin un solo dato** | `docker compose stop api-gestion` |
