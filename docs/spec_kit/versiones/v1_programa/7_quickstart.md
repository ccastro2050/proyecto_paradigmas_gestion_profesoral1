# Quickstart — Versión 1: arranque y smoke test

## 1. Arranque

Un solo comando, desde la raíz del proyecto:

```powershell
docker compose up -d --build
```

La primera vez tarda unos minutos: descarga la imagen de PostgreSQL,
espera a que el motor responda, crea la base con sus 19 tablas y sus
catálogos, y compila la API. Al terminar:

| Qué | Dónde |
|---|---|
| API — diagnóstico | http://localhost:8029/ |
| Documentación interactiva | http://localhost:8029/docs |
| Listado de programas | http://localhost:8029/api/programa |
| PostgreSQL (SSMS o SQLTools, opcional) | `localhost,15441` · usuario `sa` |

> **¿La contraseña?** Está en el `docker-compose.yml`, a la vista: esta es
> una plantilla didáctica y esa es la excepción declarada en el Artículo 7
> de la [constitución](../../1_constitution.md). **Para correr el sistema
> no hace falta** —el compose se la entrega a los contenedores—; solo se
> necesita para conectarse por fuera con SSMS o SQLTools.
>
> **En su proyecto de aula eso no se copia:** ahí va en un `.env` fuera de
> git, con un `.env.example` adentro.

**Si cambia la contraseña**, no basta con editar el compose:

```powershell
docker compose down -v        # -v borra el volumen: la base olvida el sa viejo
docker compose up -d --build
```

Sin el `-v`, el usuario `sa` sigue existiendo dentro del volumen con la
clave anterior y el login falla — con un error que no menciona los
volúmenes por ninguna parte.

## 2. Smoke test

Los comandos van **numerados igual que los criterios de aceptación** de
[2_spec.md](2_spec.md). Si los siete pasan, la versión está terminada.

```powershell
# 1. Un solo comando: la API responde y dice qué versión es
curl http://localhost:8029/
#    → {"mensaje":"...","version":"v1","contratos":"/docs"}

# 2. El sistema arranca VACÍO: sin programas, el listado responde 204
curl -i http://localhost:8029/api/programa
#    → HTTP 204, sin cuerpo. Vacío no es error.

# 3. Crear y listar
curl -X POST http://localhost:8029/api/programa `
  -H "Content-Type: application/json" `
  -d '{"id":9001,"nombre":"Ingenieria de Sistemas","tipo":"Pregrado","nivel":"Profesional","fechaCreacion":"2005-01-15","fechaCierre":null,"numeroCohortes":"40","cantGraduados":"1250","fechaActualizacion":"2026-01-30","ciudad":"Medellin","facultad":1}'
#    → 200 creado
curl http://localhost:8029/api/programa
#    → 200 con total: 1

# 4. El ciclo de los cinco verbos
curl -X PUT http://localhost:8029/api/programa/9001 `
  -H "Content-Type: application/json" -d '{"nombre":"Ingenieria de Sistemas y Computacion","tipo":"Pregrado","nivel":"Profesional","fechaCreacion":"2005-01-15","fechaCierre":null,"numeroCohortes":"41","cantGraduados":"1300","fechaActualizacion":"2026-08-29","ciudad":"Medellin","facultad":1}'
#    → 200 filasAfectadas: 1

curl -X PATCH http://localhost:8029/api/programa/9001 `
  -H "Content-Type: application/json" -d '{"ciudad":"Bogota"}'
#    → 200 filasAfectadas: 1

curl http://localhost:8029/api/programa/9001
#    → el programa con el nombre nuevo y ciudad Bogota

# 4b. La pareja que enseña la diferencia: MISMO cuerpo, dos verbos
curl -i -X PUT http://localhost:8029/api/programa/9001 `
  -H "Content-Type: application/json" -d '{"nombre":"X","tipo":"Y","fechaCreacion":"2005-01-15","numeroCohortes":"1","cantGraduados":"1","fechaActualizacion":"2026-01-01","ciudad":"Z","facultad":1}'
#    → 422: al PUT le falta 'nivel' y reemplazar exige todo

curl -i -X PATCH http://localhost:8029/api/programa/9001 `
  -H "Content-Type: application/json" -d '{"nombre":"X","tipo":"Y","fechaCreacion":"2005-01-15","numeroCohortes":"1","cantGraduados":"1","fechaActualizacion":"2026-01-01","ciudad":"Z","facultad":1}'
#    → 200: al PATCH le basta con lo enviado

