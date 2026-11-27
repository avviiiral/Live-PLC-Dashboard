# Live PLC Dashboard

Industrial IoT platform for configurable plant hierarchy, factory-side PLC collection, production-event tracking and manufacturing monitoring.

## Architecture
- Angular frontend for dashboards and production history.
- Django backend for configuration, authentication, event ingestion and WebSocket delivery.
- PLC collector runs beside Django or on a separate factory-LAN PC and discovers assigned PLCs from the database.

## One-time Windows setup
```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend\requirements.txt
python -m pip install -r collector\requirements.txt
Copy-Item .env.example .env
python backend\manage.py migrate
python backend\manage.py createsuperuser
```

Configure only the root `.env`. For same-computer collection set `COLLECTOR_MODE=local` and use `http://127.0.0.1:8000`. For a separate factory PC use `COLLECTOR_MODE=lan`, the backend LAN URL and one persistent `COLLECTOR_TOKEN` for that collector machine.

Start in separate terminals:
```powershell
python backend\manage.py runserver 127.0.0.1:8000
python -m collector.main
```
Angular:
```powershell
cd frontend
npm install
npm start
```

## Database-driven configuration
Create companies, plants, lines, stations, PLC devices and tags in Django. In local mode, run `python backend\\manage.py setup_local_collector --all-active` once to assign all active stations. In LAN mode, assign stations to the remote machine's CollectorAgent. Station/PLC/tag definitions come from the database, not JSON. Collector sync refreshes additions and removals periodically.

Local mode sends no token and is accepted only from loopback. Separate LAN collectors authenticate with one persistent machine identity; adding a station never requires generating another token. Protect `.env`; never commit it. `.env.example` is the safe template.

## Existing Middle Testing reference
Two Siemens S7 devices are documented at `192.168.0.1` and `192.168.0.5`, rack 0/slot 1, with MW marker tags. Confirm physical tag equivalence on both devices and validate PLC networking before live use. The collector is read-only.

## Tests
```powershell
python backend\manage.py test
python -m unittest discover -s collector/tests -v
```
Hardware and LAN acceptance tests must be run at the plant. Docker is not required for development.
