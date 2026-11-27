# Architecture
The platform has three components: Angular UI, central Django REST/Channels service, and an independent PLC collector that runs inside the factory network. The collector initiates outbound communication to the backend; the central backend does not require direct access to PLC private IP addresses.

Collector flow: load local station configuration → connect to PLC → poll configured tags → detect trigger state transition → snapshot values → enqueue an event with a stable UUID → send to backend → remove only after acknowledgement.

The backend validates collector token, station assignment and PLC-to-station relationship, then persists ProductionEvent idempotently and broadcasts accepted events to station WebSocket subscribers.

ProductionEvent is the canonical source of truth. Its JSON payload snapshots dynamic tag values at event time, providing the Excel-like station record without runtime-generated SQL tables. Redis Channels and PostgreSQL should be used for multi-worker production; InMemoryChannelLayer is development-only.
