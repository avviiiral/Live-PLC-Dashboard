# Deployment
Production readiness checklist:
- DEBUG=false, strong secret key and restrictive allowed hosts.
- HTTPS, secure cookies, CSRF trusted origins and a hardened reverse proxy.
- PostgreSQL backups, monitoring and restricted network access.
- Redis-backed Channels for multiple ASGI workers.
- Angular production build served by a web server.
- Collector hosts run under least-privilege OS accounts with protected credentials and local queue files.
- Monitor collector heartbeat age, pending queue size and PLC read errors.
- Verify physical S7/Modbus address maps on target hardware.

Docker Compose is a local integration starting point. The sample credentials in .env.example must be replaced before running it; it is not a hardened production manifest.
