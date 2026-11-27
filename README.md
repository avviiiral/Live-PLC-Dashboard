# Live PLC Dashboard

Industrial IoT platform foundation for configurable plant hierarchy, factory-side PLC collection, production-event tracking and manufacturing monitoring.

## Architecture

- **Angular frontend** — dashboard overview and paginated production history.
- **Django backend** — configuration APIs, authentication, normalized persistence, collector ingestion and WebSocket event broadcasting.
- **Local PLC collector** — factory-network polling, modular adapters, event detection and persistent offline event queue.

The collector initiates outbound communication to the backend. The central backend does not need direct access to internal PLC network addresses.

## Technology

Angular 19 · TypeScript · Django · Django REST Framework · Django Channels · SQLite / PostgreSQL · Siemens S7 · Modbus TCP · Mock PLC.

## Repository structure

- `backend/` — Django service, domain models, API and Channels consumer.
- `frontend/` — Angular application.
- `collector/` — independent PLC collector and protocol adapters.
- `documentation/` — architecture, database, PLC, API, deployment and setup guides.

## Windows quick start

### Backend

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend\requirements.txt
Copy-Item .env.example .env
python backend\manage.py migrate
python backend\manage.py createsuperuser
python backend\manage.py runserver 0.0.0.0:8000
```

### Frontend

```powershell
cd frontend
npm install
npm start
```

### Collector

After creating the hierarchy, registering a collector as a staff user, assigning it stations and supplying real PLC/tag IDs in its configuration:

```powershell
python -m pip install -r collector\requirements.txt
$env:COLLECTOR_API_BASE_URL = "http://127.0.0.1:8000"
$env:COLLECTOR_TOKEN = "<provisioned-token>"
$env:COLLECTOR_CONFIG_PATH = "collector/config/example.json"
python -m collector.main
```

Do not commit the provisioned token or real factory network configuration.

## Database

SQLite is the default local database. For PostgreSQL set `DB_ENGINE=postgresql` and configure `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST` and `POSTGRES_PORT`.

Copy `.env.example` to `.env` and replace sample values. The real `.env`, database files and local collector queue are ignored by Git.

## API and real-time endpoints

- REST API base: `/api/v1/`
- OpenAPI schema: `/api/schema/`
- Swagger UI: `/api/docs/`
- Station WebSocket: `/ws/stations/<station-uuid>/`

The API currently includes hierarchy CRUD endpoints, collector registration/heartbeat, production event ingestion, paginated production history, alarms and dashboard aggregate counts.

## Excel-like production records

`ProductionEvent` is the canonical source of truth. Its JSON payload snapshots the configured tag values at event time. Historical payloads therefore remain intact when station tag configuration changes.

The Angular history page renders these records in a station-filtered, server-paginated table. Dynamic per-station SQL tables are intentionally avoided: runtime DDL increases schema migration and SQLite/PostgreSQL portability risks without improving the canonical record.

## Tests

```powershell
python backend\manage.py test
python -m unittest discover -s collector/tests
cd frontend
npm test
```

Tests are included as a starting suite. Run them in your local environment before relying on the software. This repository update has not been executed against a local Python/Node/PostgreSQL runtime as part of this GitHub-only session.

## Implementation status and limitations

The current branch provides a development foundation, not a certified or production-hardened SCADA product.

**Implemented in source**
- Normalized company → plant → line → station → PLC → tag models and basic REST CRUD APIs.
- Collector token hashing, station assignments and idempotent production event ingestion.
- Mock, Siemens S7 and Modbus TCP adapter implementations.
- Configurable trigger edge/debounce/result mapping foundation.
- Persistent SQLite collector event queue and retry loop.
- Basic Channels station event consumer.
- Angular overview, production history table and system guidance.
- SQLite/PostgreSQL settings, Dockerfiles, Compose and technical documentation.

**Still required before production**
- End-to-end mock PLC event flow and complete acceptance tests.
- Automated migrations committed to the repository and verification against both database engines.
- Collector configuration delivery, token rotation and provisioning workflow improvements.
- Full station-wise and tenant-level authorization for REST and WebSocket subscribers.
- Proper login UI, route guards, user/role administration and full hierarchy management screens.
- Tag telemetry ingestion, alarm lifecycle, shift/report aggregates, CSV/XLSX export and advanced charts.
- Redis Channels configuration, rate limiting, auditing, secure production settings and deployment validation.
- Verification of S7/Modbus library APIs and address/data representation against physical PLC hardware.

Physical PLC connectivity is **hardware-unverified**. PostgreSQL and Angular production build compatibility must be tested in an environment with those services available.

## Documentation

Start with:
- [Architecture](documentation/ARCHITECTURE.md)
- [Database design](documentation/DATABASE_DESIGN.md)
- [PLC configuration](documentation/PLC_CONFIGURATION.md)
- [Collector setup](documentation/COLLECTOR_SETUP.md)
- [API reference](documentation/API_REFERENCE.md)
- [Real-time communication](documentation/REALTIME_COMMUNICATION.md)
- [Windows setup](documentation/WINDOWS_SETUP.md)
- [Deployment](documentation/DEPLOYMENT.md)
- [Troubleshooting](documentation/TROUBLESHOOTING.md)

## Repository

https://github.com/avviiiral/Live-PLC-Dashboard

Development branch: `feature/live-plc-dashboard-platform`
