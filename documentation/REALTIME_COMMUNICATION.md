# Real-time Communication
WebSocket endpoint: `/ws/stations/<station-uuid>/`. The current Channels consumer requires an authenticated Django session and publishes accepted production events to that station group.

Important limitation: station-level tenant/membership authorization must be added before this is exposed to multi-tenant users. The configured in-memory channel layer is suitable only for local development. Use Redis in production, configure trusted WebSocket origins, secure cookies and reverse-proxy upgrade headers.
