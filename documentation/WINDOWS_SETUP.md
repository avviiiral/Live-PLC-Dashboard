# Windows PowerShell Setup
Backend:
```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend\requirements.txt
Copy-Item .env.example .env
python backend\manage.py migrate
python backend\manage.py createsuperuser
python backend\manage.py runserver 0.0.0.0:8000
```

Frontend in a second terminal:
```powershell
cd frontend
npm install
npm start
```

Collector from repository root after provisioning/configuration:
```powershell
python -m pip install -r collector\requirements.txt
$env:COLLECTOR_API_BASE_URL = "http://127.0.0.1:8000"
$env:COLLECTOR_TOKEN = "<provisioned-token>"
$env:COLLECTOR_CONFIG_PATH = "collector/config/example.json"
python -m collector.main
```
