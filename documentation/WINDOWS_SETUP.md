# Windows PowerShell Setup

## One-time setup
```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend\requirements.txt
python -m pip install -r collector\requirements.txt
Copy-Item .env.example .env
python backend\manage.py migrate
python backend\manage.py createsuperuser
```

Edit the single root `.env`. Use `COLLECTOR_MODE=local` when backend and collector share a machine. Use `COLLECTOR_MODE=lan` on a separate factory PC, with backend LAN URL and that machine's persistent token.

## Start
Terminal 1 — backend:
```powershell
python backend\manage.py runserver 127.0.0.1:8000
```
For remote collectors, configure a LAN-reachable backend binding, firewall and HTTPS. Tokenless local mode must never be exposed on that interface.

Terminal 2 — collector, from repository root:
```powershell
python -m collector.main
```

Terminal 3 — frontend:
```powershell
cd frontend
npm install
npm start
```

Collector discovers current database assignments and refreshes periodically. Docker is not required.
