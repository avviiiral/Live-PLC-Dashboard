# API Reference
Base path: `/api/v1/`

- GET /health/ — public health endpoint.
- companies/, plants/, lines/, stations/, plcs/, tags/ — authenticated CRUD APIs; writes are staff-only.
- POST /collectors/register/ — staff-only collector provisioning; returns a one-time token.
- POST /collectors/heartbeat/ — collector authentication via X-Collector-Token.
- POST /production/ingest/ — collector-authenticated idempotent event ingestion; validates station, PLC and collector assignment.
- GET /production-events/ — authenticated paginated history; supports station, result, start, end and ordering.
- GET /dashboard/summary/ — authenticated aggregate counters.
- alarms/ — authenticated alarm records.

OpenAPI: `/api/schema/`; Swagger UI: `/api/docs/`.
