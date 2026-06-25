# ABAP Factory AI

Plataforma web para **generar, analizar, corregir, documentar y probar código ABAP** (SAP ECC y S/4HANA) asistida por IA. Proyecto independiente — comparte la *arquitectura* (FastAPI + React + Tailwind) con otros productos pero no comparte código de dominio.

- **Backend**: FastAPI + SQLAlchemy 2 + PostgreSQL + Pydantic v2 + APScheduler
- **Frontend**: React 18 + Vite + TailwindCSS + Framer Motion + Monaco Editor (Context API)
- **IA conmutable**: capa de abstracción que soporta **Claude (Anthropic)** y **OpenAI**, elegible por agente. Claves por variables de entorno.

## Módulos

1. Generador de código ABAP (ECC / S4 / clásico / OO, reports, ALV/SALV, CDS, AMDP, RAP, BAPIs, BAdIs, IDocs, OData…)
2. Selector de contexto SAP (versión, módulo, tipo, complejidad, naming, transporte, mandante, ambiente)
3. Generador de especificación técnica (funcional, objetos, BAPIs, riesgos, transporte, rollback)
4. Editor ABAP inteligente (Monaco): explicar, refactorizar, procedural→OO, ECC→S/4, limpieza legacy
5. Analizador de Dumps ST22 (causa raíz, ubicación, código corregido, severidad, historial)
6. Code Inspector / ATC Advisor (score, hallazgos, reglas, compatibilidad S/4)
7. Generador de pruebas ABAP Unit (GIVEN/WHEN/THEN, mocks, cobertura)
8. Protocolos de prueba (unitaria, técnica, funcional, integración, regresión, performance, UAT)
9. Gestión de clientes y proyectos ABAP
10. Dashboard de métricas
11. Roles y permisos (admin, líder técnico, consultor, QA, cliente solo lectura)
12. Exportaciones (.abap, PDF, Excel)
13. 6 agentes IA especializados (ABAP ECC, S/4HANA, WebDynpro, Dump Solver, Code Inspector, QA)

## Los 6 agentes

| key | Agente | Especialidad |
|-----|--------|--------------|
| `abap_ecc` | ABAP Senior ECC | clásico, reports, ALV, enhancements, BAPIs, performance |
| `abap_s4` | ABAP S/4HANA | CDS, AMDP, RAP, OData, simplification items |
| `webdynpro` | WebDynpro ABAP | componentes, context, views, controllers, plugs |
| `dump_solver` | Dump Solver | ST22, causa raíz, corrección |
| `inspector` | Code Inspector / ATC | calidad, seguridad, performance, clean code |
| `qa_abap` | QA ABAP | ABAP Unit, pruebas funcionales/regresión/integración |

## Requerimiento → Solución (orquestador)

Pega o **sube** un requerimiento funcional (correo, acta, spec) y el sistema **clasifica**
qué se necesita y lo **resuelve de punta a punta**:
- `nuevo_desarrollo` → genera el programa/objeto (código + explicación + calidad).
- `correccion_bug` / `mejora_enhancement` / `ajuste` → aplica el cambio sobre el código existente
  (pegado), con diff de cambios.
- `fix_dump` → analiza el dump y entrega el código corregido.
- `migracion` → migra el código existente a S/4HANA / ABAP Cloud.

Devuelve el tipo detectado, el plan, el código, la explicación, los cambios y las notas de
confianza; guarda el resultado como artefacto versionable del proyecto. Endpoint `/solution/build`.

- **Lee PDF / Word / texto**: sube el documento funcional y el servidor extrae el texto
  (`pypdf` / `python-docx`). Endpoint `/solution/extract-file`.
- **Entrega completa (un clic)**: con la casilla activada, además del código encadena la
  **especificación técnica + pruebas ABAP Unit + documento técnico paso a paso**, todo
  persistido y descargable en PDF.

## Migración, calidad y documentación

- **Migración ECC → S/4HANA / ABAP Cloud**: pega código ECC y obtén la versión modernizada,
  con cada cambio explicado (antes/después + motivo), simplification items, compatibilidad y
  pasos manuales. Destinos: S/4 on-premise, S/4 Cloud Public (ABAP Cloud) y BTP ABAP. Export PDF.
- **Code Inspector**: revisa código **creado** (carga un artefacto del proyecto) o **pegado**.
- **Documento técnico (objeto por objeto)**: lista CADA objeto a crear/modificar/usar con su
  nombre exacto, tipo, paquete y dependencias, + guía **paso a paso**, plan de transporte y
  rollback. **Descargable en PDF**.
- **Nomenclaturas dinámicas**: cada empresa define sus patrones por tipo de objeto
  (tablas, clases, CDS, RAP, etc.) con marcadores `Z{MODULE}_{NAME}`; el generador los aplica
  automáticamente. Preview en vivo.

