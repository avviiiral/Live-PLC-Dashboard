# Architecture

The platform comprises Angular, Django REST/Channels and one or more factory-side collectors.

## Configuration source of truth
Company, plant, line, station, PLC device, PLC tag, event rules and collector assignments live in Django's database. The root `.env` contains deployment-wide settings only. PLC-specific configuration is not duplicated in JSON files.

## Same-computer collector
Set `COLLECTOR_MODE=local` and use a loopback API URL. Backend trusts this mode only for a direct loopback peer and resolves the Local Development Collector record with explicit station assignments. No collector token is sent. Do not expose tokenless local mode on a LAN-bound backend.

## Factory-LAN collector
Set `COLLECTOR_MODE=lan`, backend LAN URL and one persistent machine-level token. The backend scopes configuration and ingestion to stations assigned to that machine's CollectorAgent. A single agent can own multiple stations; assigning a new station does not require another credential.

## Runtime flow
1. Collector reads the root `.env`.
2. Collector requests active assigned stations, enabled PLCs and enabled tags.
3. It creates one adapter and detector per PLC.
4. It polls, snapshots result transitions and enqueues events with stable UUIDs.
5. Backend validates station assignment and PLC/station relationship, persists idempotently and broadcasts new events.
6. Collector periodically refreshes assignments and applies additions/removals without editing JSON.

The backend does not need direct routing to PLC private IPs. Collectors initiate outbound requests. Production should use TLS, PostgreSQL and a production-capable Channels layer.
