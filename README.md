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

## Despliegue con Docker
```bash
docker compose up --build
```
App en http://localhost:6600, backend en http://localhost:8000.

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

## Seguridad
- Claves de IA **solo** por variables de entorno (nunca en código).
- JWT + bcrypt. Permisos por rol en backend (`require_*`) y frontend (`can()`).
- Cada llamada a IA se registra en `ai_usage` para auditoría y control de costos.