## ABAP moderno (ABAP Cloud / BTP / RAP)

Soporta todos los entornos: ECC, S/4HANA on-premise, S/4HANA Cloud Private/Public y
**SAP BTP ABAP Environment (Steampunk)**. Tipos modernos: RAP (managed/unmanaged/draft),
CDS de interfaz/proyección/analítica, Behavior Definition/Implementation, Service
Definition/Binding (OData V4/V2), EML, Fiori Elements y APIs liberadas. Un **7º agente
especializado** (`abap_cloud`) cubre ABAP Cloud/BTP/RAP con sus restricciones (solo APIs C1).

## Inteligencia y automatización (el consultor hace y sabe lo mínimo)

- **Loop self-healing**: con *Auto-optimizar* activado, el sistema genera → corre el linter
  estático → inspecciona con IA → si la calidad es baja, **se refactoriza solo** y vuelve a
  evaluar, hasta alcanzar el score objetivo (o agotar iteraciones). El consultor recibe código
  que ya pasó calidad.
- **Linter ABAP estático (sin IA)** + **guardrails duros**: detecta SELECT *, SELECT en LOOP,
  DELETE/UPDATE sin WHERE (crítico/bloqueante), BREAK-POINT, falta de AUTHORITY-CHECK, etc.
  Es determinista, instantáneo y no gasta llamadas a IA ni ciclos en SAP. Endpoint `/generation/validate`.
- **Memoria del cliente (RAG)**: ingiere objetos Z, diccionario y estándares del cliente una vez;
  el generador los reutiliza automáticamente para producir código consistente con su landscape.
  Sin dependencias externas (recuperación por relevancia de términos).
- **Mapa de confianza**: cada generación marca los FM/tablas/BAPIs inciertos para que el consultor
  revise solo ese 5% riesgoso, no el 100%.
- **Recetas**: plantillas 1-clic (ALV, OData, CDS, IDoc, RFC-BAPI, job) — elige y completa 1-2 campos.
- **Refinamiento conversacional**: edita un artefacto con lenguaje natural ("pásalo a SALV",
  "agrégale filtro por sociedad") → crea una nueva versión.
- **Ingesta de spec**: pega un correo o spec funcional → el sistema extrae el requerimiento estructurado.

## Instalación (desarrollo local)

### Requisitos
- Python 3.11+, Node 20+, PostgreSQL 16 (o Docker)

### 1. Base de datos (Docker, recomendado)
```bash
docker compose up -d db
```
> Postgres queda en el puerto **6602** para no chocar con otros proyectos locales.

### 2. Backend
```bash
cd backend
python -m venv .venv
source .venv/Scripts/activate   # Git Bash en Windows
pip install -r requirements.txt
cp .env.example .env             # edita y pon ANTHROPIC_API_KEY u OPENAI_API_KEY
python seed.py                   # crea usuarios y datos demo
uvicorn app.main:app --reload --port 8000
```
- API docs: http://localhost:8000/api/docs
- Health: http://localhost:8000/health (muestra qué proveedores de IA están activos)

### 3. Frontend
```bash
cd frontend
npm install
npm run dev
```
- App: http://localhost:6600 (proxy `/api` → backend en 8000)

### Usuarios demo (password `demo1234`)
| email | rol |
|-------|-----|
| admin@abapfactory.ai | admin |
| lider@abapfactory.ai | líder técnico |
| consultor@abapfactory.ai | consultor |
| qa@abapfactory.ai | QA |
| cliente@abapfactory.ai | cliente solo lectura |

## Entrega y transporte (abapGit / ADT)

- **Paquete abapGit (.zip)**: descarga todos los artefactos del proyecto en formato abapGit
  (carpeta `src/` + `.abapgit.xml` + `manifest.json`), listo para hacer **pull/push** desde tu
  repo abapGit y activar/transportar en SAP. Endpoint `/exports/project/{id}/abapgit.zip`.
- **Destino por proyecto**: registra repo git, branch, paquete SAP y orden de transporte
  (metadatos, **nunca credenciales** — el push real lo hace tu repo git).
- **Diff visual ECC ↔ S/4**: en Migración, vista lado a lado o diff coloreado del antes/después.

## Despliegue local (dev)
```bash
docker compose up --build
```
App en http://localhost:6600, backend en http://localhost:8000.

## Despliegue en producción (VPS + Docker + Caddy TLS)
```bash
cp .env.prod.example .env.prod   # completa claves IA, DB y dominio
nano Caddyfile                   # pon tu dominio real
bash deploy.sh                   # build + up + seed; Caddy emite TLS automático
```
- `docker-compose.prod.yml`: db + backend + frontend + **Caddy** (TLS automático).
- Verifica en `https://<tu-dominio>/health`.
- `.env.prod` está en `.gitignore` (no se versiona).

