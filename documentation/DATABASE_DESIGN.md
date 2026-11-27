# Database Design
Entities include Company, Plant, ProductionLine, Station, PLCDevice, PLCTag, CollectorAgent, CollectorHeartbeat, TagReading, ProductionEvent, AlarmEvent and AuditLog. UUIDs identify external configuration objects and production events. Foreign keys protect historical references; uniqueness constraints protect scoped plant/line/station codes and PLC tag names.

## Excel-like production rows
ProductionEvent stores a JSON payload containing the entire tag snapshot at event time. Historical values remain intact after the current tag configuration changes. The Angular production grid is paginated server-side and renders payload data. Dedicated dynamic station SQL tables are deliberately not used: runtime DDL creates portability and migration risks across SQLite and PostgreSQL.

Indexes support station/time, result/time, collector heartbeat and tag/time access patterns.
