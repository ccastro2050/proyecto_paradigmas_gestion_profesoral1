# Módulo Gestión Profesoral — ejemplo de referencia (Python)

Este repositorio contiene **dos cosas distintas**, y conviene no confundirlas:

| | Qué es |
|---|---|
| [`ProyectosDeAula/`](ProyectosDeAula/) | **El material del curso**: la metodología, los documentos de módulo y los scripts de base de datos. Es lo que ya conocen |
| Todo lo demás | **El ejemplo de referencia** del módulo Gestión Profesoral: su versión 1, construida siguiendo esa metodología al pie de la letra |

El ejemplo no es un sistema para descargar: es un **molde de método**. Se
ejecuta, se estudia, y se reconstruye.

**El stack es el de paradigmas**: Python, FastAPI y PostgreSQL. El mismo
módulo existe en otro repositorio con otro lenguaje — y esa es justamente la
demostración de que **la metodología y los contratos no dependen del stack**.

---

## 1. Arranque: un solo comando

Solo hace falta **Docker Desktop**. No hay que instalar Python ni PostgreSQL.

```powershell
git clone https://github.com/ccastro2050/proyecto_paradigmas_gestion_profesoral1.git
cd proyecto_paradigmas_gestion_profesoral1
docker compose up -d --build
```

| Qué | Dónde |
|---|---|
| **LA PANTALLA** (lo que ve el usuario) | http://localhost:8027 |
| Programas | http://localhost:8027/programas |
| **API — documentación interactiva** | http://localhost:8029/docs |
| Diagnóstico | http://localhost:8029/ |
| Listado | http://localhost:8029/api/programa |
| PostgreSQL (DBeaver o pgAdmin, opcional) | `localhost:15441` · usuario `gestion` |

Pruebe en `/docs`: un `PUT` al que le falte un campo responde **422**; el
**mismo cuerpo** por `PATCH` responde **200**. Esa diferencia no la decide un
`if`: la decide el tipo del cuerpo.

### Los días siguientes

```powershell
docker compose up -d          # encender
docker compose down           # apagar (los datos se conservan)
docker compose down -v        # resetear la base a su estado original
```

Si edita un `.py`, **no hay que hacer nada**: el código está montado y
`uvicorn --reload` recarga solo.

## 2. Qué construye la versión 1

El CRUD completo de **`programa`** de punta a punta: controlador, servicio,
repositorio, interfaces, modelos por verbo y una prueba que corre **sin base
de datos**.

**La tabla arranca con 191 filas** **del Excel del módulo**: el smoke test
recorre el ciclo completo sobre datos de verdad —**listar → crear → total
192 → borrar → total 191 otra vez**— y compara contra la pantalla lo que la
API devolvió. De dónde salió cada columna está en `db/init.sql`, encima
del `INSERT`, y en §3 de `5_data_model.md`. Los catálogos que además
vienen cargados (218 filas de `area_conocimiento`) son infraestructura: la v1 no los nombra.

**La v1 del curso pide cinco tablas sin clave foránea.** Este repositorio construye **una sola,
completa**: es el molde. Las demás son el mismo patrón con otros nombres. El
equipo que tome este ejemplo lo revisa y, **si está de acuerdo, lo retoma y
lo completa; si no, lo rehace a su manera**. Lo que no puede es cambiar la
especificación sin pasar por sus compuertas.

## 3. Estructura

```
proyecto_paradigmas_gestion_profesoral1/
├── db/init.sql                         la base COMPLETA (19 tablas, artefacto DADO)
├── api_gestion/
│   ├── main.py                         arma la app y registra el router
│   ├── controllers/                    CAPA 1: HTTP — códigos de estado y JSON
│   ├── models/                         la frontera: Pydantic valida → 422
│   ├── servicios/                      CAPA 2: negocio — no conoce HTTP ni el motor
│   │   ├── abstracciones/                la interfaz que la capa 1 conoce
│   │   └── ensamblador.py                el ÚNICO sitio que decide el motor
│   ├── repositorios/                   CAPA 3: datos — el SQL a mano
│   │   └── abstracciones/                la interfaz que la capa 2 conoce
│   └── pruebas/                        el servicio con un repositorio de mentiras
├── docs/spec_kit/                      LA FUENTE DE VERDAD (ver abajo)
├── postman/                            los endpoints listos para probar con clics
├── docker-compose.yml                  TODO el sistema declarado en un archivo
└── ProyectosDeAula/                    el material del curso
```

## 4. Las especificaciones

Empiece por **[SDD_SPECKIT.md](docs/SDD_SPECKIT.md)**: qué es SDD, qué es
GitHub Spec Kit, y cómo se arman estos documentos.

| Documento | Contenido |
|---|---|
| [PLAN_V1.md](PLAN_V1.md) | **El plan con el que se construyó esta versión**: los hallazgos, las decisiones, los ocho pasos y el prompt |
| [SDD_SPECKIT.md](docs/SDD_SPECKIT.md) | **Empiece por aquí**: el método |
| [1_constitution.md](docs/spec_kit/1_constitution.md) | Las reglas permanentes del proyecto |
| [0_mapa_versiones.md](docs/spec_kit/versiones/0_mapa_versiones.md) | La ruta v1 → v4 y qué tabla entra en cada versión |
| [2_spec.md](docs/spec_kit/versiones/v1_programa/2_spec.md) | QUÉ construir, los criterios y las **Clarificaciones** |
| [3_plan.md](docs/spec_kit/versiones/v1_programa/3_plan.md) | CÓMO: el stack, las capas y el **chequeo de constitución** |
| [4_research.md](docs/spec_kit/versiones/v1_programa/4_research.md) | Las decisiones con la alternativa que se descartó |
| [5_data_model.md](docs/spec_kit/versiones/v1_programa/5_data_model.md) | La tabla y quién no puede escribir qué |
| [6_contracts.md](docs/spec_kit/versiones/v1_programa/6_contracts.md) | Los 7 endpoints con TODOS sus códigos |
| [7_quickstart.md](docs/spec_kit/versiones/v1_programa/7_quickstart.md) | El smoke test, comando por comando |
| [8_tasks.md](docs/spec_kit/versiones/v1_programa/8_tasks.md) | Las fases, cada una con su verificación |
| [9_checklist.md](docs/spec_kit/versiones/v1_programa/9_checklist.md) | **La compuerta 3**: se firma ANTES de programar |

## 5. Lo que hay que mirar del código

| Si quiere entender… | Abra |
|---|---|
| Por qué el 422 sale solo | `api_gestion/models/programa.py` |
| Por qué PUT y PATCH se comportan distinto | los **tres** modelos: la diferencia es el tipo, no un `if` |
| Dónde está el SQL | `api_gestion/repositorios/` — a la vista y parametrizado |
| Por qué el servicio no sabe qué es un 404 | `api_gestion/servicios/servicio_programa.py` |
| Que las capas son de verdad | `api_gestion/pruebas/prueba_capas.py`, que corre **con la base apagada** |