## Variables de entorno clave (`backend/.env`)
| Variable | Descripción |
|----------|-------------|
| `DEFAULT_AI_PROVIDER` | `claude` u `openai` |
| `ANTHROPIC_API_KEY` | clave Claude (opcional si usas OpenAI) |
| `OPENAI_API_KEY` | clave OpenAI (opcional si usas Claude) |
| `CLAUDE_DEFAULT_MODEL` | ej. `claude-opus-4-8` |
| `OPENAI_DEFAULT_MODEL` | ej. `gpt-4o` |
| `USD_TO_CLP` | tipo de cambio para reportar costos en CLP |

> Si ninguna clave está configurada, los endpoints de IA responden **503** con un mensaje claro; el resto de la app (proyectos, historial, dashboard) funciona igual.

## Robustez y resiliencia
- **Manejo global de errores**: respuestas JSON limpias (sin stack traces) para errores de BD,
  validación e inesperados; cada uno con `request_id` para trazabilidad.
- **Logging con request-id** y tiempo por request (middleware).
- **Resiliencia IA**: timeout por llamada + **reintentos con backoff** ante errores transitorios
  (rate limit, timeout, 5xx, overloaded). Si el proveedor elegido falla, cae al otro.
- **Guard de costo diario** por usuario (`DAILY_AI_COST_LIMIT_USD`): corta con **429** al superarlo.
- **Límite de tamaño de entrada** (`MAX_INPUT_CHARS`): rechaza payloads gigantes con **422**.
- **Pool de BD** con `pool_pre_ping`, reciclaje y overflow; `/health` reporta estado de BD e IA.
- **No arranca en `ENV=prod` con `SECRET_KEY` por defecto.**
- **Frontend**: `ErrorBoundary` por vista (un fallo no tumba la app) + interceptor axios que
  avisa de 429/5xx/timeout/sin-conexión y maneja 401.

## Roles dinámicos (RBAC a bajo nivel)
- **Crea roles a medida** con permisos granulares (≈24 claves: `code.generate`, `code.approve`,
  `dump.analyze`, `migration.run`, `roles.manage`, `costs.view`, …) o `*` (superusuario).
- 5 roles base del sistema (no borrables) + los que definas. Asignación de rol dinámico por
  usuario; los usuarios sin rol dinámico usan el mapeo de su rol base.
- Backend: `require_perm("code.generate")`, etc. — toda la autorización pasa por permisos.
  Frontend: `hasPerm("code.approve")` / `can("create")`. Pantalla **Roles y permisos**.

## Lectura de requerimiento PDF/Word + OCR
- Sube/arrastra el documento funcional; el servidor extrae el texto (`pypdf`/`python-docx`).
- **OCR** para PDFs escaneados (best-effort: requiere `tesseract` + `poppler`, ya incluidos en
  el Dockerfile; si faltan, avisa para pegar el texto).

## Seguridad
- Claves de IA **solo** por variables de entorno (nunca en código).
- **JWT con access (8h) + refresh (14 días)**: el frontend refresca el access automáticamente;
  los refresh tokens no autorizan endpoints (solo `/auth/refresh`). Configurable.
- **2FA (TOTP)**: cada usuario activa verificación en dos pasos (Google Authenticator/Authy/…)
  desde *Seguridad (2FA)* — QR + código manual. El login pide el código si está activo.
- **Auditoría**: toda acción mutante queda registrada (usuario, acción, ruta, estado, IP, fecha)
  en `audit_logs`; visible en *Auditoría* (permiso `audit.view`).
- bcrypt + autorización por **permisos granulares** (backend `require_perm`, frontend `hasPerm`).
- **Rate limiting del login** (anti fuerza bruta): por IP+email, configurable
  (`LOGIN_RATE_MAX`, `LOGIN_RATE_WINDOW_SEC`); responde **429** al superar el límite.
- Cada llamada a IA se registra en `ai_usage` para control de costos.

## CI (GitHub Actions)
`.github/workflows/ci.yml` corre en cada push/PR: **smoke test** del backend (TestClient+SQLite)
y **build** del frontend. Sin necesidad de Postgres en CI.

## Backups de la base de datos
- `bash scripts/backup.sh` → dump comprimido con fecha en `backups/` + rotación (14 días por defecto).
- Programar en cron (VPS): `0 3 * * * cd /opt/abap-factory-ai && bash scripts/backup.sh >> backups/backup.log 2>&1`
- Restaurar: `bash scripts/restore.sh backups/abap_factory_YYYYmmdd_HHMMSS.sql.gz` (pide confirmación).
- La carpeta `backups/` está en `.gitignore` (los dumps no se versionan).
