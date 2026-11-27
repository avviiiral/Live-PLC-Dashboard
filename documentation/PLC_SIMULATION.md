# Middle Testing PLC simulation

Use this configuration only when the physical Siemens PLCs are unavailable. It keeps the same station UUID, PLC UUIDs, 11 tag names, MW addresses, INT types, one-second polling interval, and event detector settings as the real S7 configuration.

The mock adapter generates clearly synthetic integer values. It follows the supplied logger's result sequence independently for each PLC:

1. `MW3112 = 0`: arm the PLC's event capture.
2. `MW3112 = 3`: report an in-progress test; do not create a production event.
3. `MW3112 = 1` or `2`: create exactly one PASS or FAIL event.
4. `MW3112 = 0`: re-arm for the next cycle.

The simulator repeats a ten-second cycle and alternates PASS and FAIL outcomes. Other tag values are illustrative test values, not calibrated measurements and not readings from the real machine.

## Run

Start Django in one terminal:

```powershell
cd D:\IOT
.\.venv\Scripts\Activate.ps1
python backend\manage.py runserver 127.0.0.1:8000
```

Start the collector in another terminal. Set the replacement collector token locally; never commit it or paste it into chat:

```powershell
cd D:\IOT
.\.venv\Scripts\Activate.ps1
$env:COLLECTOR_API_BASE_URL = "http://127.0.0.1:8000"
$env:COLLECTOR_TOKEN = "YOUR_REPLACEMENT_COLLECTOR_TOKEN"
$env:COLLECTOR_CONFIG_PATH = "collector/config/simulation.json"
python -m collector.main
```

The simulation configuration uses the existing PLC database IDs and station assignment. It sends events through the same collector authentication, persistent queue, ingestion endpoint, and database path as real S7 events.

When the physical PLCs are available, switch `COLLECTOR_CONFIG_PATH` back to `collector/config/example.json`. That configuration retains `protocol: s7`; no simulated values are sent in real mode.
