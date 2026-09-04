# Tareas — Versión 1: el orden de construcción

> **Versión 1** ([mapa](../0_mapa_versiones.md)) · Rige la
> [constitución](../../1_constitution.md).
>
> | Documento | Contenido |
> |---|---|
> | [2_spec.md](2_spec.md) | QUÉ construir y los criterios de aceptación |
> | [3_plan.md](3_plan.md) | CÓMO: el stack, las capas y sus decisiones |
> | [4_research.md](4_research.md) | Las decisiones, con lo que se descartó |
> | [5_data_model.md](5_data_model.md) | La tabla, sus semillas y quién escribe qué |
> | [6_contracts.md](6_contracts.md) | Los 7 endpoints exactos |
> | [7_quickstart.md](7_quickstart.md) | Arranque y smoke test |
> | [8_tasks.md](8_tasks.md) | El orden de construcción por fases |
> | [9_checklist.md](9_checklist.md) | La compuerta 3: se firma ANTES de programar |
> | [GUIA_IA1.md](GUIA_IA1.md) | Construirla con ayuda de una IA |

---

> Cada fase termina en algo **que se puede comprobar**. No se pasa a la
> siguiente sin verificar la anterior.

## Fase 1 — La base de datos

- [ ] Derivar `db/init.sql` del script del curso, aplicando **las cinco
      correcciones** con su marca `[Cn]` en la cabecera.
- [ ] Montarlo en `/docker-entrypoint-initdb.d/`: PostgreSQL lo ejecuta
      **solo la primera vez**, cuando el volumen está vacío.

**Verificación:**

```powershell
docker compose up -d postgres
docker compose exec postgres psql -U gestion -d gestion_local `
  -c "SELECT COUNT(*) FROM programa"
#  → 0
```

## Fase 2 — El esqueleto de la API

- [ ] `requirements.txt`, `Dockerfile` y `main.py` con **solo** el
      diagnóstico `GET /`.
- [ ] El servicio en el `docker-compose.yml`, con `depends_on:
      service_healthy`.

**Verificación:** `GET http://localhost:8029/` responde `"version": "v1"`.
*Todavía no habla con la base.*

## Fase 3 — Los modelos: la frontera

- [ ] Las **tres** clases Pydantic, una por verbo.
- [ ] `id` como **texto** de 1 a 6 (C1), no como entero.

**Verificación:** los módulos importan sin error, y `/docs` ya muestra los
esquemas.

## Fase 4 — Las interfaces y el servicio

- [ ] `IRepositorioAreaConocimiento` e `IServicioAreaConocimiento`.
- [ ] `ServicioAreaConocimiento`, que lanza `ValueError` y `LookupError` —
      **nunca códigos HTTP**.

**Verificación:** la prueba de capas de la Fase 8 ya podría escribirse; el
servicio no importa nada de FastAPI.

## Fase 5 — El repositorio

- [ ] `RepositorioAreaConocimientoPostgreSQL` con `text()` y `:parametro`.
- [ ] **Todas** las consultas filtran por `activo = TRUE`.
- [ ] El borrado lógico, en **una sola** consulta.
- [ ] `ensamblador.py`.

**Verificación:** desde el contenedor,

```powershell
docker compose exec api-gestion python -c "import asyncio, os; from repositorios.repositorio_programa_postgresql import RepositorioAreaConocimientoPostgreSQL as R; print(len(asyncio.run(R(os.environ['DB_POSTGRES']).obtener_todos(1000))))"
#  → 0
```

## Fase 6 — El controlador

- [ ] Los 7 endpoints.
- [ ] El listado vacío responde **204**, no 200 con lista vacía.
- [ ] `ValueError` → 400 · `LookupError` → 404 · lo demás → 500.

**Verificación:** los criterios 1 a 4 de [2_spec](2_spec.md).

## Fase 7 — Los desenlaces de error

- [ ] `PATCH {}` → **400** (no 404).
- [ ] `?limite=0` → **400**.
- [ ] Un id repetido → **500**: la llave la defiende la base.
- [ ] Un id de más de 6 caracteres → **422**, de Pydantic.

**Verificación:** el criterio 6 — **los cuatro casos, uno por uno**.

## Fase 8 — La prueba de capas

- [ ] `pruebas/prueba_capas.py` con un repositorio que guarda en una lista.

**Verificación, y es la que importa:**

```powershell
docker compose stop postgres
docker compose exec api-gestion python pruebas/prueba_capas.py
#  → todas las comprobaciones en OK, CON LA BASE APAGADA
docker compose start postgres
```

> Si esto pasa sin base de datos, **la separación de capas es real** y no un
> dibujo en un documento.

## Fase 9 — Cierre

- [ ] El smoke test de [7_quickstart](7_quickstart.md) corrido **por una
      persona**.
- [ ] [9_checklist.md](9_checklist.md) firmada.
- [ ] La colección de Postman y el README.
- [ ] Commit y **tag `v1`**.


## El FRONT: la otra mitad de la versión

Va **después** de que la API responda y **antes** del cierre. Sin esta fase la
versión está a medias.

| # | Tarea | Archivo |
|---|---|---|
| 1 | El proyecto Blazor Server, **sin ningún paquete de acceso a datos** | `front_blazor/FrontGestion.csproj` |
| 2 | `ServicioPrograma`: seis métodos, uno por operación | `Servicios/ServicioPrograma.cs` |
| 3 | El tipo `Resultado<T>`, para que las páginas no vean códigos de estado | `Servicios/ServicioPrograma.cs` |
| 4 | La traducción del sobre de error a textos para el usuario | `Servicios/ServicioPrograma.cs` |
| 5 | El marco y el menú, con **un enlace por pantalla** | `Components/Layout/` |
| 6 | La pantalla del CRUD, con los **dos botones** de guardar | `Components/Pages/Programas.razor` |
| 7 | Los estilos, escritos a mano | `wwwroot/app.css` |
| 8 | El servicio en el compose, en el **8027**, sin `depends_on: postgres` | `docker-compose.yml` |
| 9 | La prueba de humo del front | `pruebas_humo/humo_front.py` |

**Verificación de la fase:**

- [ ] `http://localhost:8027/programas` muestra las filas.
- [ ] El recorrido a mano de `7_quickstart.md` se hizo completo.
- [ ] `python pruebas_humo/humo_front.py` da todo en verde.
- [ ] **Con `docker compose stop api-gestion`, la pantalla sigue en pie
      con su aviso y sin un solo dato.**
