# Collector Setup — single root .env

Station, PLC and tag configuration is stored in Django database records. Do not edit collector JSON files to add equipment.

## Same-computer mode

1. Copy `.env.example` to `.env` in the repository root.
2. Install `backend/requirements.txt` and `collector/requirements.txt`.
3. Set `COLLECTOR_MODE=local` and `COLLECTOR_API_BASE_URL=http://127.0.0.1:8000`.
4. Run migrations and start Django.
5. Create a CollectorAgent named **Local Development Collector** once and assign the stations this machine should poll.
6. Create PLCDevice and PLCTag records. Configure station `event_config` with `trigger_tag`, `active_values`, `rearm_value` and `result_mapping`.
7. Run `python -m collector.main`. It periodically syncs configuration; new/removed PLCs are applied without editing JSON.

Local mode sends no collector token and is accepted only from loopback. Do not expose this mode to LAN clients or a reverse proxy.

## Separate factory-LAN computer

Set `COLLECTOR_MODE=lan`, point `COLLECTOR_API_BASE_URL` at the backend LAN address and set one persistent machine-level `COLLECTOR_TOKEN` in that machine's root `.env`. Provision the remote CollectorAgent once and assign all stations for that machine to it. New stations/PLCs require database assignment only, not new tokens.

Remote LAN collectors must authenticate. Disabling authentication on a factory network would allow other machines to submit forged production events. Protect the `.env` file and rotate credentials only on compromise or decommissioning.

## Queue behavior

Events retain their UUID in the local SQLite queue. An event is removed only after backend acknowledgement. Never delete a queue containing pending events.