# 5. El borrado es LÓGICO, y se comprueba
curl -X DELETE http://localhost:8029/api/programa/9001
#    → 200 filasAfectadas: 1
curl -i http://localhost:8029/api/programa
#    → 204 otra vez: el único programa desapareció del listado
curl -i -X DELETE http://localhost:8029/api/programa/9001
#    → 404: para la API ya no existe

#    …pero la fila SIGUE en la base. Comprobarlo:
docker compose exec postgres bash -c '/opt/mssql-tools18/bin/sqlcmd `
  -S localhost -U sa -P "$MSSQL_SA_PASSWORD" -C -d gestion_local `
  -Q "SELECT id, activo FROM programa"'
#    → 9001 | 0

# 6. La validación es la frontera: nada de esto llega a la base
curl -i -X POST http://localhost:8029/api/programa `
  -H "Content-Type: application/json" -d '{"id":9002,"nombre":"X","tipo":"Y"}'
#    → 422 con errores: faltan nivel, fechaCreacion y los demás obligatorios

curl -i -X POST http://localhost:8029/api/programa `
  -H "Content-Type: application/json" `
  -d '{"id":"abc","nombre":"X","tipo":"Y","nivel":"Z","fechaCreacion":"2020-01-01","numeroCohortes":"1","cantGraduados":"1","fechaActualizacion":"2026-01-01","ciudad":"W","facultad":1}'
#    → 422: el tipo también es regla

# 7. La prueba de capas: sin base de datos
docker compose exec api-gestion uvicorn --project pruebas
#    → todas las verificaciones pasan, con un repositorio de mentiras
```

## 3. Regresión

Esta es la primera versión: no hay nada anterior que probar. **Desde la
v2**, esta sección conserva los smokes de todas las versiones cerradas y
todos deben seguir pasando antes de cerrar la nueva.

## 4. Si algo falla

| Síntoma | Causa probable |
|---|---|
| `Login failed for user 'sa'` | Se cambió la contraseña sin `docker compose down -v` (§1) |
| La API responde 500 en todo, con "No address associated with hostname" | La API arrancó antes que la base. `docker compose restart api-gestion` |
| El listado responde 200 con `total: 0` en vez de 204 | El controlador no está devolviendo `NoContent()` cuando la lista viene vacía (RF1) |
| El contenedor de PostgreSQL se reinicia solo | Contraseña que no cumple la política (8+ caracteres, mayúscula, minúscula, dígito y símbolo) o poca memoria: pide ~2 GB |
| Un inactivo aparece en el listado | A alguna consulta le falta `WHERE activo = TRUE` ([3_plan](3_plan.md) §4.2) |
| `bad interpreter: /bin/bash^M` | `db/init.sh` se guardó con finales de línea de Windows. Es lo que previene `*.sh text eol=lf` en `.gitattributes` |


---

## El front: la otra mitad de la versión

`docker compose up -d --build` levanta **tres** contenedores, no dos:

| Qué | Dónde |
|---|---|
| **LA PANTALLA** (lo que ve el usuario) | <http://localhost:8027> |
| Programas | <http://localhost:8027/programas> |
| La API | <http://localhost:8029> |

### La prueba automática

```powershell
python pruebas_humo/humo_front.py
```

Comprueba que las pantallas responden, que **los datos que muestran son los que
dio la API**, que no aparece jerga, y —lo que importa— que **con la API apagada
la pantalla sigue en pie con su aviso**. La apaga y la vuelve a encender sola.

**Lo que esa prueba NO puede hacer:** Blazor Server manda los clics por una
conexión persistente, así que un guion no puede llenar el formulario. Eso queda
para el recorrido a mano.

### El recorrido a mano, que hace una persona

1. Abra <http://localhost:8027>. Entre a **Programas**: la
   barra de direcciones dice `/programas` — una dirección de verdad, no
   un molde.
2. **Agregue** una ficha. Aparece en la tabla.
3. **Agréguela otra vez**, con el mismo código. Sale un aviso rojo con el
   mensaje que mandó la API — y **el formulario conserva lo que usted escribió**.
4. **Edítela** y use **«Guardar solo lo que cambié»** dejando campos vacíos:
   guarda, y lo que dejó en blanco queda como estaba.
5. Ahora **«Guardar la ficha completa»** con un campo obligatorio vacío: se
   rechaza. *El mismo formulario, dos comportamientos.*
6. **Retírela.** Pide confirmación y desaparece. Pero la fila **sigue en la
   base**: el borrado es lógico.
7. **Apague la API** y recargue la pantalla:
   ```powershell
   docker compose stop api-gestion
   ```
   La pantalla sigue cargando, con su menú y su pie, y dice que el servicio no
   está disponible. **Eso es lo que demuestra que son dos procesos.** Vuelva a
   levantarla con `docker compose start api-gestion`.
