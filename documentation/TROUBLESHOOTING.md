# Troubleshooting
- DB_ENGINE must be sqlite or postgresql.
- PostgreSQL errors: verify database, credentials, host/port and psycopg installation.
- Collector refuses startup: check configuration, backend URL and provisioned collector token.
- PLC connection errors: verify collector-to-PLC routing, firewall and protocol-specific parameters.
- No production events: verify trigger tag name/address, active state, debounce and result mapping.
- WebSocket failures: verify signed-in Django session, proxy upgrade and channel layer configuration.
- Queue growth: inspect backend availability, collector token validity and ingestion responses.
