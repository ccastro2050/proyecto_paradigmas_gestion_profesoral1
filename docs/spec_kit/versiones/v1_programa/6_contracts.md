# Contratos HTTP — Versión 1: los 7 endpoints exactos

> Base: `http://localhost:8029` · Documentación interactiva en `/docs`.
> Lo que este documento dice se cumple **al pie de la letra** (Artículo 9).

## 0. Convenciones globales

**Sobre de lectura:**

```json
{ "tabla": "programa", "limite": 1000, "total": 1, "datos": [ … ] }
```

**Sobre de error:**

```json
{ "estado": 422, "mensaje": "Datos inválidos.", "detalle": "…",
  "errores": ["El campo nivel es obligatorio."] }
```

`errores[]` aparece **solo** en el 422.

**Los nombres de los campos JSON van en snake_case** (`fechaCreacion`,
`numeroCohortes`, `filasAfectadas`), que es lo que FastAPI hace **por
defecto**: no hay que configurar nada, y por lo tanto no hay nada que se
pueda configurar mal.

> La ruta es `/api/programa` —nombra la tabla— y el cuerpo usa
> `fechaCreacion`, no `fecha_creacion`. **El JSON no es una ventana a la
> tabla**: la ruta identifica el recurso y el cuerpo sigue la convención de
> quien lo consume.

**Catálogo de códigos:**

| Situación | Código |
|---|---|
| Lectura o escritura correcta | **200** |
| Lectura sin filas activas | **204** (sin cuerpo) |
| Regla de negocio rota (`limite` ≤ 0, `PATCH` sin campos) | **400** |
| Cuerpo inválido: falta un campo, tipo equivocado, texto muy largo | **422** |
| El código no existe, o está inactivo | **404** |
| La base rechaza (llave duplicada) o falla | **500** |

## 1. `GET /` — Diagnóstico

```
GET /
→ 200 { "mensaje": "API Gestión Profesoral — módulo de programas",
        "version": "v1", "contratos": "/docs" }
```

**Sin desenlaces de error, y a propósito:** no recibe parámetros ni cuerpo
y no consulta la base. Si no responde 200, la API no está arriba.

## 2. `GET /api/programa[?limite=N]` — Listar

```
GET /api/programa
→ 204 (sin cuerpo)          ← el ESTADO INICIAL: no hay programas

…y una vez creado alguno:
→ 200 { "tabla":"programa", "limite":1000, "total":1, "datos":[ … ] }

GET /api/programa?limite=1
→ 200 { …, "limite":1, "total":1 }

→ 400 si limite <= 0
```

Devuelve **solo** las filas con `activo = TRUE`. El campo `activo` **no viaja
en la respuesta**.

## 3. `GET /api/programa/{id}` — Obtener uno

```
GET /api/programa/9001
→ 200 {"id":9001,"nombre":"Ingenieria de Sistemas","tipo":"Pregrado","nivel":"Profesional","fechaCreacion":"2005-01-15","fechaCierre":null,"numeroCohortes":"40","cantGraduados":"1250","fechaActualizacion":"2026-01-30","ciudad":"Medellin","facultad":1}

GET /api/programa/999999                       ← no existe
→ 404 { "estado":404, "mensaje":"Programa no encontrado.",
        "detalle":"No existe un programa con el código 999999." }
```

Una fila **inactiva** responde igual: 404 (C8).

## 4. `POST /api/programa` — Crear

Cuerpo (petición `ProgramaCrear`): diez campos obligatorios y
`fechaCierre`, que es el único opcional (C12).

```
POST /api/programa
body {"id":9001,"nombre":"Ingenieria de Sistemas","tipo":"Pregrado","nivel":"Profesional","fechaCreacion":"2005-01-15","fechaCierre":null,"numeroCohortes":"40","cantGraduados":"1250","fechaActualizacion":"2026-01-30","ciudad":"Medellin","facultad":1}
→ 200 { "estado":200, "mensaje":"Programa creado exitosamente." }

body {"id":9002,"nombre":"X","tipo":"Y"}        ← faltan siete campos
→ 422 { "estado":422, "mensaje":"Datos inválidos.",
        "errores":["El campo nivel es obligatorio.", …] }

body {"id":"no-es-un-numero", …}                ← el tipo también es regla
→ 422

body {"id":9001, …}                             ← código duplicado (PK)
→ 500 con el error del motor en detalle
```

## 5. `PUT /api/programa/{id}` — Reemplazo COMPLETO

```
PUT /api/programa/9001
body {"nombre":"Ingenieria de Sistemas y Computacion","tipo":"Pregrado",
      "nivel":"Profesional","fechaCreacion":"2005-01-15","fechaCierre":null,
      "numeroCohortes":"41","cantGraduados":"1300",
      "fechaActualizacion":"2026-08-29","ciudad":"Medellin","facultad":1}
→ 200 { "estado":200, "mensaje":"Programa reemplazado.", "filasAfectadas":1 }

body sin "nivel"
→ 422 { …, "errores":["El campo nivel es obligatorio."] }

PUT /api/programa/999999
→ 404
```

**Los nueve obligatorios lo siguen siendo**: reemplazar es poner todo de
nuevo. El `id` no va en el cuerpo — identifica la fila.

## 6. `PATCH /api/programa/{id}` — Actualización PARCIAL

```
PATCH /api/programa/9001
body {"ciudad":"Bogota"}                       ← solo lo que cambia
→ 200 { "estado":200, "mensaje":"Programa actualizado.", "filasAfectadas":1 }

body sin "nivel" (el MISMO que el PUT rechazó)
→ 200                                           ← aquí es válido

body {}                                         ← nada que actualizar
→ 400 { "estado":400, "mensaje":"Parámetros inválidos.",
        "detalle":"No se envió ningún campo para actualizar." }

PATCH /api/programa/999999
→ 404
```

**Esta pareja es la lección del contrato:** el mismo cuerpo da 422 en `PUT`
y 200 en `PATCH`.

## 7. `DELETE /api/programa/{id}` — Eliminar (LÓGICO)

```
DELETE /api/programa/9001
→ 200 { "estado":200, "mensaje":"Programa eliminado.", "filasAfectadas":1 }

DELETE /api/programa/9001                      ← segunda vez: ya está inactivo
→ 404

DELETE /api/programa/999999                    ← nunca existió
→ 404
```

**La fila no se borra:** queda con `activo = FALSE`. El listado **vuelve a
responder 204** y la fila sigue en la base — es el criterio 5.
